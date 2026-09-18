"""Shared CSV data access for ProcurePrep operational data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY_PATH = PROJECT_ROOT / "data" / "inventory.csv"
DEFAULT_QUOTATIONS_PATH = PROJECT_ROOT / "data" / "quotations.csv"
REFERENCE_DATE_DEFAULT = "2026-09-16"


def load_inventory(path: Path | str | None = None) -> dict[str, dict[str, Any]]:
    filepath = Path(path) if path else DEFAULT_INVENTORY_PATH
    items: dict[str, dict[str, Any]] = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["current_stock"] = float(row["current_stock"])
            row["reorder_threshold"] = float(row["reorder_threshold"])
            items[row["item_id"]] = row
    return items


def load_quotations(path: Path | str | None = None) -> dict[str, list[dict[str, Any]]]:
    filepath = Path(path) if path else DEFAULT_QUOTATIONS_PATH
    quotes_by_item: dict[str, list[dict[str, Any]]] = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            item_id = row["item_id"]
            quotes_by_item.setdefault(item_id, []).append(row)
    return quotes_by_item


def check_reorder_need(current_stock: float, reorder_threshold: float) -> bool:
    return current_stock < reorder_threshold
