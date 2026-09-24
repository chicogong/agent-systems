"""A deterministic side-effect reconciliation lab; no network or real writes."""

from __future__ import annotations

import argparse
import json


class FakeService:
    def __init__(self, *, supports_lookup: bool = True) -> None:
        self.supports_lookup = supports_lookup
        self.operations: dict[str, str] = {}
        self.effects: list[str] = []

    def submit(self, operation_id: str, payload: str, *, lose_receipt: bool = False) -> str | None:
        # Only this fake service guarantees deduplication by operation ID.
        if operation_id not in self.operations:
            self.operations[operation_id] = payload
            self.effects.append(payload)
        return None if lose_receipt else "accepted"

    def lookup(self, operation_id: str) -> str | None:
        if not self.supports_lookup:
            raise NotImplementedError("the target offers no status lookup")
        return "accepted" if operation_id in self.operations else None


def run(mode: str) -> dict:
    if mode not in {"normal", "lost_receipt", "no_lookup", "unsafe_new_id"}:
        raise ValueError(mode)
    service = FakeService(supports_lookup=mode != "no_lookup")
    operation_id = "task-42:publish-v1"
    events: list[dict] = []
    receipt = service.submit(operation_id, "publish-v1", lose_receipt=mode != "normal")
    events.append({"event": "submit", "operation_id": operation_id, "receipt": receipt})

    if receipt == "accepted":
        status = "confirmed"
    elif mode == "no_lookup":
        # An unavailable lookup is not evidence that the request failed.
        events.append({"event": "lookup", "result": "unavailable"})
        status = "unknown_stop"
    else:
        result = service.lookup(operation_id)
        events.append({"event": "lookup", "operation_id": operation_id, "result": result})
        if mode == "unsafe_new_id":
            # This deliberately shows a bug: a *new* ID is a second operation.
            second_id = "task-42:publish-v1-retry"
            second = service.submit(second_id, "publish-v1")
            events.append({"event": "unsafe_retry", "operation_id": second_id, "receipt": second})
            status = "duplicate_effect"
        else:
            status = "confirmed_by_lookup" if result == "accepted" else "unknown_stop"

    return {"status": status, "effects": len(service.effects), "events": events}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("normal", "lost_receipt", "no_lookup", "unsafe_new_id"), default="normal")
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.mode), ensure_ascii=False, indent=2))
