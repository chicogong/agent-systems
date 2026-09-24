"""A deterministic teaching harness, not a model-backed Agent.

Run with: python3 examples/first-agent-loop/demo.py --mode normal
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory


def propose(observations: list[dict], mode: str) -> dict:
    """Stand in for a model; decide only after seeing the previous result."""
    if not observations:
        return {"tool": "read"}
    last = observations[-1]
    if not last["ok"]:
        return {"tool": "stop"}
    if last["tool"] == "read":
        return {"tool": "write", "timeout": 5, "retries": 0 if mode == "regression" else 3}
    if last["tool"] == "write":
        return {"tool": "check"}
    return {"tool": "finish"}


def execute(action: dict, config_path: Path) -> dict:
    tool = action["tool"]
    state = json.loads(config_path.read_text(encoding="utf-8"))
    if tool == "read":
        return {"tool": tool, "ok": True, "detail": state}
    if tool == "write":
        state.update(timeout=action["timeout"], retries=action["retries"])
        config_path.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
        return {"tool": tool, "ok": True, "detail": state}
    if tool == "check":
        passed = state == {"timeout": 5, "retries": 3}
        return {"tool": tool, "ok": passed, "detail": "both requirements pass" if passed else "retry rule changed"}
    raise ValueError(f"Unknown tool: {tool}")


def run(mode: str) -> dict:
    if mode not in {"normal", "denied", "regression"}:
        raise ValueError(mode)
    events: list[dict] = []
    observations: list[dict] = []
    status = "budget_exhausted"
    with TemporaryDirectory(prefix="agent-loop-lab-") as directory:
        config_path = Path(directory) / "config.json"
        config_path.write_text('{"timeout": 30, "retries": 3}', encoding="utf-8")
        for _ in range(5):
            action = propose(observations, mode)
            events.append({"event": "proposal", "tool": action["tool"], "seen_results": len(observations)})
            if action["tool"] == "finish":
                # A model stopping is not acceptance. The host checks its own gate.
                state = json.loads(config_path.read_text(encoding="utf-8"))
                status = "candidate_ready" if state == {"timeout": 5, "retries": 3} else "blocked"
                break
            if action["tool"] == "stop":
                status = "blocked"
                break
            if action["tool"] == "write":
                granted = mode != "denied"
                events.append({"event": "approval", "granted": granted})
                if not granted:
                    observation = {"tool": "write", "ok": False, "detail": "write denied before execution"}
                    observations.append(observation)
                    events.append({"event": "tool_result", **observation})
                    continue
            observation = execute(action, config_path)
            observations.append(observation)
            events.append({"event": "tool_result", **observation})
        state = json.loads(config_path.read_text(encoding="utf-8"))
    return {"status": status, "config": state, "events": events}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("normal", "denied", "regression"), default="normal")
    args = parser.parse_args()
    print(json.dumps(run(args.mode), ensure_ascii=False, indent=2))
