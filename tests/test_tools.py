"""Week 4 tool and orchestrator tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent_orchestrator import AgentOrchestratorError, run_agent
from src.requisition_store import RequisitionStore
from src.tools import (
    create_requisition_draft,
    dispatch_tool,
    get_reorder_status,
    get_supplier_quotations,
    route_requisition_for_approval,
    set_reference_date,
    set_store,
)


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = RequisitionStore(Path(self.tmp.name) / "requisitions.json")
        set_store(self.store)
        set_reference_date("2026-09-16")

    def tearDown(self):
        self.tmp.cleanup()

    # --- Missing parameters ---

    def test_get_quotations_missing_item_id(self):
        result = get_supplier_quotations()
        self.assertEqual(result["error"], "MISSING_PARAMETER")
        self.assertEqual(result["parameter"], "item_id")

    def test_create_draft_missing_quantity(self):
        result = create_requisition_draft(
            item_id="ITEM-004",
            quantity=None,
            selected_quotation_id="Q-107",
            requested_by="Tester",
        )
        self.assertEqual(result["error"], "MISSING_PARAMETER")
        self.assertEqual(result["parameter"], "quantity")

    def test_route_missing_requisition_id(self):
        result = route_requisition_for_approval()
        self.assertEqual(result["error"], "MISSING_PARAMETER")

    # --- Invalid / unauthorized ---

    def test_get_quotations_item_not_found(self):
        result = get_supplier_quotations("ITEM-999")
        self.assertEqual(result["error"], "ITEM_NOT_FOUND")

    def test_get_quotations_empty_list_with_warning(self):
        result = get_supplier_quotations("ITEM-007")
        self.assertEqual(result["quotations"], [])
        self.assertEqual(result["warning"], "NO_QUOTATIONS_ON_FILE")

    def test_create_draft_invalid_quantity(self):
        result = create_requisition_draft(
            item_id="ITEM-004",
            quantity=0,
            selected_quotation_id="Q-107",
            requested_by="Tester",
        )
        self.assertEqual(result["error"], "INVALID_QUANTITY")

    def test_create_draft_wrong_quotation_for_item(self):
        result = create_requisition_draft(
            item_id="ITEM-004",
            quantity=10,
            selected_quotation_id="Q-101",
            requested_by="Tester",
        )
        self.assertEqual(result["error"], "QUOTATION_NOT_FOUND_FOR_ITEM")

    def test_create_draft_expired_quotation(self):
        result = create_requisition_draft(
            item_id="ITEM-005",
            quantity=5,
            selected_quotation_id="Q-109",
            requested_by="Tester",
        )
        self.assertEqual(result["error"], "QUOTATION_EXPIRED")

    def test_route_nonexistent_requisition(self):
        result = route_requisition_for_approval("REQ-NOPE-0001")
        self.assertEqual(result["error"], "REQUISITION_NOT_FOUND")

    def test_route_already_pending(self):
        draft = create_requisition_draft(
            item_id="ITEM-004",
            quantity=5,
            selected_quotation_id="Q-107",
            requested_by="Tester",
        )
        first = route_requisition_for_approval(draft["requisition_id"])
        self.assertEqual(first["status"], "PENDING_APPROVAL")
        second = route_requisition_for_approval(draft["requisition_id"])
        self.assertEqual(second["error"], "INVALID_STATUS")
        self.assertEqual(second["current_status"], "PENDING_APPROVAL")

    # --- Malformed quotation record ---

    def test_create_draft_malformed_quotation(self):
        with patch("src.tools.load_quotations") as mock_q:
            mock_q.return_value = {
                "ITEM-004": [
                    {
                        "quotation_id": "Q-BAD",
                        "item_id": "ITEM-004",
                        "supplier_name": "Bad Vendor",
                        "unit_price": "",
                        "quantity_available": "10",
                        "delivery_terms": "",
                        "quotation_valid_until": "",
                        "notes": "",
                    }
                ]
            }
            result = create_requisition_draft(
                item_id="ITEM-004",
                quantity=5,
                selected_quotation_id="Q-BAD",
                requested_by="Tester",
            )
        self.assertEqual(result["error"], "MALFORMED_QUOTATION_RECORD")

    # --- Happy paths ---

    def test_get_reorder_status_item_004(self):
        result = get_reorder_status("ITEM-004")
        self.assertTrue(result["needs_reorder"])
        self.assertEqual(result["replenishment_deficit"], 20.0)

    def test_create_draft_success(self):
        result = create_requisition_draft(
            item_id="ITEM-004",
            quantity=20,
            selected_quotation_id="Q-107",
            requested_by="Jane Okello",
        )
        self.assertEqual(result["status"], "DRAFT")
        self.assertEqual(result["unit_price"], 45000)
        self.assertEqual(result["total_estimated_cost"], 900000)
        self.assertIn("requisition_id", result)

    # --- Orchestrator API failure ---

    def test_orchestrator_api_unreachable(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = TimeoutError("API unreachable")

        with self.assertRaises(AgentOrchestratorError) as ctx:
            run_agent("Check ITEM-004", api_client=mock_client)

        self.assertIn("API unreachable", str(ctx.exception))
        self.assertTrue(any("ORCHESTRATOR ERROR" in line for line in ctx.exception.transcript))


if __name__ == "__main__":
    unittest.main()
