"""
Justified persistent memory for ProcurePrep (Week 6).

Stores officer preferences and prior preparation results so a later run can
prefill quantity / requester. Memory never awards a supplier, never skips the
reorder check, and never routes a requisition.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MEMORY_PATH = PROJECT_ROOT / "data" / "agent_memory.json"
ALLOWED_ROLES = frozenset({"procurement_officer", "store_manager"})
DEFAULT_RETENTION_DAYS = 90

_lock = threading.Lock()


def _empty_store() -> dict[str, Any]:
    return {
        "version": 1,
        "preferences": {
            "default_requested_by": "Jane Okello",
            "prefer_cheapest_valid": True,
        },
        "item_history": {},
        "access": {
            "roles": sorted(ALLOWED_ROLES),
            "retention_days": DEFAULT_RETENTION_DAYS,
            "purpose": "Prefill requester and last quantity for a known item. Not a decision record.",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


class AgentMemory:
    def __init__(self, path: Path | str | None = None, *, role: str = "procurement_officer"):
        self.path = Path(path) if path else DEFAULT_MEMORY_PATH
        self.role = role

    def _authorized(self) -> bool:
        return self.role in ALLOWED_ROLES

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_store()
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _prune(self, data: dict[str, Any]) -> dict[str, Any]:
        days = int(data.get("access", {}).get("retention_days", DEFAULT_RETENTION_DAYS))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        kept: dict[str, Any] = {}
        for item_id, rec in data.get("item_history", {}).items():
            stamp = rec.get("last_prepared_at")
            if not stamp:
                continue
            try:
                prepared = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if prepared >= cutoff:
                kept[item_id] = rec
        data["item_history"] = kept
        return data

    def hints_for(self, item_id: str | None) -> dict[str, Any]:
        """Return prefill hints. Empty if unauthorized or no history."""
        if not self._authorized():
            return {"error": "MEMORY_FORBIDDEN", "role": self.role}

        with _lock:
            data = self._prune(self._load())
            prefs = data.get("preferences", {})
            history = data.get("item_history", {}).get(item_id or "", {})
            return {
                "default_requested_by": prefs.get("default_requested_by"),
                "prefer_cheapest_valid": bool(prefs.get("prefer_cheapest_valid", True)),
                "last_quantity": history.get("last_quantity"),
                "last_quotation_id": history.get("last_quotation_id"),
                "last_requisition_id": history.get("last_requisition_id"),
                "times_prepared": history.get("times_prepared", 0),
            }

    def record_preparation(
        self,
        *,
        item_id: str,
        quantity: int,
        quotation_id: str,
        requisition_id: str,
        requested_by: str,
    ) -> dict[str, Any]:
        if not self._authorized():
            return {"error": "MEMORY_FORBIDDEN", "role": self.role}

        with _lock:
            data = self._prune(self._load())
            prev = data["item_history"].get(item_id, {})
            data["item_history"][item_id] = {
                "last_quantity": quantity,
                "last_quotation_id": quotation_id,
                "last_requisition_id": requisition_id,
                "last_requested_by": requested_by,
                "last_prepared_at": datetime.now(timezone.utc).isoformat(),
                "times_prepared": int(prev.get("times_prepared", 0)) + 1,
            }
            self._save(data)
            return data["item_history"][item_id]

    def delete_item(self, item_id: str) -> bool:
        if not self._authorized():
            return False
        with _lock:
            data = self._load()
            existed = item_id in data.get("item_history", {})
            data.get("item_history", {}).pop(item_id, None)
            self._save(data)
            return existed

    def clear(self) -> None:
        if not self._authorized():
            return
        with _lock:
            self._save(_empty_store())
