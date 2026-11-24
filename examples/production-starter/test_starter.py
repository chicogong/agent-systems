"""Unit tests for the production agent starter harness."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_starter import (
    ContextAssembler,
    HostApprovalGate,
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


if __name__ == "__main__":
    unittest.main()
