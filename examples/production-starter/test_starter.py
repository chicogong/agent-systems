"""Unit tests for the production agent starter harness."""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_starter import (
    ContextAssembler,
    HostApprovalGate,
    LiveLLMClient,
    LLMAPIError,
    LLMClientError,
    LLMNetworkError,
    LLMResponseError,
    MockInferenceEngine,
    ToolDefinition,
    ToolRiskLevel,
    Turn,
    truncate_tool_output,
)
from demo import run_demo


class ProductionStarterTests(unittest.TestCase):
    def setUp(self):
        self.tools = [
            ToolDefinition(
                name="read_file",
                description="Read file content",
                parameters={"path": {"type": "string"}},
                risk_level=ToolRiskLevel.READ_ONLY,
            ),
            ToolDefinition(
                name="write_file",
                description="Write file content",
                parameters={"path": {"type": "string"}},
                risk_level=ToolRiskLevel.MUTATION,
            ),
        ]
        self.assembler = ContextAssembler(
            system_role="You are a test assistant.",
            tools=self.tools,
            session_rules="Rule 1: Always be safe.",
        )

    def test_prefix_caching_stability_across_appends(self):
        engine = MockInferenceEngine()

        # Turn 1
        self.assembler.append_turn(Turn(role="user", content="Hello world"))
        prompt1 = self.assembler.assemble_prompt()
        res1 = engine.query(prompt1)
        self.assertEqual(res1["cached_tokens"], 0)

        # Turn 2: Append-only preserves entire prompt1 as prefix
        self.assembler.append_turn(Turn(role="assistant", content="Hi there!"))
        prompt2 = self.assembler.assemble_prompt()
        res2 = engine.query(prompt2)

        # Cache read should equal prompt1 token count
        self.assertEqual(res2["cached_tokens"], res1["total_tokens"])
        self.assertTrue(res2["hit_rate_percent"] > 80.0)

    def test_head_tail_truncation_limits_context_rot(self):
        raw_lines = [f"Log line {i}" for i in range(100)]
        raw_text = "\n".join(raw_lines)
        truncated = truncate_tool_output(raw_text, max_lines=30, head_lines=10, tail_lines=10)

        lines = truncated.splitlines()
        self.assertEqual(len(lines), 21)  # 10 head + 1 marker + 10 tail
        self.assertTrue("Log line 0" in lines[0])
        self.assertTrue("Log line 9" in lines[9])
        self.assertTrue("truncated by Host Guard" in lines[10])
        self.assertTrue("Log line 90" in lines[11])
        self.assertTrue("Log line 99" in lines[20])

    def test_short_tool_output_is_not_truncated(self):
        short_text = "Line 1\nLine 2\nLine 3"
        result = truncate_tool_output(short_text, max_lines=40)
        self.assertEqual(result, short_text)

    def test_host_approval_gate_blocks_unauthorized_mutation(self):
        # Gate that only allows writes to /tmp
        def safe_approval(tool: str, args: dict) -> bool:
            return args.get("path", "").startswith("/tmp/")

        gate = HostApprovalGate(approval_hook=safe_approval)
        write_tool = self.tools[1]

        # Dangerous write
        allowed, reason = gate.evaluate(write_tool, {"path": "/etc/passwd"})
        self.assertFalse(allowed)
        self.assertIn("DENIED", reason)

        # Safe write
        allowed, reason = gate.evaluate(write_tool, {"path": "/tmp/test.txt"})
        self.assertTrue(allowed)
        self.assertIn("granted", reason)

    def test_watermark_compaction_condenses_history(self):
        for i in range(15):
            self.assembler.append_turn(Turn(role="user", content=f"Step query {i}"))

        self.assertEqual(len(self.assembler.history), 15)
        compacted = self.assembler.check_and_compact(watermark_turns=10, retain_recent=4)

        self.assertTrue(compacted)
        self.assertEqual(len(self.assembler.history), 4)
        self.assertIn("Summarized 11 historical turns", self.assembler.milestone_summary)

    def test_full_demo_execution(self):
        summary = run_demo(verbose=False)
        self.assertEqual(summary["total_turns"], 5)
        self.assertEqual(summary["final_status"], "candidate_ready")
        self.assertTrue(summary["overall_hit_rate_percent"] > 65.0)


