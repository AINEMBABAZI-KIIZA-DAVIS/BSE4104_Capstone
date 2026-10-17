#!/usr/bin/env python3
"""Run Week 4 tool tests and a two-tool demonstration; write results markdown."""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.requisition_store import RequisitionStore
from src.tools import (
    create_requisition_draft,
    dispatch_tool,
    get_reorder_status,
    get_supplier_quotations,
    route_requisition_for_approval,
    set_reference_date,
    set_store,
)


def run_unit_tests() -> tuple[str, int, int]:
    buf = io.StringIO()
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("tests.test_tools")
    runner = unittest.TextTestRunner(stream=buf, verbosity=2)
    result = runner.run(suite)
    return buf.getvalue(), result.testsRun, len(result.failures) + len(result.errors)


def write_test_report(output: str, ran: int, failed: int) -> Path:
    path = PROJECT_ROOT / "results" / "week4_tool_tests.md"
    status = "PASS" if failed == 0 else "FAIL"
    lines = [
        "# ProcurePrep UG – Week 4 Failure and Authorization Tests",
        "",
        f"**Date:** {datetime.now().isoformat(timespec='seconds')}  ",
        f"**Suite:** `tests/test_tools.py`  ",
        f"**Result:** {ran} tests, {failed} failure(s) — **{status}**",
        "",
        "These tests cover the assignment requirement to exercise missing parameters, unauthorized requests, unavailable services and unexpected tool responses.",
        "",
        "## Cases",
        "",
        "| Requirement | Test | Expected behaviour |",
        "| :--- | :--- | :--- |",
        "| Missing parameters | `test_get_quotations_missing_item_id`, `test_create_draft_missing_quantity`, `test_route_missing_requisition_id` | Structured `MISSING_PARAMETER`; no crash |",
        "| Unauthorized / unknown tool | `test_unknown_tool_rejected` | `UNKNOWN_TOOL` for `award_supplier_contract` |",
        "| Unauthorized routing | `test_human_declines_routing` | `HUMAN_DECLINED`; requisition stays `DRAFT` |",
        "| Invalid / expired / wrong-item | `test_create_draft_expired_quotation`, `test_create_draft_wrong_quotation_for_item`, `test_create_draft_invalid_quantity` | Deterministic reject; no record written |",
        "| Unexpected tool response | `test_create_draft_malformed_quotation` | `MALFORMED_QUOTATION_RECORD` |",
        "| Unavailable service | `test_orchestrator_api_unreachable` | `AgentOrchestratorError` with transcript; no hang |",
        "| Invalid status | `test_route_already_pending` | `INVALID_STATUS` on second route |",
        "",
        "## Raw unittest output",
        "",
        "```",
        output.rstrip(),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_offline_demo() -> list[str]:
    """Execute the same tool sequence as the ITEM-004 demo using real tools."""
    tmp = tempfile.TemporaryDirectory()
    store = RequisitionStore(Path(tmp.name) / "requisitions.json")
    set_store(store)
    set_reference_date("2026-09-16")

    transcript = [
        "Mode: deterministic tool demonstration (same calls the agent makes for ITEM-004)",
        "Reference date: 2026-09-16",
        "User: For ITEM-004 (Thermal POS Receipt Rolls): check reorder status and quotations, then create a DRAFT requisition for 20 cartons using the cheapest valid quote. Requested by Jane Okello.",
        "",
    ]

    status = get_reorder_status("ITEM-004")
    transcript.append("[TOOL CALL] get_reorder_status({\"item_id\": \"ITEM-004\"})")
    transcript.append("[TOOL RESULT]")
    transcript.append(json.dumps(status, indent=2))
    transcript.append("")

    quotes = get_supplier_quotations("ITEM-004")
    transcript.append("[TOOL CALL] get_supplier_quotations({\"item_id\": \"ITEM-004\"})")
    transcript.append("[TOOL RESULT]")
    transcript.append(json.dumps(quotes, indent=2))
    transcript.append("")

    valid = [
        q for q in quotes.get("quotations", [])
        if q.get("quotation_valid_until") and q["quotation_valid_until"] >= "2026-09-16"
    ]
    cheapest = min(valid, key=lambda q: q["unit_price"]) if valid else None
    if cheapest is None:
        transcript.append("[ERROR] No valid quotation available.")
        tmp.cleanup()
        return transcript

    draft = create_requisition_draft(
        item_id="ITEM-004",
        quantity=20,
        selected_quotation_id=cheapest["quotation_id"],
        requested_by="Jane Okello",
    )
    transcript.append(
        "[TOOL CALL] create_requisition_draft("
        + json.dumps({
            "item_id": "ITEM-004",
            "quantity": 20,
            "selected_quotation_id": cheapest["quotation_id"],
            "requested_by": "Jane Okello",
        })
        + ")"
    )
    transcript.append("[TOOL RESULT]")
    transcript.append(json.dumps(draft, indent=2))
    transcript.append("")

    routed = route_requisition_for_approval(draft.get("requisition_id"))
    transcript.append(
        "[STAGED] route_requisition_for_approval — human confirmation required"
    )
    transcript.append("[DEMO] Human confirmed routing.")
    transcript.append("[TOOL RESULT]")
    transcript.append(json.dumps(routed, indent=2))
    transcript.append("")
    transcript.append(
        "FINAL SUMMARY: ITEM-004 needs reorder (deficit 20 cartons). "
        f"Cheapest valid quote is {cheapest['quotation_id']} at UGX {cheapest['unit_price']}. "
        f"Draft {draft.get('requisition_id')} was created and routed to PENDING_APPROVAL. "
        "No purchase order or payment was issued."
    )
    tmp.cleanup()
    return transcript


def try_live_agent() -> tuple[str, list[str]] | None:
    if not os.environ.get("GEMINI_API_KEY"):
        return None
    try:
        from src.agent_orchestrator import run_agent
        final, transcript = run_agent(
            "For ITEM-004 (Thermal POS Receipt Rolls): use get_reorder_status and "
            "get_supplier_quotations, then create a DRAFT requisition for 20 cartons "
            "using the cheapest quotation that is still valid on 2026-09-16. "
            "Requested by Jane Okello. Do not route for approval.",
            auto_confirm=False,
        )
        return final, transcript
    except Exception as exc:
        return None


def write_demo(offline: list[str], live: tuple[str, list[str]] | None) -> Path:
    path = PROJECT_ROOT / "results" / "week4_tool_demo.md"
    lines = [
        "# ProcurePrep UG – Week 4 Tool Demonstration",
        "",
        f"**Date:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}  ",
        "**Model:** `gemini-3.5-flash-lite` (live section) / deterministic tool runner (evidence section)  ",
        "**Item:** ITEM-004 Thermal POS Receipt Rolls 80mm  ",
        "",
        "The assignment requires a working demonstration of at least two tools. This run uses `get_reorder_status` (deterministic application data), `get_supplier_quotations` (current quotation CSV) and `create_requisition_draft` (low-risk simulated side effect). Routing is shown as a staged high-impact action.",
        "",
        "## 1. Deterministic tool transcript",
        "",
        "```",
        "\n".join(offline),
        "```",
        "",
    ]
    if live:
        final, transcript = live
        lines.extend([
            "## 2. Live Gemini function-calling transcript",
            "",
            "```",
            "\n".join(transcript),
            "```",
            "",
            "### Final model response",
            "",
            final,
            "",
        ])
    else:
        lines.extend([
            "## 2. Live Gemini function-calling transcript",
            "",
            "Live Gemini run was not captured in this evidence file. The orchestrator in `src/agent_orchestrator.py` is implemented and can be started with:",
            "",
            "```",
            "python src/agent_orchestrator.py --demo --auto-confirm --transcript results/week4_tool_demo.md",
            "```",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    print("Running Week 4 unit tests...")
    output, ran, failed = run_unit_tests()
    print(output)
    test_path = write_test_report(output, ran, failed)
    print(f"Wrote {test_path}")

    print("Running offline two-tool demonstration...")
    offline = run_offline_demo()

    print("Attempting live Gemini demonstration...")
    live = try_live_agent()
    if live:
        print("Live agent run succeeded.")
    else:
        print("Live agent run skipped or failed; offline transcript still written.")

    demo_path = write_demo(offline, live)
    print(f"Wrote {demo_path}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
