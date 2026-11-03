"""Shared CSV data access for ProcurePrep operational data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY_PATH = PROJECT_ROOT / "data" / "inventory.csv"
DEFAULT_QUOTATIONS_PATH = PROJECT_ROOT / "data" / "quotations.csv"
REFERENCE_DATE_DEFAULT = "2026-09-16"
ACTIVE_INVENTORY_PATH: Path | None = None
ACTIVE_QUOTATIONS_PATH: Path | None = None


def set_inventory_path(path: Path | str | None) -> Path:
    global ACTIVE_INVENTORY_PATH
    ACTIVE_INVENTORY_PATH = Path(path) if path is not None else DEFAULT_INVENTORY_PATH
    return ACTIVE_INVENTORY_PATH


def reset_inventory_path() -> Path:
    global ACTIVE_INVENTORY_PATH
    ACTIVE_INVENTORY_PATH = DEFAULT_INVENTORY_PATH
    return ACTIVE_INVENTORY_PATH


def set_quotations_path(path: Path | str | None) -> Path:
    global ACTIVE_QUOTATIONS_PATH
    ACTIVE_QUOTATIONS_PATH = Path(path) if path is not None else DEFAULT_QUOTATIONS_PATH
    return ACTIVE_QUOTATIONS_PATH


def reset_quotations_path() -> Path:
    global ACTIVE_QUOTATIONS_PATH
    ACTIVE_QUOTATIONS_PATH = DEFAULT_QUOTATIONS_PATH
    return ACTIVE_QUOTATIONS_PATH


def _normalize_csv_key(value: str | None) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_quotation_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if key is None:
            continue
        normalized[_normalize_csv_key(key)] = value

    quote_id = (
        normalized.get("quotation_id")
        or normalized.get("quote_id")
        or normalized.get("id")
        or normalized.get("quotation_no")
        or ""
    )
    item_id = (
        normalized.get("item_id")
        or normalized.get("item")
        or normalized.get("sku")
        or ""
    )
    supplier_name = (
        normalized.get("supplier_name")
        or normalized.get("supplier")
        or normalized.get("vendor_name")
        or normalized.get("vendor")
        or "Unknown supplier"
    )
    unit_price = (
        normalized.get("unit_price")
        or normalized.get("price")
        or normalized.get("price_ugx")
        or normalized.get("unit_price_ugx")
        or ""
    )
    quantity_available = (
        normalized.get("quantity_available")
        or normalized.get("available_quantity")
        or normalized.get("quantity")
        or normalized.get("available_qty")
        or ""
    )
    delivery_terms = (
        normalized.get("delivery_terms")
        or normalized.get("delivery")
        or normalized.get("delivery_method")
        or normalized.get("lead_time")
        or ""
    )
    quotation_valid_until = (
        normalized.get("quotation_valid_until")
        or normalized.get("valid_until")
        or normalized.get("quote_valid_until")
        or normalized.get("expiry_date")
        or normalized.get("expires_on")
        or ""
    )
    notes = normalized.get("notes") or normalized.get("remarks") or normalized.get("comments") or ""

    return {
        "quotation_id": str(quote_id).strip(),
        "item_id": str(item_id).strip(),
        "supplier_name": str(supplier_name).strip(),
        "unit_price": str(unit_price).strip(),
        "quantity_available": str(quantity_available).strip(),
        "delivery_terms": str(delivery_terms).strip(),
        "quotation_valid_until": str(quotation_valid_until).strip(),
        "notes": str(notes).strip(),
    }


def load_inventory(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    filepath = Path(path) if path is not None else (ACTIVE_INVENTORY_PATH or DEFAULT_INVENTORY_PATH)
    items: dict[str, dict[str, Any]] = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["current_stock"] = float(row["current_stock"])
            row["reorder_threshold"] = float(row["reorder_threshold"])
            items[row["item_id"]] = row
    return items


def load_quotations(path: Path | str | None = None) -> dict[str, list[dict[str, Any]]]:
    filepath = Path(path) if path is not None else (ACTIVE_QUOTATIONS_PATH or DEFAULT_QUOTATIONS_PATH)
    quotes_by_item: dict[str, list[dict[str, Any]]] = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            normalized_row = _normalize_quotation_row(row)
            item_id = normalized_row.get("item_id", "").strip()
            quotation_id = normalized_row.get("quotation_id", "").strip()
            if not item_id or not quotation_id:
                continue
            quotes_by_item.setdefault(item_id, []).append(normalized_row)
    return quotes_by_item


def check_reorder_need(current_stock: float, reorder_threshold: float) -> bool:
    return current_stock < reorder_threshold
