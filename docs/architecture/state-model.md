# ProcurePrep Workflow State Model (Week 6)

**Implementation:** `src/agent_state.py` (`WorkflowState`)  
**Lifetime:** One bounded agent session (`SES-…`). Not written to disk unless a draft or memory record is created.

---

## Purpose

Week 4 kept tool results only in the model conversation. Week 6 makes workflow state explicit so the planner, tests and traces can inspect the same fields: what has been sensed, which tool ran last, whether recovery is in progress, and why the loop stopped.

## Session fields

| Field | Type | Meaning |
| :--- | :--- | :--- |
| `session_id` | string | Unique run identifier |
| `goal` | string | Always `PREPARE_REQUISITION` in this milestone |
| `phase` | enum | `SENSE` → `PLAN` → `ACT` → `OBSERVE` → `STOP` |
| `item_id` | string? | Target inventory item |
| `requested_by` | string? | Officer name (user or memory prefill) |
| `quantity` | int? | Units to draft |
| `wants_routing` | bool | Whether to stage high-impact routing |
| `iteration` | int | Plan/act cycles used |
| `max_iterations` | int | Hard cap (8) |
| `reorder` | object? | Last `get_reorder_status` payload |
| `quotations` | list? | Last `get_supplier_quotations` rows |
| `excluded_quotation_ids` | list | Quotes rejected this session (e.g. expired) |
| `selected_quotation_id` | string? | Quote accepted by the draft tool |
| `requisition_id` / `status` | string? | Draft identity and `DRAFT` / `PENDING_APPROVAL` |
| `recovery_attempts` | int | Failed tool observations this session |
| `stop_reason` / `outcome` | string? | Why the loop ended |
| `memory_hints_used` | list | Which memory fields were applied |

## State transitions

```
SENSE  → apply memory hints; do not call tools
PLAN   → choose next approved tool or a stop reason
ACT    → dispatch tool (or stage human confirm)
OBSERVE→ write tool result into session fields; maybe re-plan
STOP   → terminal; no further tools
```

Re-plan is a return from `OBSERVE` to `PLAN` inside the iteration limit (for example after `QUOTATION_EXPIRED`).

## What is not session state

- Inventory and quotation CSVs remain the system of record for operational data.
- `data/requisitions.json` holds draft records across sessions.
- `data/agent_memory.json` holds justified long-lived hints (see Memory Design Note).
- Model chat history is not the workflow state.
