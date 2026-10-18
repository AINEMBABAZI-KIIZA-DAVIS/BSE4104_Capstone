#!/usr/bin/env python3
"""Build WEEK5 and WEEK6 submission folders in WEEK1 style."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBMISSION = PROJECT_ROOT / "submission"
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from arrange_submissions import (  # noqa: E402
    _arrow,
    _draw_box,
    _font,
    build_week1_style_progress,
)
from build_submission_docx import add_page_numbers, add_title_block, parse_markdown_to_doc  # noqa: E402


def save_week5_architecture(path: Path) -> None:
    w, h = 1500, 1080
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_f, box_f, small_f = _font(22, True), _font(15, True), _font(13)
    d.text((40, 20), "ProcurePrep UG — Week 5 Bounded Agent Architecture", fill="#111", font=title_f)

    _draw_box(d, (520, 70, 980, 130), "Goal: prepare DRAFT requisition", box_f, fill="#E8F1FB")
    _arrow(d, (750, 130), (750, 165))
    _draw_box(d, (480, 165, 1020, 230), "SENSE  session + optional memory hints", box_f, fill="#F4F4F4")
    _arrow(d, (750, 230), (750, 265))
    _draw_box(d, (500, 265, 1000, 330), "PLAN  next approved tool or stop", box_f, fill="#FFF4D6")

    y = 390
    tools = [
        (40, "get_reorder_status"),
        (400, "get_supplier_quotations"),
        (760, "create_requisition_draft"),
        (1120, "route (human gate)"),
    ]
    for x, name in tools:
        _arrow(d, (750, 330), (x + 160, y))
        fill = "#FDECEA" if "route" in name else "#E6F4EA"
        _draw_box(d, (x, y, x + 320, y + 70), name, small_f, fill=fill)

    _arrow(d, (750, 460), (750, 500))
    _draw_box(d, (400, 500, 1100, 580), "OBSERVE  write result into WorkflowState", box_f, fill="#E8F1FB")
    _arrow(d, (750, 580), (750, 620))
    _draw_box(d, (280, 620, 1220, 720), "Re-plan if QUOTATION_EXPIRED / stop on limits, no quotes, or no reorder", small_f, fill="#FFF4D6")
    _arrow(d, (750, 720), (750, 770))
    _draw_box(d, (360, 770, 1140, 880), "STOP  GOAL_COMPLETE / FAILED / HUMAN_DECLINED", box_f, fill="#EDE7F6")
    _draw_box(d, (360, 920, 1140, 1000), "Human store manager  —  no purchase or award", box_f, fill="#EDE7F6")

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=92)
    print(f"  Wrote {path.relative_to(PROJECT_ROOT)}")


def save_week6_architecture(path: Path) -> None:
    w, h = 1500, 980
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_f, box_f, small_f = _font(22, True), _font(15, True), _font(13)
    d.text((40, 20), "ProcurePrep UG — Week 6 State, Memory and MCP Interface", fill="#111", font=title_f)

    _draw_box(d, (40, 90, 480, 200), "Session state\nWorkflowState  (one run)", box_f, fill="#E8F1FB")
    _draw_box(d, (520, 90, 980, 200), "Bounded agent\nSense / Plan / Act / Observe", box_f, fill="#FFF4D6")
    _draw_box(d, (1020, 90, 1460, 200), "MCP-style adapter\nlist / call + roles", box_f, fill="#F4F4F4")

    _arrow(d, (260, 200), (260, 250))
    _arrow(d, (750, 200), (750, 250))
    _arrow(d, (1240, 200), (1240, 250))

    _draw_box(d, (40, 250, 480, 360), "Persistent memory\npreferences + item history", box_f, fill="#E6F4EA")
    _draw_box(d, (520, 250, 980, 360), "Approved tools\nvalidation in Python", box_f, fill="#E6F4EA")
    _draw_box(d, (1020, 250, 1460, 360), "Permissions\nconfirm on route", box_f, fill="#FDECEA")

    _arrow(d, (750, 360), (750, 410))
    _draw_box(d, (300, 410, 1200, 520), "Memory may prefill requester and last quantity only", small_f, fill="#FFF4D6")
    _arrow(d, (750, 520), (750, 570))
    _draw_box(d, (300, 570, 1200, 680), "Still re-check stock and quotes. Draft stays DRAFT.", small_f, fill="#E8F1FB")
    _arrow(d, (750, 680), (750, 730))
    _draw_box(d, (300, 730, 1200, 850), "90-day retention  ·  officer/manager roles  ·  no silent award", box_f, fill="#EDE7F6")

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=92)
    print(f"  Wrote {path.relative_to(PROJECT_ROOT)}")


def build_doc(title: str, md_path: Path, out_path: Path) -> None:
    doc = Document()
    add_title_block(doc, title)
    parse_markdown_to_doc(doc, md_path.read_text(encoding="utf-8"), render_diagrams=False)
    add_page_numbers(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"  Created {out_path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    week5 = SUBMISSION / "WEEK5"
    week6 = SUBMISSION / "WEEK6"
    week5.mkdir(parents=True, exist_ok=True)
    week6.mkdir(parents=True, exist_ok=True)

    save_week5_architecture(week5 / "Agent_Architecture.jpg")
    save_week6_architecture(week6 / "State_Memory_Architecture.jpg")

    build_week1_style_progress(
        "Week 5 Progress Report",
        PROJECT_ROOT / "docs/weekly-reports/week5.md",
        week5 / "BSE4104 Week 5 Progress Report.docx",
    )
    build_week1_style_progress(
        "Week 6 Progress Report",
        PROJECT_ROOT / "docs/weekly-reports/week6.md",
        week6 / "BSE4104 Week 6 Progress Report.docx",
    )

    build_doc("Agent Task Contract", PROJECT_ROOT / "docs/architecture/agent-task-contract.md", week5 / "ProcurePrep UG Agent Task Contract.docx")
    build_doc("Updated Agent Architecture", PROJECT_ROOT / "docs/architecture/agent-architecture.md", week5 / "ProcurePrep UG Agent Architecture.docx")
    build_doc("Execution Traces", PROJECT_ROOT / "results/week5_execution_traces.md", week5 / "ProcurePrep UG Execution Traces.docx")

    build_doc("State Model", PROJECT_ROOT / "docs/architecture/state-model.md", week6 / "ProcurePrep UG State Model.docx")
    build_doc("Memory Design and Data Handling Note", PROJECT_ROOT / "docs/architecture/memory-design.md", week6 / "ProcurePrep UG Memory Design Note.docx")
    build_doc("Memory and State Demonstration", PROJECT_ROOT / "results/week6_memory_demo.md", week6 / "ProcurePrep UG Memory Demonstration.docx")
    build_doc("MCP-Style Interface Specification", PROJECT_ROOT / "docs/architecture/mcp-interface.md", week6 / "ProcurePrep UG MCP Interface.docx")
    print("Done.")


if __name__ == "__main__":
    main()
