"""
ProcurePrep Week 4 – callable procurement tools.

Each tool returns a JSON-serializable dict. Validation for create_requisition_draft
and route_requisition_for_approval is deterministic Python, not LLM-based.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from src.procure_data import (
    REFERENCE_DATE_DEFAULT,
    check_reorder_need,
    load_inventory,
    load_quotations,
)
from src.requisition_store import RequisitionStore

# Module-level store; tests inject a temp path via set_store().
_store = RequisitionStore()
_reference_date = REFERENCE_DATE_DEFAULT


def set_store(store: RequisitionStore) -> None:
    global _store
    _store = store


def set_reference_date(iso_date: str) -> None:
    global _reference_date
    _reference_date = iso_date


def _missing_param(name: str) -> dict[str, Any]:
    return {
        "error": "MISSING_PARAMETER",
        "parameter": name,
        "message": f"Required parameter '{name}' was not provided.",
    }


def _parse_valid_until(value: Optional[str]) -> Optional[date]:
    if not value or not str(value).strip():
        return None
    return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()


def _is_quotation_expired(valid_until: Optional[str], reference: Optional[str] = None) -> bool:
    ref = _parse_valid_until(reference or _reference_date)
    exp = _parse_valid_until(valid_until)
    if ref is None or exp is None:
        return False
    return exp < ref


def get_supplier_quotations(item_id: Optional[str] = None) -> dict[str, Any]:
    """
    Retrieve current quotation records for an inventory item from quotations.csv.

    Args:
        item_id: Inventory item identifier (e.g. ITEM-004).
    """
    if item_id is None or str(item_id).strip() == "":
        return _missing_param("item_id")

    item_id = str(item_id).strip()
    inventory = load_inventory()
    if item_id not in inventory:
        return {"error": "ITEM_NOT_FOUND", "item_id": item_id}

    quotes = load_quotations().get(item_id, [])
    records = [
        {
            "quotation_id": q["quotation_id"],
            "supplier_name": q["supplier_name"],
            "unit_price": int(q["unit_price"]),
            "quantity_available": int(q["quantity_available"]),
            "delivery_terms": q.get("delivery_terms") or "",
            "quotation_valid_until": q.get("quotation_valid_until") or "",
            "notes": q.get("notes") or "",
        }
        for q in quotes
    ]

    result: dict[str, Any] = {"item_id": item_id, "quotations": records}
    if not records:
        result["warning"] = "NO_QUOTATIONS_ON_FILE"
    return result


def get_reorder_status(item_id: Optional[str] = None) -> dict[str, Any]:
    """
    Return the deterministic reorder decision for an inventory item.

    Args:
        item_id: Inventory item identifier.
    """
    if item_id is None or str(item_id).strip() == "":
        return _missing_param("item_id")

    item_id = str(item_id).strip()
    inventory = load_inventory()
    if item_id not in inventory:
        return {"error": "ITEM_NOT_FOUND", "item_id": item_id}

    item = inventory[item_id]
    needs = check_reorder_need(item["current_stock"], item["reorder_threshold"])
    deficit = max(0.0, item["reorder_threshold"] - item["current_stock"])

    return {
        "item_id": item_id,
        "item_name": item["item_name"],
        "current_stock": item["current_stock"],
        "reorder_threshold": item["reorder_threshold"],
        "unit": item["unit"],
        "needs_reorder": needs,
        "replenishment_deficit": deficit if needs else 0.0,
        "reference_date": _reference_date,
    }


def create_requisition_draft(
    item_id: Optional[str] = None,
    quantity: Optional[int] = None,
    selected_quotation_id: Optional[str] = None,
    requested_by: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a DRAFT purchase requisition (does not submit or approve spend).

    Args:
        item_id: Inventory item identifier.
        quantity: Units to requisition (must be > 0).
        selected_quotation_id: Quotation ID from get_supplier_quotations.
        requested_by: Name of the requesting procurement officer.
    """
    for name, value in [
        ("item_id", item_id),
        ("quantity", quantity),
        ("selected_quotation_id", selected_quotation_id),
        ("requested_by", requested_by),
    ]:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return _missing_param(name)

    item_id = str(item_id).strip()
    selected_quotation_id = str(selected_quotation_id).strip()
    requested_by = str(requested_by).strip()

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return {
            "error": "INVALID_PARAMETER",
            "parameter": "quantity",
            "message": "quantity must be a positive integer.",
        }

    if quantity <= 0:
        return {
            "error": "INVALID_QUANTITY",
            "message": "quantity must be greater than zero.",
            "quantity": quantity,
        }

    inventory = load_inventory()
    if item_id not in inventory:
        return {"error": "ITEM_NOT_FOUND", "item_id": item_id}

    quotes = load_quotations().get(item_id, [])
    quote = next((q for q in quotes if q["quotation_id"] == selected_quotation_id), None)
    if quote is None:
        return {
            "error": "QUOTATION_NOT_FOUND_FOR_ITEM",
            "item_id": item_id,
            "selected_quotation_id": selected_quotation_id,
        }

    if _quotation_record_invalid(quote):
        return {
            "error": "MALFORMED_QUOTATION_RECORD",
            "selected_quotation_id": selected_quotation_id,
            "message": "Quotation record is missing required fields for validation.",
        }

    if _is_quotation_expired(quote.get("quotation_valid_until")):
        return {
            "error": "QUOTATION_EXPIRED",
            "selected_quotation_id": selected_quotation_id,
            "quotation_valid_until": quote.get("quotation_valid_until"),
            "reference_date": _reference_date,
        }

    unit_price = int(quote["unit_price"])
    total = unit_price * quantity
    created_at = datetime.now(timezone.utc).isoformat()

    draft = _store.create(
        {
            "item_id": item_id,
            "quantity": quantity,
            "selected_quotation_id": selected_quotation_id,
            "supplier_name": quote["supplier_name"],
            "unit_price": unit_price,
            "total_estimated_cost": total,
            "status": "DRAFT",
            "requested_by": requested_by,
            "created_at": created_at,
        }
    )

    return {
        "requisition_id": draft["requisition_id"],
        "item_id": item_id,
        "quantity": quantity,
        "selected_quotation_id": selected_quotation_id,
        "unit_price": unit_price,
        "total_estimated_cost": total,
        "status": "DRAFT",
        "created_at": created_at,
    }


