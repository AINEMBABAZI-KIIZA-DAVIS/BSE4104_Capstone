#!/usr/bin/env python3
"""Run the Week 7 32-scenario evaluation set and write results markdown."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.scenarios import SCENARIOS
from src.agent_memory import AgentMemory
from src.bounded_agent import run_bounded_agent
from src.mcp_interface import call_mcp_tool
from src.observability import AgentTracer
from src.requisition_store import RequisitionStore
from src.tools import set_reference_date, set_store


def _match(actual: dict, expect: dict) -> bool:
    for key, value in expect.items():
        if actual.get(key) != value:
            return False
    return True


def _run_one(scenario: dict, memory: AgentMemory, tracer: AgentTracer) -> dict:
    mode = scenario["mode"]
    started = time.perf_counter()
    actual: dict = {}

    if mode == "agent":
        state, _ = run_bounded_agent(
            item_id=scenario.get("item_id"),
            requested_by=scenario.get("requested_by"),
            quantity=scenario.get("quantity"),
            wants_routing=bool(scenario.get("wants_routing")),
            confirm_callback=(lambda n, a: bool(scenario.get("confirm"))) if "confirm" in scenario else None,
            memory=memory,
            persist_memory=False,
            user_text=scenario.get("user_text"),
            role=scenario.get("role", "procurement_officer"),
            tracer=tracer,
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
    passed = _match(actual, scenario["expect"])
    return {
        "id": scenario["id"],
        "category": scenario["category"],
        "mode": mode,
        "passed": passed,
        "expect": scenario["expect"],
        "actual": actual,
        "latency_ms": latency_ms,
    }


def main() -> None:
    tmp = tempfile.TemporaryDirectory()
    set_store(RequisitionStore(Path(tmp.name) / "requisitions.json"))
    set_reference_date("2026-09-16")
    memory = AgentMemory(Path(tmp.name) / "memory.json")
    tracer = AgentTracer(PROJECT_ROOT / "results" / "traces" / "week7_eval.jsonl")
    if tracer.path.exists():
        tracer.path.unlink()

    rows = [_run_one(s, memory, tracer) for s in SCENARIOS]
    passed = sum(1 for r in rows if r["passed"])
    failed = [r for r in rows if not r["passed"]]
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)

    lines = [
        "# ProcurePrep UG – Week 7 Evaluation Results",
        "",
        f"**Date:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**Scenarios:** {len(rows)}  ",
        f"**Passed:** {passed} / {len(rows)}  ",
        f"**Trace log:** `results/traces/week7_eval.jsonl`",
        "",
        "## Criteria",
        "",
        "| Criterion | How it is scored |",
        "| :--- | :--- |",
        "| Task completion | Agent reaches the expected stop reason / outcome |",
        "| Tool selection | Only allow-listed tools run; unknown names fail closed |",
        "| Instruction following | Injection and award/payment overrides are blocked |",
        "| Safety violations | Unauthorized roles and unconfirmed routing are rejected |",
        "| Latency | Wall time per scenario recorded in milliseconds |",
        "",
        "## Results by category",
        "",
        "| Category | Pass | Total |",
        "| :--- | ---: | ---: |",
    ]
    for cat, items in by_cat.items():
        lines.append(f"| {cat} | {sum(1 for i in items if i['passed'])} | {len(items)} |")

    lines.extend(["", "## Scenario table", "", "| ID | Category | Expected | Actual | Latency (ms) | Result |", "| :--- | :--- | :--- | :--- | ---: | :--- |"])
    for r in rows:
        exp = json.dumps(r["expect"])
        act = json.dumps({k: r["actual"].get(k) for k in r["expect"]})
        mark = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['id']} | {r['category']} | `{exp}` | `{act}` | {r['latency_ms']} | **{mark}** |")

    if failed:
        lines.extend(["", "## Failed scenarios", ""])
        for r in failed:
            lines.append(f"- **{r['id']}** expected `{r['expect']}` got `{r['actual']}`")
    else:
        lines.extend(["", "No failed scenarios in this run.", ""])

    out = PROJECT_ROOT / "results" / "week7_evaluation.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{passed}/{len(rows)} passed")
    print(f"Wrote {out}")
    tmp.cleanup()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
