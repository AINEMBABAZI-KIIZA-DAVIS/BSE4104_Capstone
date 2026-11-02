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

We do not keep a winning supplier, bank details, an auto-route flag, or Gemini chat logs.

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

## What memory actually does

Second run of ITEM-004 without typing quantity and name: it fills 20 cartons and Jane Okello. It still checks stock, still loads quotes, still validates the quote in Python, still writes a new DRAFT, and still does not route unless we ask and type y.

## Critical-decision boundary

Memory must not silently control purchasing. Tests in `tests/test_bounded_agent.py` assert that a remembered ITEM-004 run still ends as `DRAFT`, not `PENDING_APPROVAL`.
