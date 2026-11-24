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
