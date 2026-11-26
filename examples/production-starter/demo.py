"""Self-contained runnable demo of the production agent starter harness.

Demonstrates:
1. 5-Layer Prompt Assembly with stable prefix preservation.
2. Tool proposal vs host approval gate.
3. Anti-Context-Rot output truncation (100-line test output trimmed).
4. Live KV Cache hit rate accounting across turns.
5. Zero-dependency live LLM caller support (--live flag).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_starter import (
    ContextAssembler,
    HostApprovalGate,
    LiveLLMClient,
    MockInferenceEngine,
    ToolDefinition,
    ToolRiskLevel,
    Turn,
    truncate_tool_output,
)


def run_demo(
    verbose: bool = True,
    live: bool = False,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    json_mode: bool = False,
) -> dict[str, Any]:
    # 1. Define tools
    tools = [
        ToolDefinition(
            name="read_file",
            description="Read content of a target file path",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
            risk_level=ToolRiskLevel.READ_ONLY,
        ),
        ToolDefinition(
            name="write_file",
            description="Overwrite target file with new content",
            parameters={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
            risk_level=ToolRiskLevel.MUTATION,
        ),
        ToolDefinition(
            name="run_bash",
            description="Run an arbitrary shell command inside container",
            parameters={"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]},
            risk_level=ToolRiskLevel.DESTRUCTIVE,
        ),
    ]

    # 2. Host configuration & approval policy
    system_role = (
        "You are an autonomous engineering agent following strict verification guidelines. "
        "Always inspect facts before modifying state. Propose minimal diffs."
    )
    session_rules = (
        "# AGENTS.md Repository Rules\n"
        "- Do not modify production config without tests.\n"
        "- Run pytest after all edits."
    )

    # Host approval callback: approve write_file only if writing to test/config
    def host_approval(tool_name: str, args: dict[str, Any]) -> bool:
        if tool_name == "write_file":
            return args.get("path", "").endswith(".json")
        return False

    gate = HostApprovalGate(auto_approve_readonly=True, approval_hook=host_approval)
    assembler = ContextAssembler(system_role, tools, session_rules)

    if live:
        engine = LiveLLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        if not engine.api_key:
            raise ValueError(
                "Live mode requires an API key. Set OPENAI_API_KEY, DEEPSEEK_API_KEY, "
                "GEMINI_API_KEY, or LLM_API_KEY in your environment, or pass --api-key <KEY>."
            )
    else:
        engine = MockInferenceEngine()

    if verbose:
        print("=" * 70)
        mode_label = f"LIVE ({engine.model} @ {engine.base_url})" if live else "MOCK INFERENCE"
        print(f"  Illustrated Agent Systems - Production Starter Harness Demo")
        print(f"  Mode: {mode_label}")
        print("=" * 70)

    # Turn 1: User Request
    turn1_user = Turn(role="user", content="Fix config.json: change timeout from 30 to 5.")
    assembler.append_turn(turn1_user)
    prompt1 = assembler.assemble_prompt(transient_tail="[Step 1/5] Pending initial inspection.")
    usage1 = engine.query(prompt1, json_mode=json_mode) if live else engine.query(prompt1)
    if verbose:
        print(f"\n[Turn 1] Input Tokens: {usage1['total_tokens']} | Cache Read: {usage1['cached_tokens']} | Hit Rate: {usage1['hit_rate_percent']}%")
        if live and usage1.get("content"):
            preview = usage1["content"].strip().replace("\n", " ")[:90]
            print(f"         Live Model Output: {preview}...")

    # Turn 2: Agent proposes read_file
    turn2_call = Turn(
        role="assistant",
        content="I will inspect config.json first.",
        tool_calls=[{"name": "read_file", "args": {"path": "config.json"}}],
    )
    assembler.append_turn(turn2_call)

    # Tool execution
    read_tool = next(t for t in tools if t.name == "read_file")
    allowed, reason = gate.evaluate(read_tool, {"path": "config.json"})
    assert allowed

    raw_output = json.dumps({"timeout": 30, "retries": 3, "service": "payment"})
    turn2_result = Turn(role="tool", content=raw_output, name="read_file")
    assembler.append_turn(turn2_result)

    prompt2 = assembler.assemble_prompt(transient_tail="[Step 2/5] Inspection complete. Preparing fix.")
    usage2 = engine.query(prompt2, json_mode=json_mode) if live else engine.query(prompt2)
    if verbose:
        print(f"[Turn 2] Input Tokens: {usage2['total_tokens']} | Cache Read: {usage2['cached_tokens']} | Hit Rate: {usage2['hit_rate_percent']}%")
        if live and usage2.get("content"):
            preview = usage2["content"].strip().replace("\n", " ")[:90]
            print(f"         Live Model Output: {preview}...")

    # Turn 3: Agent runs bash tests (returns 80 lines of verbose test logs -> Truncated by Host)
    turn3_call = Turn(
        role="assistant",
        content="Running baseline test suite before applying change.",
        tool_calls=[{"name": "run_bash", "args": {"cmd": "pytest -v"}}],
    )
    assembler.append_turn(turn3_call)

    verbose_raw_log = "\n".join([f"test_case_{i:03d} PASSED [1ms]" for i in range(1, 80)]) + "\nFAILED test_timeout: expected 5 got 30"
    truncated_log = truncate_tool_output(verbose_raw_log, max_lines=30, head_lines=10, tail_lines=10)
    turn3_result = Turn(role="tool", content=truncated_log, name="run_bash")
    assembler.append_turn(turn3_result)

    prompt3 = assembler.assemble_prompt(transient_tail="[Step 3/5] Test failure confirmed. Applying edit.")
    usage3 = engine.query(prompt3, json_mode=json_mode) if live else engine.query(prompt3)
    if verbose:
        print(f"[Turn 3] Input Tokens: {usage3['total_tokens']} | Cache Read: {usage3['cached_tokens']} | Hit Rate: {usage3['hit_rate_percent']}%")
        print(f"         (Tool output truncated from 81 lines to {len(truncated_log.splitlines())} lines to prevent Context Rot)")
        if live and usage3.get("content"):
            preview = usage3["content"].strip().replace("\n", " ")[:90]
            print(f"         Live Model Output: {preview}...")

    # Turn 4: Agent proposes write_file (Mutation -> Gate check)
    turn4_call = Turn(
        role="assistant",
        content="Writing updated configuration with timeout=5.",
        tool_calls=[{"name": "write_file", "args": {"path": "config.json", "content": '{"timeout": 5, "retries": 3}'}}],
    )
    assembler.append_turn(turn4_call)

    write_tool = next(t for t in tools if t.name == "write_file")
    allowed, reason = gate.evaluate(write_tool, {"path": "config.json", "content": '{"timeout": 5}'})
    turn4_result = Turn(
        role="tool",
        content=f'{{"status": "ok", "bytes_written": 32, "gate_verdict": "{reason}"}}',
        name="write_file",
    )
    assembler.append_turn(turn4_result)

    prompt4 = assembler.assemble_prompt(transient_tail="[Step 4/5] Edit landed. Finishing task.")
    usage4 = engine.query(prompt4, json_mode=json_mode) if live else engine.query(prompt4)
    if verbose:
        print(f"[Turn 4] Input Tokens: {usage4['total_tokens']} | Cache Read: {usage4['cached_tokens']} | Hit Rate: {usage4['hit_rate_percent']}%")
        if live and usage4.get("content"):
            preview = usage4["content"].strip().replace("\n", " ")[:90]
            print(f"         Live Model Output: {preview}...")

    # Turn 5: Finish
    turn5_call = Turn(role="assistant", content="Successfully updated timeout to 5 and validated requirements.")
    assembler.append_turn(turn5_call)
    prompt5 = assembler.assemble_prompt(transient_tail="[Step 5/5] Task Completed.")
    usage5 = engine.query(prompt5, json_mode=json_mode) if live else engine.query(prompt5)
    if verbose:
        print(f"[Turn 5] Input Tokens: {usage5['total_tokens']} | Cache Read: {usage5['cached_tokens']} | Hit Rate: {usage5['hit_rate_percent']}%")
        if live and usage5.get("content"):
            preview = usage5["content"].strip().replace("\n", " ")[:90]
            print(f"         Live Model Output: {preview}...")

    overall_hit_rate = (
        (engine.cumulative_cached_tokens / engine.cumulative_input_tokens) * 100
        if engine.cumulative_input_tokens > 0
        else 0.0
    )

    summary = {
        "total_turns": 5,
        "cumulative_input_tokens": engine.cumulative_input_tokens,
        "cumulative_cached_tokens": engine.cumulative_cached_tokens,
        "cumulative_uncached_tokens": engine.cumulative_uncached_tokens,
        "overall_hit_rate_percent": round(overall_hit_rate, 2),
        "host_approval_passed": allowed,
        "final_status": "candidate_ready",
        "live": live,
    }

    if verbose:
        print("-" * 70)
        print(f"Overall Statistics:")
        print(f"  Cumulative Input Tokens:   {summary['cumulative_input_tokens']}")
        print(f"  Cumulative Cached Tokens:  {summary['cumulative_cached_tokens']}")
        print(f"  Cumulative Uncached Tokens:{summary['cumulative_uncached_tokens']}")
        print(f"  Overall Cache Hit Rate:    {summary['overall_hit_rate_percent']}%")
        print(f"  Final Gate Verdict:        {summary['final_status']}")
        print("=" * 70)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Illustrated Agent Systems - Production Starter Harness Demo")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute against a live LLM chat completions endpoint (default: mock mode).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model identifier (e.g. gpt-4o-mini, deepseek-chat, gemini-1.5-flash).",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base API URL (e.g. https://api.openai.com/v1, https://api.deepseek.com).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API Key (default: loaded from OPENAI_API_KEY / DEEPSEEK_API_KEY / GEMINI_API_KEY).",
    )
    parser.add_argument(
        "--json-mode",
        action="store_true",
        help="Request JSON mode (response_format={'type': 'json_object'}).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress terminal log output.",
    )
    cli_args = parser.parse_args()

    try:
        run_demo(
            verbose=not cli_args.quiet,
            live=cli_args.live,
            model=cli_args.model,
            api_key=cli_args.api_key,
            base_url=cli_args.base_url,
            json_mode=cli_args.json_mode,
        )
    except ValueError as err:
        sys.exit(f"Error: {err}")
