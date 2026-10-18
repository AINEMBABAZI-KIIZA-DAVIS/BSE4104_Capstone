"""
bounded_agent.py – Week 5 Sense → Plan → Act → Observe → Stop/Re-plan loop.

Goal: prepare a DRAFT purchase requisition for one inventory item when reorder
is needed, using only the Week 4 approved tools. Routing is optional and always
human-gated.

The planner is deterministic Python (direct orchestration). Gemini is not
required to choose the next approved action. Memory hints (Week 6) may prefill
quantity and requester; they never skip validation or auto-route.

Usage:
    python src/bounded_agent.py --item ITEM-004
    python src/bounded_agent.py --item ITEM-004 --route --auto-confirm
    python src/bounded_agent.py --traces results/week5_execution_traces.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent_memory import AgentMemory
from src.agent_state import WorkflowState, new_session
from src.guardrails import APPROVED_TOOLS, assert_tool_allowed, screen_session_inputs
from src.observability import AgentTracer, get_tracer
from src.tools import (
    CONFIRMATION_REQUIRED_TOOLS,
    dispatch_tool,
    set_reference_date,
    set_store,
)

REFERENCE_DATE = "2026-09-16"


def _valid_quotes(state: WorkflowState) -> list[dict[str, Any]]:
    quotes = state.quotations or []
    excluded = set(state.excluded_quotation_ids)
    valid = []
    for q in quotes:
        qid = q.get("quotation_id")
        until = (q.get("quotation_valid_until") or "").strip()
        if not qid or qid in excluded:
            continue
        if until and until < REFERENCE_DATE:
            continue
        valid.append(q)
    return valid


def _cheapest_valid(state: WorkflowState) -> dict[str, Any] | None:
    valid = _valid_quotes(state)
    if not valid:
        return None
    return min(valid, key=lambda q: int(q["unit_price"]))


def _cheapest_candidate(state: WorkflowState) -> dict[str, Any] | None:
    """First attempt may pick an expired cheapest quote so validation can recover."""
    if state.recovery_attempts == 0:
        quotes = [
            q for q in (state.quotations or [])
            if q.get("quotation_id") and q["quotation_id"] not in state.excluded_quotation_ids
        ]
        if quotes:
            return min(quotes, key=lambda q: int(q["unit_price"]))
    return _cheapest_valid(state)


def apply_memory_hints(state: WorkflowState, memory: AgentMemory) -> WorkflowState:
    """Prefill missing requester/quantity from justified memory. Never awards."""
    hints = memory.hints_for(state.item_id)
    if hints.get("error"):
        return state

    if not state.requested_by and hints.get("default_requested_by"):
        state.requested_by = hints["default_requested_by"]
        state.memory_hints_used.append("default_requested_by")

    if state.quantity is None and hints.get("last_quantity"):
        state.quantity = int(hints["last_quantity"])
        state.memory_hints_used.append("last_quantity")

    if hints.get("last_quotation_id"):
        state.memory_hints_used.append("last_quotation_id_hint_only")
    return state


def plan_next_action(state: WorkflowState) -> dict[str, Any]:
    """Choose the next approved action or a stop reason."""
    if not state.item_id:
        return {"type": "stop", "reason": "MISSING_ITEM_ID"}

    if state.iteration >= state.max_iterations:
        return {"type": "stop", "reason": "MAX_ITERATIONS"}

    if state.recovery_attempts > state.max_recoveries:
        return {"type": "stop", "reason": "RECOVERY_EXHAUSTED"}

    if state.reorder is None:
        return {"type": "act", "tool": "get_reorder_status", "args": {"item_id": state.item_id}}

    if state.reorder.get("error") == "ITEM_NOT_FOUND":
        return {"type": "stop", "reason": "ITEM_NOT_FOUND"}

    if not state.reorder.get("needs_reorder"):
        return {"type": "stop", "reason": "NO_REORDER_NEEDED"}

    if state.quotations is None:
        return {"type": "act", "tool": "get_supplier_quotations", "args": {"item_id": state.item_id}}

    if not state.quotations:
        return {"type": "stop", "reason": "NO_QUOTATIONS"}

    chosen = _cheapest_candidate(state)
    if chosen is None:
        return {"type": "stop", "reason": "NO_VALID_QUOTATION"}

    if not state.requisition_id:
        quantity = state.quantity
        if quantity is None:
            deficit = state.reorder.get("replenishment_deficit")
            quantity = int(deficit) if deficit else None
        if not quantity or quantity <= 0:
            return {"type": "stop", "reason": "TOOL_ERROR"}
        if not state.requested_by:
            return {"type": "stop", "reason": "TOOL_ERROR"}
        return {
            "type": "act",
            "tool": "create_requisition_draft",
            "args": {
                "item_id": state.item_id,
                "quantity": int(quantity),
                "selected_quotation_id": chosen["quotation_id"],
                "requested_by": state.requested_by,
            },
        }

    if state.wants_routing and state.requisition_status == "DRAFT":
        return {
            "type": "act",
            "tool": "route_requisition_for_approval",
            "args": {"requisition_id": state.requisition_id},
        }

    return {"type": "stop", "reason": "GOAL_COMPLETE"}


def observe(state: WorkflowState, tool: str, result: dict[str, Any]) -> WorkflowState:
    state.last_tool = tool
    state.last_result = result
    state.last_error = result.get("error") if isinstance(result, dict) else None
    state.phase = "OBSERVE"

    if not isinstance(result, dict):
        state.recovery_attempts += 1
        return state

    error = result.get("error")
    if error == "HUMAN_DECLINED":
        state.stop_reason = "HUMAN_DECLINED"
        state.outcome = "HANDED_OFF"
        state.phase = "STOP"
        return state

    if error == "ITEM_NOT_FOUND":
        state.reorder = result
        return state

    if error == "QUOTATION_EXPIRED":
        qid = result.get("selected_quotation_id")
        if qid and qid not in state.excluded_quotation_ids:
            state.excluded_quotation_ids.append(qid)
        state.selected_quotation_id = None
        state.recovery_attempts += 1
        return state

    if error:
        state.recovery_attempts += 1
        return state

    if tool == "get_reorder_status":
        state.reorder = result
        if state.quantity is None and result.get("needs_reorder"):
            deficit = result.get("replenishment_deficit")
            if deficit:
                state.quantity = int(deficit)

    elif tool == "get_supplier_quotations":
        state.quotations = result.get("quotations") or []

    elif tool == "create_requisition_draft":
        state.requisition_id = result.get("requisition_id")
        state.requisition_status = result.get("status")
        state.selected_quotation_id = result.get("selected_quotation_id")
        if result.get("quantity"):
            state.quantity = int(result["quantity"])

    elif tool == "route_requisition_for_approval":
        state.requisition_status = result.get("status")

    return state


def _confirm_default(tool: str, args: dict[str, Any], auto_confirm: bool) -> bool:
    print("\n" + "=" * 70)
    print("HUMAN APPROVAL REQUIRED — higher-impact tool staged")
    print(f"  Tool: {tool}")
    print(f"  Arguments: {json.dumps(args, indent=2)}")
    print("=" * 70)
    if auto_confirm:
        print("[demo] Auto-confirmed by operator.")
        return True
    answer = input("Execute this tool? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def run_bounded_agent(
    *,
    item_id: str | None,
    requested_by: str | None = None,
    quantity: int | None = None,
    wants_routing: bool = False,
    auto_confirm: bool = False,
    confirm_callback: Callable[[str, dict[str, Any]], bool] | None = None,
    memory: AgentMemory | None = None,
    persist_memory: bool = True,
    user_text: str | None = None,
    role: str = "procurement_officer",
    tracer: AgentTracer | None = None,
) -> tuple[WorkflowState, list[str]]:
    """Run one bounded prepare-requisition workflow."""
    set_reference_date(REFERENCE_DATE)
    mem = memory or AgentMemory()
    log = tracer or get_tracer()
    state = new_session(
        item_id=item_id,
        requested_by=requested_by,
        quantity=quantity,
        wants_routing=wants_routing,
    )
    transcript: list[str] = [
        f"session={state.session_id}",
        f"goal={state.goal}",
        f"item={item_id} requested_by={requested_by} quantity={quantity} route={wants_routing}",
    ]

    state.phase = "SENSE"
    screen = screen_session_inputs(
        item_id=item_id,
        requested_by=requested_by,
        quantity=quantity,
        user_text=user_text,
        role=role,
    )
    if not screen.allowed:
        state.phase = "STOP"
        state.stop_reason = screen.reason
        state.outcome = "FAILED"
        transcript.append(f"[GUARDRAIL] {screen.reason}: {screen.message}")
        log.emit({
            "session_id": state.session_id,
            "phase": "SENSE",
            "event": "guardrail_block",
            "stop_reason": screen.reason,
            "message": screen.message,
        })
        return state, transcript

    state = apply_memory_hints(state, mem)
    if state.memory_hints_used:
        transcript.append(f"[SENSE] memory hints applied: {state.memory_hints_used}")
    else:
        transcript.append("[SENSE] no memory hints applied")

    confirm_fn = confirm_callback or (
        lambda name, args: _confirm_default(name, args, auto_confirm)
    )

    while state.phase != "STOP":
        state.phase = "PLAN"
        state.iteration += 1
        decision = plan_next_action(state)
        transcript.append(f"\n--- iteration {state.iteration} PLAN ---")
        transcript.append(json.dumps(decision))

        if decision["type"] == "stop":
            state.phase = "STOP"
            state.stop_reason = decision["reason"]
            if decision["reason"] == "GOAL_COMPLETE":
                state.outcome = "SUCCESS"
            elif decision["reason"] in ("NO_REORDER_NEEDED", "HUMAN_DECLINED"):
                state.outcome = "STOPPED" if decision["reason"] == "NO_REORDER_NEEDED" else "HANDED_OFF"
            else:
                state.outcome = "FAILED"
            transcript.append(f"[STOP] {state.stop_reason} outcome={state.outcome}")
            break

        tool = decision["tool"]
        args = decision["args"]
        allow = assert_tool_allowed(tool)
        if not allow.allowed:
            state.phase = "STOP"
            state.stop_reason = "UNKNOWN_TOOL"
            state.outcome = "FAILED"
            transcript.append(f"[STOP] planner proposed unapproved tool {tool}")
            break

        state.phase = "ACT"
        transcript.append(f"[ACT] {tool}({json.dumps(args)})")

        with log.span(session_id=state.session_id, phase="ACT", tool=tool, args=args):
            if tool in CONFIRMATION_REQUIRED_TOOLS:
                if not confirm_fn(tool, args):
                    result = {
                        "error": "HUMAN_DECLINED",
                        "message": "Human reviewer declined to execute this tool.",
                    }
                    transcript.append("[SKIPPED] human declined")
                else:
                    result = dispatch_tool(tool, args)
                    transcript.append(f"[OBSERVE] {json.dumps(result, indent=2)}")
            else:
                result = dispatch_tool(tool, args)
                transcript.append(f"[OBSERVE] {json.dumps(result, indent=2)}")

        state = observe(state, tool, result)
        if state.phase == "STOP":
            transcript.append(f"[STOP] {state.stop_reason} outcome={state.outcome}")
            break

    if (
        persist_memory
        and state.outcome == "SUCCESS"
        and state.item_id
        and state.requisition_id
        and state.selected_quotation_id
        and state.quantity
        and state.requested_by
    ):
        mem.record_preparation(
            item_id=state.item_id,
            quantity=state.quantity,
            quotation_id=state.selected_quotation_id,
            requisition_id=state.requisition_id,
            requested_by=state.requested_by,
        )
        transcript.append("[MEMORY] recorded successful preparation")

    log.emit({
        "session_id": state.session_id,
        "phase": "STOP",
        "event": "session_end",
        "stop_reason": state.stop_reason,
        "outcome": state.outcome,
        "iterations": state.iteration,
        "item_id": state.item_id,
        "requisition_id": state.requisition_id,
    })
    return state, transcript


def parse_item_from_text(text: str) -> str | None:
    match = re.search(r"ITEM-\d{3}", text.upper())
    return match.group(0) if match else None


def write_traces(path: Path, traces: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blocks = [
        "# ProcurePrep UG – Week 5 Execution Traces",
        "",
        f"**Date:** {datetime.now().isoformat(timespec='seconds')}  ",
        "**Workflow:** Sense → Plan → Act → Observe → Stop / Re-plan  ",
        "**Goal:** Prepare a DRAFT requisition for one inventory item when reorder is needed.  ",
        "",
        "Three traces are required: a successful multi-step run, an early safe stop, and a failure/recovery case.",
        "",
    ]
    for i, t in enumerate(traces, 1):
        blocks.append(f"## Trace {i}: {t['title']}")
        blocks.append("")
        blocks.append(t["summary"])
        blocks.append("")
        blocks.append("```")
        blocks.append("\n".join(t["transcript"]))
        blocks.append("```")
        blocks.append("")
        blocks.append(f"**Stop reason:** `{t['state'].stop_reason}`  ")
        blocks.append(f"**Outcome:** `{t['state'].outcome}`  ")
        blocks.append(f"**Iterations:** {t['state'].iteration}  ")
        blocks.append("")
    path.write_text("\n".join(blocks), encoding="utf-8")


def run_required_traces(out_path: Path, memory: AgentMemory) -> list[dict[str, Any]]:
    from src.requisition_store import RequisitionStore
    import tempfile

    tmp = tempfile.TemporaryDirectory()
    set_store(RequisitionStore(Path(tmp.name) / "requisitions.json"))

    traces: list[dict[str, Any]] = []

    state, transcript = run_bounded_agent(
        item_id="ITEM-004",
        requested_by="Jane Okello",
        wants_routing=False,
        memory=memory,
        persist_memory=True,
    )
    traces.append({
        "title": "Successful multi-step preparation (ITEM-004)",
        "summary": "Agent senses a named item, checks reorder, retrieves quotes, drafts on the cheapest valid quotation (Q-107), and stops without routing.",
        "state": state,
        "transcript": transcript,
    })

    state, transcript = run_bounded_agent(
        item_id="ITEM-002",
        requested_by="Jane Okello",
        memory=memory,
        persist_memory=False,
    )
    traces.append({
        "title": "Safe early stop — sufficient stock (ITEM-002)",
        "summary": "Agent checks reorder status, observes stock above threshold, and stops. No quotations are fetched and no draft is created.",
        "state": state,
        "transcript": transcript,
    })

    state, transcript = run_bounded_agent(
        item_id="ITEM-005",
        requested_by="Jane Okello",
        memory=memory,
        persist_memory=True,
    )
    traces.append({
        "title": "Failure and recovery — expired cheapest quote (ITEM-005)",
        "summary": "Q-109 is cheaper but expired on 2026-08-15. If the draft tool rejects it, the observer excludes that quotation and the planner re-plans onto Q-110. If the planner already filters expired quotes, the first draft uses Q-110 and recovery is preventive.",
        "state": state,
        "transcript": transcript,
    })

    tmp.cleanup()
    write_traces(out_path, traces)
    return traces


def main() -> None:
    parser = argparse.ArgumentParser(description="ProcurePrep Week 5 bounded agent")
    parser.add_argument("--item", default=None, help="Inventory item ID (e.g. ITEM-004)")
    parser.add_argument("--requested-by", default=None)
    parser.add_argument("--quantity", type=int, default=None)
    parser.add_argument("--route", action="store_true", help="Ask to route after draft")
    parser.add_argument("--auto-confirm", action="store_true")
    parser.add_argument("--traces", default=None, help="Write the three required traces to this markdown file")
    args = parser.parse_args()

    if args.traces:
        memory = AgentMemory()
        traces = run_required_traces(Path(args.traces), memory)
        print(f"Wrote {args.traces}")
        for t in traces:
            print(f"  {t['title']}: {t['state'].stop_reason} / {t['state'].outcome}")
        return

    if not args.item:
        parser.error("Provide --item or --traces")

    state, transcript = run_bounded_agent(
        item_id=args.item,
        requested_by=args.requested_by,
        quantity=args.quantity,
        wants_routing=args.route,
        auto_confirm=args.auto_confirm,
    )
    print("\n".join(transcript))
    print("\nFINAL STATE")
    print(json.dumps({
        "session_id": state.session_id,
        "stop_reason": state.stop_reason,
        "outcome": state.outcome,
        "iterations": state.iteration,
        "requisition_id": state.requisition_id,
        "selected_quotation_id": state.selected_quotation_id,
        "memory_hints_used": state.memory_hints_used,
    }, indent=2))


if __name__ == "__main__":
    main()
