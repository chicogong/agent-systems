"""Production-Grade Agent Harness Starter (Zero External Dependencies).

This module brings together the core architectural principles from "Illustrated Agent Systems":
1. 5-Layer Prefix Caching Layout (Global Static -> Tools -> Session AGENTS.md -> Append-Only Turns -> Transient Tail).
2. Host Approval Gate (Distinguishing model proposal from host-controlled execution).
3. Anti Context-Rot Truncation (Head-tail preservation for tool outputs).
4. Watermark Compaction (Checkpointing long histories to keep signal density high).
5. Deterministic Token Usage & Cache Hit Accounting.

Pure Python 3.10+ standard library. Copy and adapt freely for production agents.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ToolRiskLevel(str, Enum):
    READ_ONLY = "read_only"
    MUTATION = "mutation"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    risk_level: ToolRiskLevel = ToolRiskLevel.READ_ONLY

    def to_schema_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "risk_level": self.risk_level.value,
        }


def truncate_tool_output(
    text: str,
    max_lines: int = 40,
    head_lines: int = 15,
    tail_lines: int = 15,
) -> str:
    """Truncate verbose command outputs at the source to prevent Context Rot.

    Preserves head context (command launch/init) and tail context (stack trace/error)
    while dropping intermediate noise.
    """
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    dropped = len(lines) - head_lines - tail_lines
    if dropped <= 0:
        return text
    kept_head = lines[:head_lines]
    kept_tail = lines[-tail_lines:]
    marker = f"[... {dropped} lines truncated by Host Guard to prevent Context Rot ...]"
    return "\n".join(kept_head + [marker] + kept_tail)


@dataclass
class Turn:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None


class ContextAssembler:
    """Assembles prompts strictly ordered by decreasing stability to maximize KV Cache hits.

    Layer 1: Global Invariable (Role instructions + strictly sorted tool schemas)
    Layer 2: Session Constant (AGENTS.md guidelines + pinned read-only memory)
    Layer 3: Milestone Summary (Compacted summaries from watermark evictions)
    Layer 4: Append-Only Turns (Historical interactions, never mutated)
    Layer 5: Transient Tail (Step budget, current checklist, step-specific alert)
    """

    def __init__(
        self,
        system_role: str,
        tools: list[ToolDefinition],
        session_rules: str = "",
    ):
        self.system_role = system_role.strip()
        # Strictly sort tool schemas by name to prevent key-order cache busting
        self.sorted_tools = sorted(tools, key=lambda t: t.name)
        self.session_rules = session_rules.strip()
        self.milestone_summary: str = ""
        self.history: list[Turn] = []

    @property
    def static_prefix(self) -> str:
        """The completely stable prefix across all turns."""
        tools_json = json.dumps(
            [t.to_schema_dict() for t in self.sorted_tools],
            sort_keys=True,
            ensure_ascii=False,
            indent=None,
        )
        parts = [
            f"<system_role>\n{self.system_role}\n</system_role>",
            f"<available_tools>\n{tools_json}\n</available_tools>",
        ]
        if self.session_rules:
            parts.append(f"<session_rules>\n{self.session_rules}\n</session_rules>")
        return "\n\n".join(parts)

    def assemble_prompt(self, transient_tail: str = "") -> str:
        """Build the full prompt adhering to the 5-layer hierarchy."""
        sections = [self.static_prefix]

        if self.milestone_summary:
            sections.append(
                f"<milestone_checkpoint>\n{self.milestone_summary}\n</milestone_checkpoint>"
            )

        if self.history:
            for idx, turn in enumerate(self.history, start=1):
                block = f"<turn_{idx} role=\"{turn.role}\">\n{turn.content}"
                if turn.tool_calls:
                    calls_str = json.dumps(turn.tool_calls, sort_keys=True, ensure_ascii=False)
                    block += f"\nToolCalls: {calls_str}"
                block += f"\n</turn_{idx}>"
                sections.append(block)

        if transient_tail.strip():
            sections.append(f"<transient_step_state>\n{transient_tail.strip()}\n</transient_step_state>")

        return "\n\n".join(sections)

    def append_turn(self, turn: Turn) -> None:
        self.history.append(turn)

    def check_and_compact(
        self,
        watermark_turns: int = 10,
        retain_recent: int = 4,
    ) -> bool:
        """Trigger compaction when history exceeds watermark threshold."""
        if len(self.history) <= watermark_turns:
            return False

        # Evict older turns and condense into summary
        evicted = self.history[:-retain_recent]
        self.history = self.history[-retain_recent:]

        summary_points = [
            f"- Summarized {len(evicted)} historical turns (Turns 1..{len(evicted)}) to prevent Context Rot."
        ]
        for t in evicted:
            if t.role == "user":
                summary_points.append(f"  * User goal: {t.content[:80]}")
            elif t.tool_calls:
                tool_names = [call.get("name", "") for call in t.tool_calls]
                summary_points.append(f"  * Performed actions: {', '.join(tool_names)}")

        self.milestone_summary = (
            (self.milestone_summary + "\n" if self.milestone_summary else "")
            + "\n".join(summary_points)
        )
        return True


class HostApprovalGate:
    """Safeguards mutation and destructive tools with explicit host verification."""

    def __init__(
        self,
        auto_approve_readonly: bool = True,
        approval_hook: Callable[[str, dict[str, Any]], bool] | None = None,
    ):
        self.auto_approve_readonly = auto_approve_readonly
        self.approval_hook = approval_hook or (lambda tool, args: True)

    def evaluate(self, tool_def: ToolDefinition, args: dict[str, Any]) -> tuple[bool, str]:
        if tool_def.risk_level == ToolRiskLevel.READ_ONLY and self.auto_approve_readonly:
            return True, "Auto-approved read-only tool"
        granted = self.approval_hook(tool_def.name, args)
        if granted:
            return True, f"Host approval granted for {tool_def.risk_level.value} tool"
        return False, f"Host approval DENIED for {tool_def.risk_level.value} tool"


class MockInferenceEngine:
    """Emulates a modern LLM inference backend with KV Prefix Caching accounting."""

    def __init__(self):
        self.last_prompt: str = ""
        self.cumulative_input_tokens: int = 0
        self.cumulative_cached_tokens: int = 0
        self.cumulative_uncached_tokens: int = 0

    def estimate_tokens(self, text: str) -> int:
        # Standard benchmark rule: ~4 chars per token for structured code/markdown
        return max(1, len(text) // 4)

    def calculate_prefix_match(self, new_prompt: str) -> int:
        if not self.last_prompt:
            return 0
        # Match common prefix character-by-character
        common_len = 0
        min_len = min(len(self.last_prompt), len(new_prompt))
        for i in range(min_len):
            if self.last_prompt[i] == new_prompt[i]:
                common_len += 1
            else:
                break
        return self.estimate_tokens(new_prompt[:common_len])

    def query(self, prompt: str) -> dict[str, Any]:
        total_tokens = self.estimate_tokens(prompt)
        cached_tokens = self.calculate_prefix_match(prompt)
        uncached_tokens = max(0, total_tokens - cached_tokens)

        self.last_prompt = prompt
        self.cumulative_input_tokens += total_tokens
        self.cumulative_cached_tokens += cached_tokens
        self.cumulative_uncached_tokens += uncached_tokens

        hit_rate = (cached_tokens / total_tokens * 100) if total_tokens > 0 else 0.0

        return {
            "total_tokens": total_tokens,
            "cached_tokens": cached_tokens,
            "uncached_tokens": uncached_tokens,
            "hit_rate_percent": round(hit_rate, 2),
        }


class LLMClientError(Exception):
    """Base exception for LiveLLMClient errors."""


class LLMAPIError(LLMClientError):
    """Raised when the LLM API returns an HTTP error code or API error payload."""

    def __init__(self, message: str, status_code: int | None = None, body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class LLMNetworkError(LLMClientError):
    """Raised for network-level failures (connection dropped, DNS failure, timeout)."""


class LLMResponseError(LLMClientError):
    """Raised when LLM response is malformed JSON or lacks required fields."""


class LiveLLMClient:
    """Zero-external-dependency live LLM caller using urllib.request.

    Compatible with OpenAI, DeepSeek, and Gemini-compatible chat completions APIs.
    Auto-detects API key and settings from environment variables:
    - API Key: OPENAI_API_KEY, DEEPSEEK_API_KEY, GEMINI_API_KEY, or LLM_API_KEY
    - Base URL: OPENAI_BASE_URL, DEEPSEEK_BASE_URL, GEMINI_BASE_URL, or LLM_BASE_URL (defaults to https://api.openai.com/v1)
    - Model: OPENAI_MODEL, DEEPSEEK_MODEL, GEMINI_MODEL, or LLM_MODEL (defaults to gpt-4o-mini)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        temperature: float = 0.0,
        extra_headers: dict[str, str] | None = None,
    ):
        self.api_key = (
            api_key
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("LLM_API_KEY")
            or ""
        )
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or os.environ.get("GEMINI_BASE_URL")
            or os.environ.get("LLM_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = (
            model
            or os.environ.get("OPENAI_MODEL")
            or os.environ.get("DEEPSEEK_MODEL")
            or os.environ.get("GEMINI_MODEL")
            or os.environ.get("LLM_MODEL")
            or "gpt-4o-mini"
        )
        self.timeout = float(timeout)
        self.temperature = float(temperature)
        self.extra_headers = extra_headers or {}

        # Token and cache accounting state (cumulative across calls)
        self.cumulative_input_tokens: int = 0
        self.cumulative_cached_tokens: int = 0
        self.cumulative_uncached_tokens: int = 0
        self.cumulative_completion_tokens: int = 0

    @property
    def endpoint_url(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return f"{self.base_url}/chat/completions"

    def format_messages(
        self,
        prompt_or_messages: str | list[dict[str, Any]] | list[Turn],
    ) -> list[dict[str, Any]]:
        """Normalize string, Turn objects, or message dicts into OpenAI chat messages."""
        if isinstance(prompt_or_messages, str):
            return [{"role": "user", "content": prompt_or_messages}]

        formatted: list[dict[str, Any]] = []
        for item in prompt_or_messages:
            if isinstance(item, Turn):
                msg: dict[str, Any] = {"role": item.role, "content": item.content}
                if item.name:
                    msg["name"] = item.name
                if item.tool_call_id:
                    msg["tool_call_id"] = item.tool_call_id
                if item.tool_calls:
                    msg["tool_calls"] = item.tool_calls
                formatted.append(msg)
            elif isinstance(item, dict):
                formatted.append(item)
            else:
                raise TypeError(f"Unsupported message item type: {type(item)}")
        return formatted

    def build_request(
        self,
        messages: str | list[dict[str, Any]] | list[Turn],
        json_mode: bool = False,
        model: str | None = None,
        temperature: float | None = None,
        extra_payload: dict[str, Any] | None = None,
    ) -> urllib.request.Request:
        """Build urllib.request.Request with JSON payload and authorization headers."""
        if not self.api_key:
            raise ValueError(
                "API key is required for live LLM requests. Set OPENAI_API_KEY, DEEPSEEK_API_KEY, "
                "GEMINI_API_KEY, or LLM_API_KEY environment variable, or pass api_key to LiveLLMClient."
            )

        formatted_messages = self.format_messages(messages)
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": formatted_messages,
            "temperature": self.temperature if temperature is None else temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        if extra_payload:
            payload.update(extra_payload)

        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.extra_headers:
            headers.update(self.extra_headers)

        return urllib.request.Request(
            url=self.endpoint_url,
            data=body_bytes,
            headers=headers,
            method="POST",
        )

    def parse_response(self, response_data: bytes | str | dict[str, Any]) -> dict[str, Any]:
        """Parse raw response from chat completions API and extract usage & cache stats."""
        if isinstance(response_data, bytes):
            try:
                raw_text = response_data.decode("utf-8")
            except UnicodeDecodeError as e:
                raise LLMResponseError(f"Failed to decode API response bytes as UTF-8: {e}") from e
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError as e:
                raise LLMResponseError(f"Failed to parse LLM API response as JSON: {e}") from e
        elif isinstance(response_data, str):
            try:
                parsed = json.loads(response_data)
            except json.JSONDecodeError as e:
                raise LLMResponseError(f"Failed to parse LLM API response as JSON: {e}") from e
        elif isinstance(response_data, dict):
            parsed = response_data
        else:
            raise TypeError(f"Expected bytes, str, or dict for response_data, got {type(response_data)}")

        if not isinstance(parsed, dict):
            raise LLMResponseError("LLM response is not a valid JSON object")

        if "error" in parsed and isinstance(parsed["error"], dict):
            err_msg = parsed["error"].get("message", "Unknown error")
            err_type = parsed["error"].get("type", "api_error")
            raise LLMAPIError(f"API returned error ({err_type}): {err_msg}", body=json.dumps(parsed))

        choices = parsed.get("choices")
        if not choices or not isinstance(choices, list):
            raise LLMResponseError("LLM response missing 'choices' list")

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content") or ""
        role = message.get("role", "assistant")
        tool_calls = message.get("tool_calls", [])
        finish_reason = first_choice.get("finish_reason")

        usage_raw = parsed.get("usage") or {}
        prompt_tokens = usage_raw.get("prompt_tokens", 0)
        completion_tokens = usage_raw.get("completion_tokens", 0)
        total_tokens = usage_raw.get("total_tokens", prompt_tokens + completion_tokens)

        # Support OpenAI prompt_tokens_details.cached_tokens and DeepSeek prompt_cache_hit_tokens
        cached_tokens = 0
        prompt_tokens_details = usage_raw.get("prompt_tokens_details")
        if isinstance(prompt_tokens_details, dict):
            cached_tokens = prompt_tokens_details.get("cached_tokens", 0)
        elif "prompt_cache_hit_tokens" in usage_raw:
            cached_tokens = usage_raw.get("prompt_cache_hit_tokens", 0)

        uncached_tokens = max(0, prompt_tokens - cached_tokens)
        hit_rate = (cached_tokens / prompt_tokens * 100) if prompt_tokens > 0 else 0.0

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cached_tokens": cached_tokens,
            "uncached_tokens": uncached_tokens,
            "hit_rate_percent": round(hit_rate, 2),
        }

        # Update cumulative metrics
        self.cumulative_input_tokens += prompt_tokens
        self.cumulative_cached_tokens += cached_tokens
        self.cumulative_uncached_tokens += uncached_tokens
        self.cumulative_completion_tokens += completion_tokens

        return {
            "content": content,
            "role": role,
            "tool_calls": tool_calls,
            "finish_reason": finish_reason,
            "usage": usage,
            "total_tokens": total_tokens,
            "cached_tokens": cached_tokens,
            "uncached_tokens": uncached_tokens,
            "hit_rate_percent": round(hit_rate, 2),
            "model": parsed.get("model", self.model),
            "raw": parsed,
        }

    def send_request(self, req: urllib.request.Request) -> dict[str, Any]:
        """Execute HTTP request with error translation and timeouts."""
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = resp.read()
                return self.parse_response(data)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise LLMAPIError(
                f"LLM API HTTP {e.code}: {body or e.reason}",
                status_code=e.code,
                body=body,
            ) from e
        except urllib.error.URLError as e:
            raise LLMNetworkError(f"LLM API network error: {e.reason}") from e
        except TimeoutError as e:
            raise LLMNetworkError(f"LLM API request timed out after {self.timeout}s") from e

    def complete(
        self,
        messages: str | list[dict[str, Any]] | list[Turn],
        json_mode: bool = False,
        model: str | None = None,
        temperature: float | None = None,
        extra_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """End-to-end request builder, execution, and response parsing."""
        req = self.build_request(
            messages=messages,
            json_mode=json_mode,
            model=model,
            temperature=temperature,
            extra_payload=extra_payload,
        )
        return self.send_request(req)

    def query(self, prompt: str, json_mode: bool = False) -> dict[str, Any]:
        """Drop-in compatible interface with MockInferenceEngine.query(prompt)."""
        return self.complete(prompt, json_mode=json_mode)
