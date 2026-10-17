# ProcurePrep UG – Tool Catalogue (Week 4)

**Project:** BSE4104 AI Agentic Capstone  
**Model:** `gemini-3.5-flash-lite` (Gemini native function calling via `google-genai`)  
**Implementation:** `src/tools.py`, orchestrated by `src/agent_orchestrator.py`

---

## Overview

| Tool | Risk level | Human confirmation |
| :--- | :--- | :--- |
| `get_reorder_status` | Read-only | No |
| `get_supplier_quotations` | Read-only | No |
| `create_requisition_draft` | Low (simulated draft) | No |
| `route_requisition_for_approval` | High (workflow state change) | **Yes — CLI y/n gate** |

---

## Tool 1: `get_supplier_quotations`

### Purpose
Retrieve current supplier quotation records for a given inventory item from `data/quotations.csv`. This is the “retrieves current application data” tool required by the brief.

### Input schema

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item_id` | string | Yes | Inventory item identifier (e.g. `ITEM-004`). |

### Output schema

**Success (quotations found):**

```json
{
  "item_id": "ITEM-004",
  "quotations": [
    {
      "quotation_id": "Q-107",
      "supplier_name": "PointOfSale Uganda Ltd",
      "unit_price": 45000,
      "quantity_available": 80,
      "delivery_terms": "",
      "quotation_valid_until": "2026-10-10",
      "notes": "High quality thermal paper 65gsm"
    }
  ]
}
```

**Success (no quotations):**

```json
{
  "item_id": "ITEM-007",
  "quotations": [],
  "warning": "NO_QUOTATIONS_ON_FILE"
}
```

**Failure:**

```json
{
  "error": "ITEM_NOT_FOUND",
  "item_id": "ITEM-999"
}
```

```json
{
  "error": "MISSING_PARAMETER",
  "parameter": "item_id",
  "message": "Required parameter 'item_id' was not provided."
}
```

### Authorization
Read-only. Any authenticated procurement officer role may call. No approval required.

### Failure behavior
- Unknown `item_id` (not in `inventory.csv`): structured `ITEM_NOT_FOUND` error; no exception raised.
- Known item with zero quotes: empty `quotations` list plus `warning: NO_QUOTATIONS_ON_FILE`; no exception raised.
- Missing `item_id`: structured `MISSING_PARAMETER` error.

---

## Tool 2: `create_requisition_draft`

### Purpose
Create a **DRAFT** purchase requisition record. This is the low-risk simulated side effect: it persists a draft locally but does **not** submit, approve, place an order, or commit spend.

### Input schema

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item_id` | string | Yes | Inventory item identifier. |
| `quantity` | integer | Yes | Units to requisition; must be > 0. |
| `selected_quotation_id` | string | Yes | Quotation ID from `get_supplier_quotations`. |
| `requested_by` | string | Yes | Name of requesting procurement officer. |

### Output schema

**Success:**

```json
{
  "requisition_id": "REQ-20260917-0001",
  "item_id": "ITEM-004",
  "quantity": 20,
  "selected_quotation_id": "Q-107",
  "unit_price": 45000,
  "total_estimated_cost": 900000,
  "status": "DRAFT",
  "created_at": "2026-09-17T00:15:00+00:00"
}
```

**Failure examples:**

```json
{
  "error": "INVALID_QUANTITY",
  "message": "quantity must be greater than zero.",
  "quantity": 0
}
```

```json
{
  "error": "QUOTATION_NOT_FOUND_FOR_ITEM",
  "item_id": "ITEM-004",
  "selected_quotation_id": "Q-101"
}
```

```json
{
  "error": "QUOTATION_EXPIRED",
  "selected_quotation_id": "Q-109",
  "quotation_valid_until": "2026-08-15",
  "reference_date": "2026-09-16"
}
```

```json
{
  "error": "MALFORMED_QUOTATION_RECORD",
  "selected_quotation_id": "Q-BAD",
  "message": "Quotation record is missing required fields for validation."
}
```

### Authorization
Any authenticated procurement officer may create a draft. Persisted to `data/requisitions.json` (configurable via `RequisitionStore` in tests).

### Failure behavior
Deterministic Python validation **before** any record is written:
- Reject if `quantity <= 0` → `INVALID_QUANTITY`
- Reject if `selected_quotation_id` does not belong to `item_id` → `QUOTATION_NOT_FOUND_FOR_ITEM`
- Reject if quotation `quotation_valid_until` is before reference date (`2026-09-16`) → `QUOTATION_EXPIRED`
- Reject malformed quotation rows (missing price or validity) → `MALFORMED_QUOTATION_RECORD`
- Missing required parameters → `MISSING_PARAMETER`

The LLM does not perform this validation; it is enforced in `src/tools.py`.

---

## Tool 3: `route_requisition_for_approval`

### Purpose
Mark a **DRAFT** requisition as `PENDING_APPROVAL` and simulate routing to a human approver (Charter: simulated, not live integration).

### Input schema

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `requisition_id` | string | Yes | ID returned by `create_requisition_draft`. |

### Output schema

**Success:**

```json
{
  "requisition_id": "REQ-20260917-0001",
  "status": "PENDING_APPROVAL",
  "routed_to": "Store Manager (simulated approver)",
  "routed_at": "2026-09-17T00:20:00+00:00"
}
```

**Failure:**

```json
{
  "error": "REQUISITION_NOT_FOUND",
  "requisition_id": "REQ-NOPE-0001"
}
```

```json
{
  "error": "INVALID_STATUS",
  "requisition_id": "REQ-20260917-0001",
  "current_status": "PENDING_APPROVAL",
  "message": "Only DRAFT requisitions can be routed for approval."
}
```

```json
{
  "error": "HUMAN_DECLINED",
  "message": "Human reviewer declined to execute this tool."
}
```

### Authorization
Only requisitions in `DRAFT` status may be routed. Re-routing an already pending requisition is rejected.

### Failure behavior
- Unknown `requisition_id` → `REQUISITION_NOT_FOUND`
- Status not `DRAFT` → `INVALID_STATUS`
- **Human confirmation gate:** before execution, the orchestrator prints the staged tool call and requires explicit `y` confirmation in the CLI. If declined, returns `HUMAN_DECLINED` without changing state.

---

## Tool 4 (optional): `get_reorder_status`

### Purpose
Expose the Week 2 deterministic reorder decision (`current_stock < reorder_threshold`) as an agent-callable tool so the model does not recompute thresholds probabilistically.

### Input schema

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `item_id` | string | Yes | Inventory item identifier. |

### Output schema

**Success:**

```json
{
  "item_id": "ITEM-004",
  "item_name": "Thermal POS Receipt Rolls 80mm",
  "current_stock": 5.0,
  "reorder_threshold": 25.0,
  "unit": "Carton",
  "needs_reorder": true,
  "replenishment_deficit": 20.0,
  "reference_date": "2026-09-16"
}
```

**Failure:** same as Tool 1 (`ITEM_NOT_FOUND`, `MISSING_PARAMETER`).

### Authorization
Read-only. No approval required.

### Failure behavior
Structured errors only; no exceptions for expected failure cases.

---

## Orchestration notes

- Tools are registered with Gemini via `types.GenerateContentConfig(tools=[...])` with **automatic function calling disabled** so the orchestrator can intercept `route_requisition_for_approval`.
- The model selects tools based on task state; there is no hardcoded pipeline order in Python.
- See `docs/architecture/agent-architecture.md` for the full Week 2 → Week 3 → Week 4 flow.
