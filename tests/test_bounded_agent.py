"""Week 5 bounded agent and Week 6 memory / MCP tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent_memory import AgentMemory
from src.bounded_agent import run_bounded_agent
from src.mcp_interface import call_mcp_tool, list_mcp_tools
from src.requisition_store import RequisitionStore
from src.tools import set_reference_date, set_store


class BoundedAgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = RequisitionStore(Path(self.tmp.name) / "requisitions.json")
        self.memory = AgentMemory(Path(self.tmp.name) / "memory.json")
        set_store(self.store)
        set_reference_date("2026-09-16")

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_item_004(self):
        state, _ = run_bounded_agent(
            item_id="ITEM-004",
            requested_by="Jane Okello",
            memory=self.memory,
        )
        self.assertEqual(state.outcome, "SUCCESS")
        self.assertEqual(state.stop_reason, "GOAL_COMPLETE")
        self.assertEqual(state.selected_quotation_id, "Q-107")
        self.assertEqual(state.requisition_status, "DRAFT")
        self.assertGreaterEqual(state.iteration, 3)

    def test_early_stop_sufficient_stock(self):
        state, transcript = run_bounded_agent(
            item_id="ITEM-002",
            requested_by="Jane Okello",
            memory=self.memory,
            persist_memory=False,
        )
        self.assertEqual(state.stop_reason, "NO_REORDER_NEEDED")
        self.assertIsNone(state.requisition_id)
        self.assertTrue(any("get_supplier_quotations" not in line or "[ACT]" not in line for line in transcript))
        self.assertFalse(any("[ACT] get_supplier_quotations" in line for line in transcript))

    def test_failure_no_quotations(self):
        state, _ = run_bounded_agent(
            item_id="ITEM-007",
            requested_by="Jane Okello",
            memory=self.memory,
            persist_memory=False,
        )
        self.assertEqual(state.outcome, "FAILED")
        self.assertEqual(state.stop_reason, "NO_QUOTATIONS")

    def test_recovery_expired_then_valid_quote(self):
        state, transcript = run_bounded_agent(
            item_id="ITEM-005",
            requested_by="Jane Okello",
            memory=self.memory,
        )
        self.assertEqual(state.outcome, "SUCCESS")
        self.assertEqual(state.selected_quotation_id, "Q-110")
        self.assertIn("Q-109", state.excluded_quotation_ids)
        self.assertGreaterEqual(state.recovery_attempts, 1)
        self.assertTrue(any("QUOTATION_EXPIRED" in line for line in transcript))

    def test_human_declines_routing(self):
        state, _ = run_bounded_agent(
            item_id="ITEM-004",
            requested_by="Jane Okello",
            wants_routing=True,
            confirm_callback=lambda name, args: False,
            memory=self.memory,
            persist_memory=False,
        )
        self.assertEqual(state.stop_reason, "HUMAN_DECLINED")
        self.assertEqual(state.requisition_status, "DRAFT")

    def test_missing_item_id(self):
        state, _ = run_bounded_agent(
            item_id=None,
            requested_by="Jane Okello",
            memory=self.memory,
            persist_memory=False,
        )
        self.assertEqual(state.stop_reason, "MISSING_ITEM_ID")

    def test_unknown_item(self):
        state, _ = run_bounded_agent(
            item_id="ITEM-999",
            requested_by="Jane Okello",
            memory=self.memory,
            persist_memory=False,
        )
        self.assertEqual(state.stop_reason, "ITEM_NOT_FOUND")


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = RequisitionStore(Path(self.tmp.name) / "requisitions.json")
        self.memory = AgentMemory(Path(self.tmp.name) / "memory.json")
        set_store(self.store)
        set_reference_date("2026-09-16")

    def tearDown(self):
        self.tmp.cleanup()

    def test_memory_prefills_quantity_and_requester(self):
        first, _ = run_bounded_agent(
            item_id="ITEM-004",
            requested_by="Jane Okello",
            quantity=20,
            memory=self.memory,
        )
        self.assertEqual(first.outcome, "SUCCESS")

        second, transcript = run_bounded_agent(
            item_id="ITEM-004",
            requested_by=None,
            quantity=None,
            memory=self.memory,
        )
        self.assertEqual(second.outcome, "SUCCESS")
        self.assertEqual(second.quantity, 20)
        self.assertEqual(second.requested_by, "Jane Okello")
        self.assertIn("last_quantity", second.memory_hints_used)
        self.assertIn("default_requested_by", second.memory_hints_used)
        self.assertTrue(any("memory hints applied" in line for line in transcript))

    def test_memory_does_not_auto_route(self):
        run_bounded_agent(
            item_id="ITEM-004",
            requested_by="Jane Okello",
            memory=self.memory,
        )
        state, _ = run_bounded_agent(
            item_id="ITEM-004",
            memory=self.memory,
            wants_routing=False,
        )
        self.assertEqual(state.requisition_status, "DRAFT")
        self.assertNotEqual(state.requisition_status, "PENDING_APPROVAL")

    def test_memory_forbidden_role(self):
        locked = AgentMemory(Path(self.tmp.name) / "locked.json", role="visitor")
        hints = locked.hints_for("ITEM-004")
        self.assertEqual(hints["error"], "MEMORY_FORBIDDEN")


class McpInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        set_store(RequisitionStore(Path(self.tmp.name) / "requisitions.json"))
        set_reference_date("2026-09-16")

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_tools(self):
        names = {t["name"] for t in list_mcp_tools()}
        self.assertEqual(
            names,
            {
                "get_reorder_status",
                "get_supplier_quotations",
                "create_requisition_draft",
                "route_requisition_for_approval",
            },
        )

    def test_unauthorized_role(self):
        result = call_mcp_tool("get_reorder_status", {"item_id": "ITEM-004"}, role="vendor")
        self.assertEqual(result["error"], "UNAUTHORIZED_ROLE")

    def test_route_requires_confirmation(self):
        draft = call_mcp_tool(
            "create_requisition_draft",
            {
                "item_id": "ITEM-004",
                "quantity": 5,
                "selected_quotation_id": "Q-107",
                "requested_by": "Tester",
            },
        )
        blocked = call_mcp_tool(
            "route_requisition_for_approval",
            {"requisition_id": draft["requisition_id"]},
            confirmed=False,
        )
        self.assertEqual(blocked["error"], "CONFIRMATION_REQUIRED")

    def test_unknown_mcp_tool(self):
        result = call_mcp_tool("award_contract", {})
        self.assertEqual(result["error"], "UNKNOWN_TOOL")


if __name__ == "__main__":
    unittest.main()
