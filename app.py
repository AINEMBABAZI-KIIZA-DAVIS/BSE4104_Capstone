from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import settings
from evaluation.scenarios import SCENARIOS
from src.agent_memory import AgentMemory
from src.bounded_agent import run_bounded_agent
from src.mcp_interface import call_mcp_tool
from src.procure_data import load_inventory, reset_inventory_path, set_inventory_path
from src.requisition_store import RequisitionStore
from src.tools import (
    create_requisition_draft,
    get_reorder_status,
    get_supplier_quotations,
    route_requisition_for_approval,
    set_reference_date,
    set_store,
)

DEMO_USERS = [
    {"id": "u-101", "name": "Jane Okello", "role": "procurement_officer", "department": "Procurement"},
    {"id": "u-102", "name": "Peter Nsubuga", "role": "store_manager", "department": "Stores"},
    {"id": "u-103", "name": "Sarah Nakato", "role": "vendor", "department": "Suppliers"},
    {"id": "u-104", "name": "Daniel Kintu", "role": "procurement_officer", "department": "Operations"},
]

DEMO_USER_BY_ID = {user["id"]: user for user in DEMO_USERS}

app = FastAPI(
    title="ProcurePrep UG API",
    description="Deterministic procurement preparation API for the demo dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _match_expectation(actual: dict[str, Any], expect: dict[str, Any]) -> bool:
    for key, value in expect.items():
        if actual.get(key) != value:
            return False
    return True


def _run_one_evaluation_scenario(scenario: dict[str, Any], memory: AgentMemory) -> dict[str, Any]:
    mode = scenario["mode"]
    started = time.perf_counter()
    actual: dict[str, Any] = {}

    if mode == "agent":
        state, _ = run_bounded_agent(
            item_id=scenario.get("item_id"),
            requested_by=scenario.get("requested_by"),
            quantity=scenario.get("quantity"),
            wants_routing=bool(scenario.get("wants_routing")),
            confirm_callback=(lambda _n, _a: bool(scenario.get("confirm"))) if "confirm" in scenario else None,
            memory=memory,
            persist_memory=False,
            user_text=scenario.get("user_text"),
            role=scenario.get("role", "procurement_officer"),
            tracer=None,
        )
        actual = {
            "stop_reason": state.stop_reason,
            "outcome": state.outcome,
            "selected_quotation_id": state.selected_quotation_id,
            "quantity": state.quantity,
            "requisition_status": state.requisition_status,
            "iterations": state.iteration,
        }
    elif mode == "mcp":
        result = call_mcp_tool(
            scenario["tool"],
            scenario.get("args") or {},
            role=scenario.get("role", "procurement_officer"),
            confirmed=bool(scenario.get("confirmed")),
        )
        actual = {"error": result.get("error"), "status": result.get("status")}
        if result.get("error") is None:
            actual["error"] = None
    elif mode == "memory":
        locked = AgentMemory(memory.path, role=scenario.get("role", "visitor"))
        hints = locked.hints_for("ITEM-004")
        actual = {"error": hints.get("error")}
    else:
        actual = {"error": "UNKNOWN_MODE"}

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "mode": mode,
        "passed": _match_expectation(actual, scenario["expect"]),
        "expect": scenario["expect"],
        "actual": actual,
        "latency_ms": latency_ms,
    }


class DraftRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    selected_quotation_id: str = Field(..., min_length=1)
    requested_by: str = Field(..., min_length=1)
    requested_by_user_id: str | None = None


class ApprovalRequest(BaseModel):
    approved_by_user_id: str = Field(..., min_length=1)
    approved_by_role: str | None = None


class InventoryUploadResponse(BaseModel):
    status: str
    items_loaded: int
    message: str


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "ProcurePrep UG API"}


@app.get("/api/evaluation")
def live_evaluation() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        set_store(RequisitionStore(Path(tmpdir) / "requisitions.json"))
        set_reference_date("2026-09-16")
        memory = AgentMemory(Path(tmpdir) / "memory.json")
        rows = [_run_one_evaluation_scenario(scenario, memory) for scenario in SCENARIOS]

    passed = sum(1 for row in rows if row["passed"])
    by_category: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_category.setdefault(row["category"], {"passed": 0, "total": 0})
        bucket["total"] += 1
        if row["passed"]:
            bucket["passed"] += 1

    return {
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "rows": rows,
        "by_category": by_category,
    }