def route_requisition_for_approval(requisition_id: Optional[str] = None) -> dict[str, Any]:
    """
    Mark a DRAFT requisition as PENDING_APPROVAL and simulate routing to approver.

    Args:
        requisition_id: Identifier returned by create_requisition_draft.
    """
    if requisition_id is None or str(requisition_id).strip() == "":
        return _missing_param("requisition_id")

    requisition_id = str(requisition_id).strip()
    existing = _store.get(requisition_id)
    if existing is None:
        return {"error": "REQUISITION_NOT_FOUND", "requisition_id": requisition_id}

    if existing.get("status") != "DRAFT":
        return {
            "error": "INVALID_STATUS",
            "requisition_id": requisition_id,
            "current_status": existing.get("status"),
            "message": "Only DRAFT requisitions can be routed for approval.",
        }

    routed_at = datetime.now(timezone.utc).isoformat()
    updated = _store.update(
        requisition_id,
        {
            "status": "PENDING_APPROVAL",
            "routed_to": "Store Manager (simulated approver)",
            "routed_at": routed_at,
        },
    )
    assert updated is not None

    return {
        "requisition_id": requisition_id,
        "status": "PENDING_APPROVAL",
        "routed_to": updated["routed_to"],
        "routed_at": routed_at,
    }


def _quotation_record_invalid(quote: dict[str, Any]) -> bool:
    required = ("quotation_id", "unit_price", "quotation_valid_until")
    for field in required:
        if field not in quote or quote[field] in (None, ""):
            return True
    try:
        int(quote["unit_price"])
    except (TypeError, ValueError):
        return True
    return False


TOOL_REGISTRY: dict[str, Any] = {
    "get_supplier_quotations": get_supplier_quotations,
    "get_reorder_status": get_reorder_status,
    "create_requisition_draft": create_requisition_draft,
    "route_requisition_for_approval": route_requisition_for_approval,
}

CONFIRMATION_REQUIRED_TOOLS = frozenset({"route_requisition_for_approval"})


def dispatch_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name not in TOOL_REGISTRY:
        return {"error": "UNKNOWN_TOOL", "tool": name}
    fn = TOOL_REGISTRY[name]
    return fn(**args)
