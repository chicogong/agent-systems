"""Deterministic context-selection lesson; no model, network, or tokenizer."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Record:
    id: str
    text: str


HISTORY = (
    Record("r1", "任务约束：本轮只允许生成预览稿；没有用户批准，不得对外发布。"),
    Record("r2", "草稿记录：已写好介绍与目录，下一步核对链接和图片。"),
    Record("r3", "来源记录：每条产品描述都要能回到出处；目前仍有两条待核对。"),
    Record("r4", "排版记录：已统一标题层级，目录能跳转，截图还有一些留白需要调整。"),
    Record("r5", "最近讨论：希望读者先从一条可运行轨迹开始，再逐步学习工具、上下文与恢复；练习不要求付费账号。"),
)
QUESTION = "现在能把这份草稿对外发布吗？"
CRITICAL_ID = "r1"
PROHIBITION = "没有用户批准，不得对外发布"


class BudgetTooSmall(ValueError):
    def __init__(self, required: int, budget: int):
        super().__init__(f"required input needs {required} characters; budget is {budget}")
        self.required = required
        self.budget = budget


def render_record(record: Record) -> str:
    return f"[{record.id}] {record.text}\n"


def retrieve(history: tuple[Record, ...], query: str) -> tuple[str, ...]:
    """Literal substring lookup in the stored source, not semantic retrieval."""
    if not query:
        raise ValueError("retrieval query must not be empty")
    return tuple(record.id for record in history if query in record.text)


def assemble(
    history: tuple[Record, ...],
    question: str,
    budget: int,
    preferred_ids: tuple[str, ...] = (),
) -> dict:
    """Whole-record greedy selection: preferred records, then newest first."""
    required = f"规则：仅根据已选记录判断；缺少发布许可依据时，报告依据不足。\n问题：{question}\n\n已选记录：\n"
    if budget < len(required):
        raise BudgetTooSmall(len(required), budget)
    by_id = {record.id: record for record in history}
    if len(by_id) != len(history):
        raise ValueError("record IDs must be unique")
    if any(record_id not in by_id for record_id in preferred_ids):
        raise ValueError("preferred record does not exist")
    order = list(dict.fromkeys(preferred_ids))
    order.extend(record.id for record in reversed(history) if record.id not in order)
    context = required
    visible_ids = []
    trace = []
    for record_id in order:
        rendered = render_record(by_id[record_id])
        fits = len(context) + len(rendered) <= budget
        trace.append({
            "event": "select_record",
            "id": record_id,
            "characters": len(rendered),
            "remaining_before": budget - len(context),
            "selected": fits,
            "reason": "fits" if fits else "whole_record_does_not_fit",
        })
        if fits:
            context += rendered
            visible_ids.append(record_id)
    return {
        "context": context,
        "used_characters": len(context),
        "required_characters": len(required),
        "visible_ids": visible_ids,
        "events": trace,
    }


def judge_visible(context: str) -> dict:
    """A deliberately tiny rule reader; its only input is this context string."""
    if PROHIBITION in context:
        return {"status": "do_not_publish", "reason": "本轮看见了不得发布的约束。"}
    return {
        "status": "insufficient_evidence",
        "reason": "本轮没有看见发布许可依据；不能据此判定获准。",
    }


def run(mode: str = "recent", budget: int | None = None) -> dict:
    if mode not in {"full", "recent", "retrieve"}:
        raise ValueError("unknown mode")
    if budget is None:
        budget = 1200 if mode == "full" else 220
    query = "用户批准" if mode == "retrieve" else None
    retrieved_ids = retrieve(HISTORY, query) if query else ()
    result = {
        "mode": mode,
        "budget_unit": "Unicode code points counted by Python len(str), not tokens",
        "budget": budget,
        "stored_records": [record.__dict__ for record in HISTORY],
        "retrieval": {"query": query, "matched_ids": list(retrieved_ids)},
    }
    try:
        selection = assemble(HISTORY, QUESTION, budget, retrieved_ids)
    except BudgetTooSmall as error:
        result.update({
            "status": "budget_too_small",
            "required_characters": error.required,
            "visible_ids": [],
            "context": None,
            "answer": None,
            "events": [{"event": "reject_input", "reason": "required_input_does_not_fit"}],
        })
        return result
    result.update(selection)
    result["status"] = "assembled"
    # No HISTORY, trace, retrieved IDs or audit information is passed to the reader.
    result["answer"] = judge_visible(selection["context"])
    # The audit is a separate teacher's view, computed after the answer.
    stored_answer = judge_visible("".join(render_record(record) for record in HISTORY))
    result["audit"] = {
        "critical_record_stored": any(record.id == CRITICAL_ID for record in HISTORY),
        "critical_record_visible": CRITICAL_ID in selection["visible_ids"],
        "stored_constraint": stored_answer["status"],
        "answer_recovered_constraint": (
            result["answer"]["status"] == stored_answer["status"] == "do_not_publish"
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("full", "recent", "retrieve"), default="recent")
    parser.add_argument("--budget", type=int, help="total input characters, including rules and question")
    args = parser.parse_args()
    result = run(args.mode, args.budget)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["status"] == "budget_too_small" else 0


if __name__ == "__main__":
    raise SystemExit(main())