class LiveLLMCallerTests(unittest.TestCase):
    """Unit tests verifying request building, error handling, and payload parsing for LiveLLMClient."""

    def setUp(self):
        self.client = LiveLLMClient(
            api_key="test-api-key-12345",
            base_url="https://api.openai.com/v1",
            model="gpt-4o-mini",
            timeout=15.0,
        )

    # 1. Request Building Tests
    def test_build_request_defaults(self):
        req = self.client.build_request("Hello, world!")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(req.get_header("Authorization"), "Bearer test-api-key-12345")
        self.assertEqual(req.get_header("Content-type"), "application/json")

        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertEqual(payload["temperature"], 0.0)
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Hello, world!"}])
        self.assertNotIn("response_format", payload)

    def test_build_request_json_mode(self):
        req = self.client.build_request("Generate JSON output", json_mode=True)
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    def test_build_request_custom_options_and_payload(self):
        custom_client = LiveLLMClient(
            api_key="custom-key",
            base_url="https://api.deepseek.com/chat/completions",
            model="deepseek-chat",
            extra_headers={"X-Custom-Header": "CustomVal"},
        )
        req = custom_client.build_request(
            messages=[{"role": "system", "content": "Be concise."}, {"role": "user", "content": "Hi"}],
            model="deepseek-coder",
            temperature=0.7,
            extra_payload={"max_tokens": 100},
        )
        self.assertEqual(req.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(req.get_header("Authorization"), "Bearer custom-key")
        self.assertEqual(req.get_header("X-custom-header"), "CustomVal")

        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "deepseek-coder")
        self.assertEqual(payload["temperature"], 0.7)
        self.assertEqual(payload["max_tokens"], 100)
        self.assertEqual(len(payload["messages"]), 2)

    def test_build_request_with_turns_list(self):
        turns = [
            Turn(role="user", content="Inspect config"),
            Turn(
                role="assistant",
                content="",
                tool_calls=[{"name": "read_file", "args": {"path": "a.txt"}}],
            ),
            Turn(role="tool", content='{"exists": true}', name="read_file", tool_call_id="call_001"),
        ]
        req = self.client.build_request(turns)
        payload = json.loads(req.data.decode("utf-8"))
        msgs = payload["messages"]
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0], {"role": "user", "content": "Inspect config"})
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["tool_calls"], [{"name": "read_file", "args": {"path": "a.txt"}}])
        self.assertEqual(msgs[2]["role"], "tool")
        self.assertEqual(msgs[2]["name"], "read_file")
        self.assertEqual(msgs[2]["tool_call_id"], "call_001")

    def test_build_request_missing_api_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            client = LiveLLMClient(api_key=None)
            with self.assertRaises(ValueError) as ctx:
                client.build_request("Test")
            self.assertIn("API key is required", str(ctx.exception))

    def test_env_var_api_key_loading(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env-openai-key"}, clear=True):
            client = LiveLLMClient()
            self.assertEqual(client.api_key, "sk-env-openai-key")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-env-deepseek-key"}, clear=True):
            client = LiveLLMClient()
            self.assertEqual(client.api_key, "sk-env-deepseek-key")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "sk-env-gemini-key"}, clear=True):
            client = LiveLLMClient()
            self.assertEqual(client.api_key, "sk-env-gemini-key")

        with patch.dict(os.environ, {"LLM_API_KEY": "sk-env-generic-key"}, clear=True):
            client = LiveLLMClient()
            self.assertEqual(client.api_key, "sk-env-generic-key")

    # 2. Response and Payload Parsing Tests
    def test_parse_response_openai_format_with_cache_accounting(self):
        openai_mock_response = {
            "id": "chatcmpl-123",
            "model": "gpt-4o-mini-2024-07-18",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"status": "ok", "action": "inspect"}',
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 50,
                "total_tokens": 1050,
                "prompt_tokens_details": {
                    "cached_tokens": 800,
                },
            },
        }

        parsed = self.client.parse_response(json.dumps(openai_mock_response).encode("utf-8"))
        self.assertEqual(parsed["content"], '{"status": "ok", "action": "inspect"}')
        self.assertEqual(parsed["role"], "assistant")
        self.assertEqual(parsed["finish_reason"], "stop")
        self.assertEqual(parsed["model"], "gpt-4o-mini-2024-07-18")

        # Cache accounting metrics
        usage = parsed["usage"]
        self.assertEqual(usage["prompt_tokens"], 1000)
        self.assertEqual(usage["completion_tokens"], 50)
        self.assertEqual(usage["total_tokens"], 1050)
        self.assertEqual(usage["cached_tokens"], 800)
        self.assertEqual(usage["uncached_tokens"], 200)
        self.assertEqual(usage["hit_rate_percent"], 80.0)

        # Flat fields duck-typed for MockInferenceEngine
        self.assertEqual(parsed["cached_tokens"], 800)
        self.assertEqual(parsed["uncached_tokens"], 200)
        self.assertEqual(parsed["hit_rate_percent"], 80.0)

    def test_parse_response_deepseek_format_with_prompt_cache_hit_tokens(self):
        deepseek_mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Proposal accepted.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 500,
                "completion_tokens": 25,
                "total_tokens": 525,
                "prompt_cache_hit_tokens": 375,
                "prompt_cache_miss_tokens": 125,
            },
        }

        parsed = self.client.parse_response(deepseek_mock_response)
        self.assertEqual(parsed["content"], "Proposal accepted.")
        self.assertEqual(parsed["cached_tokens"], 375)
        self.assertEqual(parsed["uncached_tokens"], 125)
        self.assertEqual(parsed["hit_rate_percent"], 75.0)

    def test_parse_response_with_tool_calls(self):
        tool_call_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "write_file",
                                    "arguments": '{"path": "config.json", "content": "{}"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 200, "completion_tokens": 20, "total_tokens": 220},
        }
        parsed = self.client.parse_response(tool_call_response)
        self.assertEqual(parsed["content"], "")
        self.assertEqual(len(parsed["tool_calls"]), 1)
        self.assertEqual(parsed["tool_calls"][0]["function"]["name"], "write_file")

    def test_parse_response_cumulative_tokens_tracking(self):
        res1 = {
            "choices": [{"message": {"role": "assistant", "content": "A"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 10, "prompt_tokens_details": {"cached_tokens": 50}},
        }
        res2 = {
            "choices": [{"message": {"role": "assistant", "content": "B"}}],
            "usage": {"prompt_tokens": 200, "completion_tokens": 20, "prompt_tokens_details": {"cached_tokens": 150}},
        }
        self.client.parse_response(res1)
        self.assertEqual(self.client.cumulative_input_tokens, 100)
        self.assertEqual(self.client.cumulative_cached_tokens, 50)
        self.assertEqual(self.client.cumulative_uncached_tokens, 50)

        self.client.parse_response(res2)
        self.assertEqual(self.client.cumulative_input_tokens, 300)
        self.assertEqual(self.client.cumulative_cached_tokens, 200)
        self.assertEqual(self.client.cumulative_uncached_tokens, 100)

    # 3. Error Handling Tests
    def test_http_error_handling_extracts_status_and_body(self):
        error_body = json.dumps({"error": {"message": "Invalid API Key provided", "type": "invalid_request_error"}}).encode("utf-8")
        http_error = urllib.error.HTTPError(
            url="https://api.openai.com/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(error_body),
        )

        with patch("urllib.request.urlopen", side_effect=http_error):
            with self.assertRaises(LLMAPIError) as ctx:
                self.client.complete("Hello")
            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("Invalid API Key provided", ctx.exception.body)
            self.assertIn("401", str(ctx.exception))

    def test_network_error_handling(self):
        url_error = urllib.error.URLError("Connection refused [Errno 61]")
        with patch("urllib.request.urlopen", side_effect=url_error):
            with self.assertRaises(LLMNetworkError) as ctx:
                self.client.complete("Hello")
            self.assertIn("Connection refused", str(ctx.exception))

    def test_timeout_error_handling(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("Timed out")):
            with self.assertRaises(LLMNetworkError) as ctx:
                self.client.complete("Hello")
            self.assertIn("timed out", str(ctx.exception))

    def test_malformed_json_response_raises_response_error(self):
        with self.assertRaises(LLMResponseError) as ctx:
            self.client.parse_response(b"<html><head><title>502 Bad Gateway</title></head></html>")
        self.assertIn("Failed to parse LLM API response as JSON", str(ctx.exception))

    def test_missing_choices_raises_response_error(self):
        with self.assertRaises(LLMResponseError) as ctx:
            self.client.parse_response({"id": "123", "object": "chat.completion"})
        self.assertIn("missing 'choices' list", str(ctx.exception))

    def test_api_error_in_json_payload_raises_api_error(self):
        payload = {"error": {"message": "Rate limit exceeded; quota used up", "type": "rate_limit_error"}}
        with self.assertRaises(LLMAPIError) as ctx:
            self.client.parse_response(payload)
        self.assertIn("Rate limit exceeded", str(ctx.exception))

    # 4. Demo CLI and Integration Tests
    def test_demo_live_mode_with_mocked_network(self):
        mock_response = {
            "choices": [{"message": {"role": "assistant", "content": "I recommend proceeding with edit."}}],
            "usage": {"prompt_tokens": 300, "completion_tokens": 15, "total_tokens": 315, "prompt_tokens_details": {"cached_tokens": 200}},
        }
        mock_http_resp = MagicMock()
        mock_http_resp.read.return_value = json.dumps(mock_response).encode("utf-8")
        mock_http_resp.__enter__.return_value = mock_http_resp

        with patch("urllib.request.urlopen", return_value=mock_http_resp):
            summary = run_demo(verbose=False, live=True, api_key="test-key")
            self.assertTrue(summary["live"])
            self.assertEqual(summary["total_turns"], 5)
            self.assertEqual(summary["final_status"], "candidate_ready")
            self.assertTrue(summary["cumulative_input_tokens"] > 0)
            self.assertTrue(summary["cumulative_cached_tokens"] > 0)

    def test_demo_live_mode_missing_key_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                run_demo(verbose=False, live=True, api_key=None)
            self.assertIn("Live mode requires an API key", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
