# ProcurePrep Memory Design and Data Handling Note (Week 6)

**Implementation:** `src/agent_memory.py`  
**Store:** `data/agent_memory.json` (local, gitignored)

---

## What is stored

| Record | Fields | Why it is stored |
| :--- | :--- | :--- |
| Officer preference | `default_requested_by`, `prefer_cheapest_valid` | Avoid re-typing the usual requester on the next preparation |
| Item history | `last_quantity`, `last_quotation_id`, `last_requisition_id`, `last_prepared_at`, `times_prepared` | Prefill quantity for a repeat reorder of the same SKU |

`last_quotation_id` is a **hint only**. The agent still loads current quotes and the draft tool still validates expiry and item membership.

## What is not stored

- No supplier “winner” or award decision
- No payment or bank details
- No automatic `PENDING_APPROVAL` flag
- No raw Gemini conversation

## Who can access it

| Role | Read hints | Write history | Delete |
| :--- | :--- | :--- | :--- |
| `procurement_officer` | Yes | Yes | Yes |
| `store_manager` | Yes | Yes | Yes |
| Any other role | `MEMORY_FORBIDDEN` | No | No |

## Retention and deletion

- Default retention: **90 days** from `last_prepared_at`.
- Expired item-history rows are pruned on read/write.
- `delete_item(item_id)` removes one SKU’s history.
- `clear()` resets the file to empty preferences.

## How memory improves a legitimate task

On a second preparation of ITEM-004, if the officer omits quantity and name, the agent prefills last quantity (20 cartons) and `Jane Okello`. That reduces re-entry error. The agent still:

1. Re-runs `get_reorder_status`
2. Re-runs `get_supplier_quotations`
3. Validates the selected quote in Python
4. Creates a new DRAFT
5. Does **not** route unless the officer asks and confirms

## Critical-decision boundary

Memory must not silently control purchasing. Tests in `tests/test_bounded_agent.py` assert that a remembered ITEM-004 run still ends as `DRAFT`, not `PENDING_APPROVAL`.
