"""Local persistence for purchase requisition drafts."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORE_PATH = PROJECT_ROOT / "data" / "requisitions.json"

_lock = threading.Lock()


class RequisitionStore:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_STORE_PATH

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"requisitions": {}, "next_seq": 1}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create(self, record: dict[str, Any]) -> dict[str, Any]:
        with _lock:
            data = self._load()
            seq = data.get("next_seq", 1)
            requisition_id = record.get("requisition_id") or _make_requisition_id(seq)
            record = {**record, "requisition_id": requisition_id}
            data.setdefault("requisitions", {})[requisition_id] = record
            data["next_seq"] = seq + 1
            self._save(data)
            return record

    def get(self, requisition_id: str) -> dict[str, Any] | None:
        with _lock:
            data = self._load()
            return data.get("requisitions", {}).get(requisition_id)

    def update(self, requisition_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with _lock:
            data = self._load()
            reqs = data.setdefault("requisitions", {})
            if requisition_id not in reqs:
                return None
            reqs[requisition_id] = {**reqs[requisition_id], **updates}
            self._save(data)
            return reqs[requisition_id]


def _make_requisition_id(seq: int) -> str:
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"REQ-{day}-{seq:04d}"