@app.get("/api/demo-users")
def demo_users() -> dict[str, Any]:
    return {"users": DEMO_USERS}


@app.post("/api/inventory/upload")
async def upload_inventory(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail={"error": "INVALID_FILE", "message": "Please upload a CSV file."})

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail={"error": "EMPTY_FILE", "message": "The uploaded file is empty."})

    try:
        csv_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ENCODING", "message": "CSV must be UTF-8 encoded."})

    try:
        tmp_path = Path(tempfile.gettempdir()) / f"procureprep_uploaded_{abs(hash(file.filename))}.csv"
        tmp_path.write_text(csv_text, encoding="utf-8")
        items = load_inventory(tmp_path)
    except Exception as exc:  # pragma: no cover - defensive guard while uploading data
        raise HTTPException(status_code=400, detail={"error": "INVALID_CSV", "message": f"Could not read the uploaded inventory: {exc}"}) from exc

    if not items:
        raise HTTPException(status_code=400, detail={"error": "NO_ITEMS", "message": "The uploaded CSV contains no inventory rows."})

    set_inventory_path(tmp_path)
    return {
        "status": "uploaded",
        "items_loaded": len(items),
        "source": str(tmp_path),
        "message": "Inventory uploaded and now active for checks.",
    }


@app.post("/api/inventory/reset")
def reset_inventory() -> dict[str, Any]:
    reset_inventory_path()
    return {"status": "reset", "message": "Inventory reset to the default demo dataset."}


@app.get("/api/items")
def list_items() -> dict[str, Any]:
    inventory = load_inventory()
    items = [
        {
            "item_id": item_id,
            "item_name": item["item_name"],
            "category": item.get("category", ""),
            "current_stock": float(item["current_stock"]),
            "reorder_threshold": float(item["reorder_threshold"]),
            "unit": item.get("unit", ""),
        }
        for item_id, item in sorted(inventory.items())
    ]
    return {"items": items}


@app.get("/api/items/{item_id}/status")
def item_status(item_id: str) -> dict[str, Any]:
    payload = get_reorder_status(item_id)
    if "error" in payload:
        raise HTTPException(status_code=404, detail=payload)
    return payload


@app.get("/api/items/{item_id}/quotes")
def item_quotes(item_id: str) -> dict[str, Any]:
    payload = get_supplier_quotations(item_id)
    if "error" in payload:
        raise HTTPException(status_code=404, detail=payload)
    return payload


@app.post("/api/requisitions/draft")
def create_draft_endpoint(payload: DraftRequest) -> dict[str, Any]:
    if payload.requested_by_user_id:
        user = DEMO_USER_BY_ID.get(payload.requested_by_user_id)
        if user is None:
            raise HTTPException(status_code=400, detail={"error": "UNKNOWN_DEMO_USER", "message": "Requested user is not available in the demo system."})
        if user["role"] not in {"procurement_officer", "store_manager"}:
            raise HTTPException(status_code=400, detail={"error": "UNAUTHORIZED_DEMO_USER", "message": "This demo account is not allowed to create requisitions."})

    result = create_requisition_draft(
        item_id=payload.item_id,
        quantity=payload.quantity,
        selected_quotation_id=payload.selected_quotation_id,
        requested_by=payload.requested_by,
    )
    if "error" in result:
        status_code = 400 if result.get("error") not in {"ITEM_NOT_FOUND"} else 404
        raise HTTPException(status_code=status_code, detail=result)
    return result


@app.post("/api/requisitions/{requisition_id}/approve")
def approve_requisition(requisition_id: str, payload: ApprovalRequest) -> dict[str, Any]:
    user = DEMO_USER_BY_ID.get(payload.approved_by_user_id)
    if user is None:
        return JSONResponse(
            status_code=400,
            content={"error": "UNKNOWN_DEMO_USER", "message": "Approval requires a valid demo user."},
        )

    role = payload.approved_by_role or user["role"]
    if role not in {"procurement_officer", "store_manager"}:
        return JSONResponse(
            status_code=400,
            content={"error": "UNAUTHORIZED_APPROVER", "message": "Only procurement or store roles may approve a draft requisition in demo mode."},
        )

    result = route_requisition_for_approval(requisition_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return {
        **result,
        "approved_by_user_id": payload.approved_by_user_id,
        "approved_by_name": user["name"],
        "approved_by_role": role,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
