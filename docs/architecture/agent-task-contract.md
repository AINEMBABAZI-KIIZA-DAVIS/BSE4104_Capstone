# ProcurePrep Agent Task Contract (Week 5)

**Task name:** Prepare a purchase requisition for one inventory item  
**Implementation:** `src/bounded_agent.py`  
**Orchestration style:** Direct Python planner (Sense → Plan → Act → Observe → Stop / Re-plan)

---

## Goal

Prepare a **DRAFT** purchase requisition when an SME inventory item is below its reorder threshold, using only approved tools and current application data. Optionally stage routing to a human approver. The agent must not purchase, pay, or award a supplier.

## Why this task needs multiple steps

A single model call cannot safely do this. The agent must:

1. Confirm reorder need in deterministic code.
2. Read live quotations.
3. Survive an expired or rejected quote by re-planning.
4. Write a draft only after validation.
5. Stop or hand off before any higher-impact routing.

## Approved tools

| Tool | When the planner may call it |
| :--- | :--- |
| `get_reorder_status` | Reorder record is not yet in session state |
| `get_supplier_quotations` | Reorder is needed and quotes are not yet loaded |
| `create_requisition_draft` | A valid (or candidate) quotation exists and no draft ID is stored |
| `route_requisition_for_approval` | User asked to route **and** a DRAFT exists **and** a human confirms |

Any other tool name is treated as `UNKNOWN_TOOL` and stops the loop.

## Session state (see also Week 6 state model)

The planner reads `WorkflowState`: `item_id`, `iteration`, `reorder`, `quotations`, `excluded_quotation_ids`, `requisition_id`, `requisition_status`, `wants_routing`, `recovery_attempts`.

## Limits

| Limit | Value | Effect |
| :--- | :--- | :--- |
| Maximum iterations | 8 | `MAX_ITERATIONS` stop |
| Maximum recoveries | 2 | `RECOVERY_EXHAUSTED` stop |
| Approved tool allow-list | 4 tools | Unlisted names stop the loop |
| Reference date | 2026-09-16 | Expiry validation |

## Stop conditions

| Reason | Meaning |
| :--- | :--- |
| `GOAL_COMPLETE` | Draft created; routing done only if requested and confirmed |
| `NO_REORDER_NEEDED` | Stock is at or above threshold — safe early stop |
| `NO_QUOTATIONS` | Reorder needed but no quotes on file |
| `NO_VALID_QUOTATION` | All remaining quotes expired or excluded |
| `ITEM_NOT_FOUND` / `MISSING_ITEM_ID` | Cannot sense a usable item |
| `HUMAN_DECLINED` | Officer refused routing; draft left unchanged |
| `MAX_ITERATIONS` / `RECOVERY_EXHAUSTED` | Bound hit; human must take over |

## Human hand-off / approval

- Creating a DRAFT is low-risk and does not require confirmation.
- `route_requisition_for_approval` always requires explicit confirmation.
- Decline returns `HUMAN_DECLINED` and does not change status.
- The agent never issues a purchase order or payment.

## Memory boundary (Week 6)

Memory may prefill `requested_by` and last `quantity`. It must not skip the reorder check, invent a quotation ID as a binding choice, or route a requisition.
