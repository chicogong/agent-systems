"""Loopback HTTP fault lab, not a production server or a model-driven Agent.

Real sockets/read timeouts; in-memory synthetic records and controlled fault
gates. No internet, authentication, file writes, or real deployment side effects.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import socket
import threading
from urllib.parse import quote, unquote

MODES = ("normal", "timeout_then_lookup", "same_id_retry", "lookup_lag",
         "late_commit", "unsafe_new_id", "payload_conflict")
OPERATION_ID = "task-42:publish-v1"
PAYLOAD = "publish-v1"
READ_TIMEOUT = 0.15
FIXTURE_LIMIT = 5.0


class Ledger:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.lock = threading.Lock()
        self.operations: dict[str, str] = {}
        self.events: list[dict] = []
        self.submissions = 0
        self.lookups = 0
        self.received = threading.Event()
        self.committed = threading.Event()
        self.release = threading.Event()

    def event(self, kind: str, **fields) -> None:
        with self.lock:
            self.events.append({"event": kind, **fields})

    def register(self, operation_id: str, payload: str) -> tuple[int, dict]:
        # The key-to-payload check and insert share ONE lock. This contract is
        # specific to this process-lifetime teaching ledger, not inherent in POST.
        with self.lock:
            if operation_id in self.operations:
                if self.operations[operation_id] != payload:
                    self.events.append({"event": "conflict", "operation_id": operation_id})
                    return 409, {"status": "payload_conflict", "operation_id": operation_id}
                status, replay = 200, True
            else:
                self.operations[operation_id] = payload
                self.events.append({"event": "registered", "operation_id": operation_id})
                status, replay = 201, False
            return status, {"status": "accepted", "operation_id": operation_id,
                            "payload": payload, "replayed": replay}

    def lookup(self, operation_id: str) -> tuple[int, dict]:
        with self.lock:
            self.lookups += 1
            # One controlled stale read. Not a claim about ordinary HTTP caching.
            hidden = self.mode == "lookup_lag" and self.lookups == 1
            if hidden or operation_id not in self.operations:
                return 404, {"status": "not_found", "operation_id": operation_id}
            return 200, {"status": "accepted", "operation_id": operation_id,
                         "payload": self.operations[operation_id]}

    def snapshot(self) -> dict:
        with self.lock:
            return {"registered_effects": len(self.operations),
                    "operations": dict(self.operations), "events": list(self.events)}


def valid_id(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9:_-]{1,80}", value) is not None


def handler_for(ledger: Ledger):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:
            pass

        def reply(self, status: int, body: dict) -> None:
            encoded = json.dumps(body).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(encoded)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                # The client may already have closed its timed-out connection.
                # This does NOT undo a registration or prove response delivery.
                pass
            finally:
                self.close_connection = True

        def do_POST(self) -> None:
            if self.path != "/operations":
                self.reply(404, {"status": "unknown_route"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 4096:
                    raise ValueError("body size")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError("object required")
                operation_id, payload = data.get("operation_id"), data.get("payload")
                if not valid_id(operation_id) or not isinstance(payload, str) or not 0 < len(payload) <= 256:
                    raise ValueError("invalid operation")
            except (ValueError, TypeError, UnicodeDecodeError):
                self.reply(400, {"status": "bad_request"})
                return

            with ledger.lock:
                ledger.submissions += 1
                first = ledger.submissions == 1
            ledger.event("received", operation_id=operation_id)
            if first:
                ledger.received.set()
            if first and ledger.mode == "late_commit":
                if not ledger.release.wait(FIXTURE_LIMIT):
                    self.reply(503, {"status": "fixture_gate_expired"})
                    return
            status, body = ledger.register(operation_id, payload)
            if first:
                ledger.committed.set()
            if first and ledger.mode not in {"normal", "late_commit"}:
                if not ledger.release.wait(FIXTURE_LIMIT):
                    self.reply(503, {"status": "fixture_gate_expired"})
                    return
            ledger.event("response_attempt", operation_id=operation_id, http_status=status)
            self.reply(status, body)

        def do_GET(self) -> None:
            prefix = "/operations/"
            if not self.path.startswith(prefix):
                self.reply(404, {"status": "unknown_route"})
                return
            operation_id = unquote(self.path[len(prefix):])
            if not valid_id(operation_id):
                self.reply(400, {"status": "bad_request"})
                return
            status, body = ledger.lookup(operation_id)
            ledger.event("lookup_reply", operation_id=operation_id, http_status=status)
            self.reply(status, body)

    return Handler


class LabServer(ThreadingHTTPServer):
    # server_close joins request threads. Release gates BEFORE joining them.
    daemon_threads = False
    block_on_close = True

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(FIXTURE_LIMIT)
        return connection, address


@contextmanager
def running_service(mode: str = "normal"):
    if mode not in MODES:
        raise ValueError(mode)
    ledger = Ledger(mode)
    server = LabServer(("127.0.0.1", 0), handler_for(ledger))
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": 0.02}, name="http-receipt-serve")
    thread.start()
    try:
        yield server.server_address[1], ledger
    finally:
        ledger.release.set()
        server.shutdown()
        server.server_close()
        thread.join(FIXTURE_LIMIT)
        if thread.is_alive():
            raise RuntimeError("HTTP fixture failed to stop")


def request(port: int, method: str, path: str, body=None, *, timeout: float = 2.0,
            fixture_before_read=None) -> dict:
    # No URL argument, redirects, proxies, or arbitrary host. Only this loopback
    # listener is reachable through this helper.
    connection = HTTPConnection("127.0.0.1", port, timeout=timeout)
    encoded = json.dumps(body).encode() if body is not None else None
    try:
        connection.request(method, path, body=encoded,
                           headers={"Content-Type": "application/json"})
        if fixture_before_read is not None:
            # Local fault orchestration ONLY. Establish the intended event
            # order before the blocking response read; not remote evidence.
            fixture_before_read()
        response = connection.getresponse()
        return {"http_status": response.status,
                "body": json.loads(response.read().decode())}
    except socket.timeout:
        return {"transport": "timeout", "http_status": None}
    finally:
        connection.close()


def accepted(result: dict, operation_id: str, payload: str) -> bool:
    body = result.get("body", {})
    return (result.get("http_status") in {200, 201} and body.get("status") == "accepted"
            and body.get("operation_id") == operation_id and body.get("payload") == payload)


def replay_status(result: dict, operation_id: str, payload: str) -> str:
    if accepted(result, operation_id, payload):
        return "confirmed_replay"
    body = result.get("body", {})
    if (result.get("http_status") == 409 and body.get("status") == "payload_conflict"
            and body.get("operation_id") == operation_id):
        return "conflict_stop"
    return "unknown_stop"


def run(mode: str) -> dict:
    events = []
    with running_service(mode) as (port, ledger):
        operation = {"operation_id": OPERATION_ID, "payload": PAYLOAD}

        def establish_fault():
            if not ledger.received.wait(2.0):
                raise RuntimeError("expected receive gate was not established")
            if mode != "late_commit" and not ledger.committed.wait(2.0):
                raise RuntimeError("expected register-before-read gate was not established")

        first = request(port, "POST", "/operations", operation,
                        timeout=2.0 if mode == "normal" else READ_TIMEOUT,
                        fixture_before_read=None if mode == "normal" else establish_fault)
        events.append({"event": "submit", "operation_id": OPERATION_ID, **first})
        if mode == "normal":
            if not accepted(first, OPERATION_ID, PAYLOAD):
                raise RuntimeError("normal fixture did not return its expected receipt")
            status = "confirmed_receipt"
        else:
            # The fault gate above established event order before response read.
            # Business decisions use only HTTP evidence, not these local events.
            if first.get("transport") != "timeout":
                raise RuntimeError("expected HTTP read timeout fixture was not established")
            if mode in {"same_id_retry", "payload_conflict"}:
                replay = dict(operation)
                if mode == "payload_conflict":
                    replay["payload"] = "publish-v2"
                result = request(port, "POST", "/operations", replay)
                events.append({"event": "retry_same_id", **result})
                status = replay_status(result, OPERATION_ID, PAYLOAD)
            else:
                result = request(port, "GET", "/operations/" + quote(OPERATION_ID, safe=""))
                events.append({"event": "lookup", "operation_id": OPERATION_ID, **result})
                status = "confirmed_lookup" if accepted(result, OPERATION_ID, PAYLOAD) else "unknown_stop"
                if mode == "unsafe_new_id":
                    if status != "confirmed_lookup":
                        raise RuntimeError("counterexample requires a confirmed first registration")
                    second_id = OPERATION_ID + "-retry"
                    result = request(port, "POST", "/operations",
                                     {"operation_id": second_id, "payload": PAYLOAD})
                    events.append({"event": "unsafe_new_id", "operation_id": second_id, **result})
                    if not accepted(result, second_id, PAYLOAD):
                        raise RuntimeError("counterexample second registration failed")
                    status = "duplicate_effect"
        # Freeze the HOST decision before releasing a late original request.
        host = {"status": status, "events": events}
    return {"mode": mode, "host": host, "observer_after_cleanup": ledger.snapshot(),
            "listener_closed": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="normal")
    args = parser.parse_args()
    result = run(args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["host"]["status"].startswith("confirmed_") else 2)
