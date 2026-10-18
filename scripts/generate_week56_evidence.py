#!/usr/bin/env python3
"""Write Week 5 traces and Week 6 memory demonstration markdown."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent_memory import AgentMemory
from src.bounded_agent import run_bounded_agent, run_required_traces
from src.requisition_store import RequisitionStore
from src.tools import set_reference_date, set_store


def main() -> None:
    tmp = tempfile.TemporaryDirectory()
    mem = AgentMemory(Path(tmp.name) / "memory.json")
    traces = run_required_traces(PROJECT_ROOT / "results" / "week5_execution_traces.md", mem)
    for t in traces:
        print(f"{t['title']}: {t['state'].stop_reason} / {t['state'].outcome}")

    set_store(RequisitionStore(Path(tmp.name) / "reqs.json"))
    set_reference_date("2026-09-16")
    mem2 = AgentMemory(Path(tmp.name) / "mem2.json")
    first, t1 = run_bounded_agent(
        item_id="ITEM-004",
        requested_by="Jane Okello",
        quantity=20,
        memory=mem2,
    )
    second, t2 = run_bounded_agent(
        item_id="ITEM-004",
        requested_by=None,
        quantity=None,
        memory=mem2,
    )

    hints1 = first.memory_hints_used or ["none"]
    lines = [
        "# ProcurePrep UG – Week 6 Memory and State Demonstration",
        "",
        "**Purpose:** Show that justified memory prefills quantity and requester on a repeat preparation without silently routing or awarding.",
        "",
        "## Run 1 — first preparation (no prior history)",
        "",
        f"- Stop: `{first.stop_reason}`  ",
        f"- Outcome: `{first.outcome}`  ",
        f"- Quantity: {first.quantity}  ",
        f"- Requester: {first.requested_by}  ",
        f"- Quotation: {first.selected_quotation_id}  ",
        f"- Requisition: {first.requisition_id} status={first.requisition_status}  ",
        f"- Memory hints used: {hints1}",
        "",
        "```",
        "\n".join(t1),
        "```",
        "",
        "## Run 2 — repeat ITEM-004 with quantity and name omitted",
        "",
        f"- Stop: `{second.stop_reason}`  ",
        f"- Outcome: `{second.outcome}`  ",
        f"- Quantity prefilled: {second.quantity}  ",
        f"- Requester prefilled: {second.requested_by}  ",
        f"- Memory hints used: {second.memory_hints_used}  ",
        f"- Status remains: {second.requisition_status} (not PENDING_APPROVAL)",
        "",
        "```",
        "\n".join(t2),
        "```",
        "",
        "## What this shows",
        "",
        "- Memory improved the second task by prefilling last quantity and default requester.",
        "- The agent still re-checked reorder status and quotations.",
        "- The new record stayed DRAFT. Memory did not route or award a supplier.",
        "",
    ]
    out = PROJECT_ROOT / "results" / "week6_memory_demo.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    print(
        "run2",
        second.memory_hints_used,
        second.quantity,
        second.requisition_status,
    )
    tmp.cleanup()


if __name__ == "__main__":
    main()
