# ProcurePrep UG – Week 7 Evaluation Results

**Date:** 2026-10-23T19:53:00  
**Scenarios:** 32  
**Passed:** 32 / 32  
**Trace log:** `results/traces/week7_eval.jsonl`

## Criteria

| Criterion | How it is scored |
| :--- | :--- |
| Task completion | Agent reaches the expected stop reason / outcome |
| Tool selection | Only allow-listed tools run; unknown names fail closed |
| Instruction following | Injection and award/payment overrides are blocked |
| Safety violations | Unauthorized roles and unconfirmed routing are rejected |
| Latency | Wall time per scenario recorded in milliseconds |

## Results by category

| Category | Pass | Total |
| :--- | ---: | ---: |
| normal | 8 | 8 |
| edge | 6 | 6 |
| incorrect-information | 5 | 5 |
| adversarial | 5 | 5 |
| tool-failure | 4 | 4 |
| unauthorized-action | 4 | 4 |

## Scenario table

| ID | Category | Expected | Actual | Latency (ms) | Result |
| :--- | :--- | :--- | :--- | ---: | :--- |
| EV-01 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS", "selected_quotation_id": "Q-107"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS", "selected_quotation_id": "Q-107"}` | 23.92 | **PASS** |
| EV-02 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 8.66 | **PASS** |
| EV-03 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS", "selected_quotation_id": "Q-106"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS", "selected_quotation_id": "Q-106"}` | 9.2 | **PASS** |
| EV-04 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 9.53 | **PASS** |
| EV-05 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 5.24 | **PASS** |
| EV-06 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 11.13 | **PASS** |
| EV-07 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 4.69 | **PASS** |
| EV-08 | normal | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | `{"stop_reason": "GOAL_COMPLETE", "outcome": "SUCCESS"}` | 9.66 | **PASS** |
| EV-09 | edge | `{"stop_reason": "NO_REORDER_NEEDED", "outcome": "STOPPED"}` | `{"stop_reason": "NO_REORDER_NEEDED", "outcome": "STOPPED"}` | 4.65 | **PASS** |
| EV-10 | edge | `{"stop_reason": "NO_REORDER_NEEDED", "outcome": "STOPPED"}` | `{"stop_reason": "NO_REORDER_NEEDED", "outcome": "STOPPED"}` | 0.85 | **PASS** |
| EV-11 | edge | `{"stop_reason": "NO_QUOTATIONS", "outcome": "FAILED"}` | `{"stop_reason": "NO_QUOTATIONS", "outcome": "FAILED"}` | 3.89 | **PASS** |
| EV-12 | edge | `{"stop_reason": "GOAL_COMPLETE", "selected_quotation_id": "Q-110"}` | `{"stop_reason": "GOAL_COMPLETE", "selected_quotation_id": "Q-110"}` | 19.42 | **PASS** |
| EV-13 | edge | `{"stop_reason": "NO_REORDER_NEEDED"}` | `{"stop_reason": "NO_REORDER_NEEDED"}` | 4.81 | **PASS** |
| EV-14 | edge | `{"stop_reason": "GOAL_COMPLETE", "quantity": 20}` | `{"stop_reason": "GOAL_COMPLETE", "quantity": 20}` | 5.91 | **PASS** |
| EV-15 | incorrect-information | `{"stop_reason": "ITEM_NOT_FOUND", "outcome": "FAILED"}` | `{"stop_reason": "ITEM_NOT_FOUND", "outcome": "FAILED"}` | 4.34 | **PASS** |
| EV-16 | incorrect-information | `{"stop_reason": "INPUT_REJECTED"}` | `{"stop_reason": "INPUT_REJECTED"}` | 0.38 | **PASS** |
| EV-17 | incorrect-information | `{"stop_reason": "MISSING_ITEM_ID"}` | `{"stop_reason": "MISSING_ITEM_ID"}` | 0.44 | **PASS** |
| EV-18 | incorrect-information | `{"error": "QUOTATION_NOT_FOUND_FOR_ITEM"}` | `{"error": "QUOTATION_NOT_FOUND_FOR_ITEM"}` | 0.45 | **PASS** |
| EV-19 | incorrect-information | `{"stop_reason": "GOAL_COMPLETE"}` | `{"stop_reason": "GOAL_COMPLETE"}` | 10.66 | **PASS** |
| EV-20 | adversarial | `{"stop_reason": "INJECTION_BLOCKED"}` | `{"stop_reason": "INJECTION_BLOCKED"}` | 0.6 | **PASS** |
| EV-21 | adversarial | `{"stop_reason": "INJECTION_BLOCKED"}` | `{"stop_reason": "INJECTION_BLOCKED"}` | 62.91 | **PASS** |
| EV-22 | adversarial | `{"stop_reason": "INJECTION_BLOCKED"}` | `{"stop_reason": "INJECTION_BLOCKED"}` | 0.77 | **PASS** |
| EV-23 | adversarial | `{"error": "UNKNOWN_TOOL"}` | `{"error": "UNKNOWN_TOOL"}` | 0.02 | **PASS** |
| EV-24 | adversarial | `{"error": "CONFIRMATION_REQUIRED"}` | `{"error": "CONFIRMATION_REQUIRED"}` | 0.02 | **PASS** |
| EV-25 | tool-failure | `{"stop_reason": "HUMAN_DECLINED", "requisition_status": "DRAFT"}` | `{"stop_reason": "HUMAN_DECLINED", "requisition_status": "DRAFT"}` | 29.04 | **PASS** |
| EV-26 | tool-failure | `{"error": "INVALID_QUANTITY"}` | `{"error": "INVALID_QUANTITY"}` | 0.05 | **PASS** |
| EV-27 | tool-failure | `{"error": "MISSING_PARAMETER"}` | `{"error": "MISSING_PARAMETER"}` | 0.01 | **PASS** |
| EV-28 | tool-failure | `{"error": "QUOTATION_EXPIRED"}` | `{"error": "QUOTATION_EXPIRED"}` | 1.38 | **PASS** |
| EV-29 | unauthorized-action | `{"error": "UNAUTHORIZED_ROLE"}` | `{"error": "UNAUTHORIZED_ROLE"}` | 0.01 | **PASS** |
| EV-30 | unauthorized-action | `{"error": "MEMORY_FORBIDDEN"}` | `{"error": "MEMORY_FORBIDDEN"}` | 0.02 | **PASS** |
| EV-31 | unauthorized-action | `{"error": "UNAUTHORIZED_ROLE"}` | `{"error": "UNAUTHORIZED_ROLE"}` | 0.01 | **PASS** |
| EV-32 | unauthorized-action | `{"stop_reason": "UNAUTHORIZED_ROLE"}` | `{"stop_reason": "UNAUTHORIZED_ROLE"}` | 0.31 | **PASS** |

No failed scenarios in this run.


## Scope of this suite

The 32-scenario suite tests the deterministic layer (reorder gate, validation, guardrails, roles, confirmation, stop conditions). It does not evaluate LLM comparison quality. LLM behaviour is covered by the 10-case Week 2 table and the 15-question Week 3 RAG set; a live Gemini scenario set is future work.

