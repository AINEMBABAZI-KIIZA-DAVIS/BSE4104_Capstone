# ProcurePrep UG – Week 4 Failure and Authorization Tests

**Date:** 2026-09-23T15:45:01  
**Suite:** `tests/test_tools.py`  
**Result:** 16 tests, 0 failure(s) — **PASS**

These tests cover the assignment requirement to exercise missing parameters, unauthorized requests, unavailable services and unexpected tool responses.

## Cases

| Requirement | Test | Expected behaviour |
| :--- | :--- | :--- |
| Missing parameters | `test_get_quotations_missing_item_id`, `test_create_draft_missing_quantity`, `test_route_missing_requisition_id` | Structured `MISSING_PARAMETER`; no crash |
| Unauthorized / unknown tool | `test_unknown_tool_rejected` | `UNKNOWN_TOOL` for `award_supplier_contract` |
| Unauthorized routing | `test_human_declines_routing` | `HUMAN_DECLINED`; requisition stays `DRAFT` |
| Invalid / expired / wrong-item | `test_create_draft_expired_quotation`, `test_create_draft_wrong_quotation_for_item`, `test_create_draft_invalid_quantity` | Deterministic reject; no record written |
| Unexpected tool response | `test_create_draft_malformed_quotation` | `MALFORMED_QUOTATION_RECORD` |
| Unavailable service | `test_orchestrator_api_unreachable` | `AgentOrchestratorError` with transcript; no hang |
| Invalid status | `test_route_already_pending` | `INVALID_STATUS` on second route |

## Raw unittest output

```
test_create_draft_expired_quotation (tests.test_tools.ToolTests) ... ok
test_create_draft_invalid_quantity (tests.test_tools.ToolTests) ... ok
test_create_draft_malformed_quotation (tests.test_tools.ToolTests) ... ok
test_create_draft_missing_quantity (tests.test_tools.ToolTests) ... ok
test_create_draft_success (tests.test_tools.ToolTests) ... ok
test_create_draft_wrong_quotation_for_item (tests.test_tools.ToolTests) ... ok
test_get_quotations_empty_list_with_warning (tests.test_tools.ToolTests) ... ok
test_get_quotations_item_not_found (tests.test_tools.ToolTests) ... ok
test_get_quotations_missing_item_id (tests.test_tools.ToolTests) ... ok
test_get_reorder_status_item_004 (tests.test_tools.ToolTests) ... ok
test_human_declines_routing (tests.test_tools.ToolTests) ... ok
test_orchestrator_api_unreachable (tests.test_tools.ToolTests) ... ok
test_route_already_pending (tests.test_tools.ToolTests) ... ok
test_route_missing_requisition_id (tests.test_tools.ToolTests) ... ok
test_route_nonexistent_requisition (tests.test_tools.ToolTests) ... ok
test_unknown_tool_rejected (tests.test_tools.ToolTests) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.061s

OK
```
