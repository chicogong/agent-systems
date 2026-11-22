"""Deterministic prefix caching mechanics lesson; demonstrates cache hit vs bust.

Run with:
  python3 examples/prefix-cache/demo.py --mode layered_hit
  python3 examples/prefix-cache/demo.py --mode dynamic_timestamp
  python3 examples/prefix-cache/demo.py --mode shuffled_tools
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class StepObservation:
    tool: str
    tokens: int
    summary: str


STEPS = (
    StepObservation("read_file", 300, "读取 auth.py 源码与测试配置"),
    StepObservation("write_file", 300, "修复超时退避重试逻辑并保存"),
    StepObservation("run_test", 300, "执行单元测试 pytest tests/test_auth.py"),
    StepObservation("finish", 400, "生成修改摘要并确认验收条件全部达成"),
)

BASE_SYSTEM_TOKENS = 6000
BASE_TOOLS_TOKENS = 800
BASE_USER_TOKENS = 200
WARM_SYSTEM_CACHE = BASE_SYSTEM_TOKENS + BASE_TOOLS_TOKENS  # 6800 tokens


def run(mode: str) -> dict:
    if mode not in {"layered_hit", "dynamic_timestamp", "shuffled_tools"}:
        raise ValueError(f"Unknown mode: {mode}")

    step_records = []
    cumulative_input = 0
    cumulative_cached = 0
    cumulative_uncached = 0

    # Turn 1: initial prompt assembly
    t1_input = BASE_SYSTEM_TOKENS + BASE_TOOLS_TOKENS + BASE_USER_TOKENS  # 7000
    if mode == "layered_hit":
        t1_cached = WARM_SYSTEM_CACHE  # 6800 warm cache anchor
        t1_uncached = BASE_USER_TOKENS  # 200
        ttft = 120
    else:
        t1_cached = 0
        t1_uncached = t1_input
        ttft = 680

    cumulative_input += t1_input
    cumulative_cached += t1_cached
    cumulative_uncached += t1_uncached

    step_records.append({
        "turn": 1,
        "action": "initial_prompt",
        "input_tokens": t1_input,
        "cache_read_tokens": t1_cached,
        "uncached_tokens": t1_uncached,
        "turn_hit_rate": f"{(t1_cached / t1_input) * 100:.1f}%",
        "ttft_ms": ttft,
        "prefix_status": "anchor_hit" if mode == "layered_hit" else "unanchored_miss",
    })

    current_context_tokens = t1_input

    for i, obs in enumerate(STEPS, start=2):
        prev_context_tokens = current_context_tokens
        current_context_tokens += obs.tokens
        cumulative_input += current_context_tokens

        if mode == "layered_hit":
            # Strict prefix matching: the entire previous context is 100% matched
            cached = prev_context_tokens
            uncached = obs.tokens
            ttft = 95
        elif mode == "dynamic_timestamp":
            # Dynamic timestamp in system prompt line 1 breaks prefix at token 4
            # 0% cache hit; all tokens must be recomputed
            cached = 0
            uncached = current_context_tokens
            ttft = 680 + (i * 45)
        else:  # shuffled_tools
            # Tools order scrambled between system prompt and messages
            # Only system prompt prefix matches (6000 tokens)
            cached = BASE_SYSTEM_TOKENS
            uncached = current_context_tokens - BASE_SYSTEM_TOKENS
            ttft = 350 + (i * 30)

        cumulative_cached += cached
        cumulative_uncached += uncached

        step_records.append({
            "turn": i,
            "action": obs.tool,
            "input_tokens": current_context_tokens,
            "cache_read_tokens": cached,
            "uncached_tokens": uncached,
            "turn_hit_rate": f"{(cached / current_context_tokens) * 100:.1f}%",
            "ttft_ms": ttft,
            "prefix_status": (
                "prefix_hit" if mode == "layered_hit"
                else "cache_bust_timestamp" if mode == "dynamic_timestamp"
                else "partial_miss_tools_diverged"
            ),
        })

    overall_hit_rate = (cumulative_cached / cumulative_input) * 100

    if mode == "layered_hit":
        status = "high_cache_hit"
        summary = f"严格分层与纯追加实现 {overall_hit_rate:.1f}% 缓存命中，计算账单节省 86.5%。"
    elif mode == "dynamic_timestamp":
        status = "cache_bust_timestamp"
        summary = "系统提示塞入动态秒级时间戳导致 0% 命中，步步全额重算输入。"
    else:
        status = "cache_bust_shuffled"
        summary = f"工具定义乱序注入导致下游历史前缀失配，综合命中率跌至 {overall_hit_rate:.1f}%。"

    return {
        "mode": mode,
        "status": status,
        "summary": summary,
        "total_turns": len(step_records),
        "ledger": {
            "total_input_tokens": cumulative_input,
            "cumulative_cached_tokens": cumulative_cached,
            "cumulative_uncached_tokens": cumulative_uncached,
            "overall_hit_rate": f"{overall_hit_rate:.2f}%",
            "effective_discount": "86.5%" if mode == "layered_hit" else "0.0%",
        },
        "turns": step_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("layered_hit", "dynamic_timestamp", "shuffled_tools"),
        default="layered_hit",
        help="Experiment mode to execute",
    )
    args = parser.parse_args()
    result = run(args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
