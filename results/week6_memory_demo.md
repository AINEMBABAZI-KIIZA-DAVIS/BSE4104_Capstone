# ProcurePrep UG – Week 6 Memory and State Demonstration

**Purpose:** Show that justified memory prefills quantity and requester on a repeat preparation without silently routing or awarding.

## Run 1 — first preparation (no prior history)

- Stop: `GOAL_COMPLETE`  
- Outcome: `SUCCESS`  
- Quantity: 20  
- Requester: Jane Okello  
- Quotation: Q-107  
- Requisition: REQ-20260923-0001 status=DRAFT  
- Memory hints used: ['none']

```
session=SES-8c59ad4b6f
goal=PREPARE_REQUISITION
item=ITEM-004 requested_by=Jane Okello quantity=20 route=False
[SENSE] no memory hints applied

--- iteration 1 PLAN ---
{"type": "act", "tool": "get_reorder_status", "args": {"item_id": "ITEM-004"}}
[ACT] get_reorder_status({"item_id": "ITEM-004"})
[OBSERVE] {
  "item_id": "ITEM-004",
  "item_name": "Thermal POS Receipt Rolls 80mm",
  "current_stock": 5.0,
  "reorder_threshold": 25.0,
  "unit": "Carton",
  "needs_reorder": true,
  "replenishment_deficit": 20.0,
  "reference_date": "2026-09-16"
}

--- iteration 2 PLAN ---
{"type": "act", "tool": "get_supplier_quotations", "args": {"item_id": "ITEM-004"}}
[ACT] get_supplier_quotations({"item_id": "ITEM-004"})
[OBSERVE] {
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
    },
    {
      "quotation_id": "Q-108",
      "supplier_name": "Victoria Paper Traders",
      "unit_price": 48000,
      "quantity_available": 40,
      "delivery_terms": "Delivery within 24 hours",
      "quotation_valid_until": "2026-10-05",
      "notes": "Express delivery included"
    }
  ]
}

--- iteration 3 PLAN ---
{"type": "act", "tool": "create_requisition_draft", "args": {"item_id": "ITEM-004", "quantity": 20, "selected_quotation_id": "Q-107", "requested_by": "Jane Okello"}}
[ACT] create_requisition_draft({"item_id": "ITEM-004", "quantity": 20, "selected_quotation_id": "Q-107", "requested_by": "Jane Okello"})
[OBSERVE] {
  "requisition_id": "REQ-20260923-0001",
  "item_id": "ITEM-004",
  "quantity": 20,
  "selected_quotation_id": "Q-107",
  "unit_price": 45000,
  "total_estimated_cost": 900000,
  "status": "DRAFT",
  "created_at": "2026-09-23T12:54:23.739946+00:00"
}

--- iteration 4 PLAN ---
{"type": "stop", "reason": "GOAL_COMPLETE"}
[STOP] GOAL_COMPLETE outcome=SUCCESS
[MEMORY] recorded successful preparation
```

## Run 2 — repeat ITEM-004 with quantity and name omitted

- Stop: `GOAL_COMPLETE`  
- Outcome: `SUCCESS`  
- Quantity prefilled: 20  
- Requester prefilled: Jane Okello  
- Memory hints used: ['default_requested_by', 'last_quantity', 'last_quotation_id_hint_only']  
- Status remains: DRAFT (not PENDING_APPROVAL)

```
session=SES-4285811583
goal=PREPARE_REQUISITION
item=ITEM-004 requested_by=None quantity=None route=False
[SENSE] memory hints applied: ['default_requested_by', 'last_quantity', 'last_quotation_id_hint_only']

--- iteration 1 PLAN ---
{"type": "act", "tool": "get_reorder_status", "args": {"item_id": "ITEM-004"}}
[ACT] get_reorder_status({"item_id": "ITEM-004"})
[OBSERVE] {
  "item_id": "ITEM-004",
  "item_name": "Thermal POS Receipt Rolls 80mm",
  "current_stock": 5.0,
  "reorder_threshold": 25.0,
  "unit": "Carton",
  "needs_reorder": true,
  "replenishment_deficit": 20.0,
  "reference_date": "2026-09-16"
}

--- iteration 2 PLAN ---
{"type": "act", "tool": "get_supplier_quotations", "args": {"item_id": "ITEM-004"}}
[ACT] get_supplier_quotations({"item_id": "ITEM-004"})
[OBSERVE] {
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
    },
    {
      "quotation_id": "Q-108",
      "supplier_name": "Victoria Paper Traders",
      "unit_price": 48000,
      "quantity_available": 40,
      "delivery_terms": "Delivery within 24 hours",
      "quotation_valid_until": "2026-10-05",
      "notes": "Express delivery included"
    }
  ]
}

--- iteration 3 PLAN ---
{"type": "act", "tool": "create_requisition_draft", "args": {"item_id": "ITEM-004", "quantity": 20, "selected_quotation_id": "Q-107", "requested_by": "Jane Okello"}}
[ACT] create_requisition_draft({"item_id": "ITEM-004", "quantity": 20, "selected_quotation_id": "Q-107", "requested_by": "Jane Okello"})
[OBSERVE] {
  "requisition_id": "REQ-20260923-0002",
  "item_id": "ITEM-004",
  "quantity": 20,
  "selected_quotation_id": "Q-107",
  "unit_price": 45000,
  "total_estimated_cost": 900000,
  "status": "DRAFT",
  "created_at": "2026-09-23T12:54:23.751042+00:00"
}

--- iteration 4 PLAN ---
{"type": "stop", "reason": "GOAL_COMPLETE"}
[STOP] GOAL_COMPLETE outcome=SUCCESS
[MEMORY] recorded successful preparation
```

## What this shows

- Memory improved the second task by prefilling last quantity and default requester.
- The agent still re-checked reorder status and quotations.
- The new record stayed DRAFT. Memory did not route or award a supplier.
