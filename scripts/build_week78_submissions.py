#!/usr/bin/env python3
"""Build WEEK7 and WEEK8 submission folders in WEEK1 style."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBMISSION = PROJECT_ROOT / "submission"
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from arrange_submissions import _arrow, _draw_box, _font, build_week1_style_progress  # noqa: E402
from build_submission_docx import add_page_numbers, add_title_block, parse_markdown_to_doc  # noqa: E402
from docx import Document


def save_week7_architecture(path: Path) -> None:
    w, h = 1480, 920
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_f, box_f, small_f = _font(22, True), _font(15, True), _font(13)
    d.text((40, 20), "ProcurePrep UG — Week 7 Evaluation and Guardrails", fill="#111", font=title_f)
    _draw_box(d, (40, 90, 460, 200), "32 scenarios\nnormal / edge / adversarial", box_f, fill="#E8F1FB")
    _draw_box(d, (510, 90, 970, 200), "Bounded agent + MCP\nfail closed", box_f, fill="#FFF4D6")
    _draw_box(d, (1020, 90, 1440, 200), "JSONL traces\nlatency + outcome", box_f, fill="#F4F4F4")
    _arrow(d, (250, 200), (250, 260))
    _arrow(d, (740, 200), (740, 260))
    _arrow(d, (1230, 200), (1230, 260))
    _draw_box(d, (40, 260, 460, 380), "Input validation\ninjection scan", small_f, fill="#E6F4EA")
    _draw_box(d, (510, 260, 970, 380), "Allow-list + roles\nconfirm on route", small_f, fill="#E6F4EA")
    _draw_box(d, (1020, 260, 1440, 380), "Failure catalogue\nre-test evidence", small_f, fill="#FDECEA")
    _arrow(d, (740, 380), (740, 440))
    _draw_box(d, (280, 440, 1200, 560), "32 / 32 scenarios passed in this release run", box_f, fill="#E8F1FB")
    _arrow(d, (740, 560), (740, 620))
    _draw_box(d, (280, 620, 1200, 760), "Human still approves spend  —  no PO or payment", box_f, fill="#EDE7F6")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=92)
    print(f"  Wrote {path.relative_to(PROJECT_ROOT)}")


def save_week8_architecture(path: Path) -> None:
    w, h = 1480, 900
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_f, box_f, small_f = _font(20, True), _font(14, True), _font(13)
    d.text((40, 20), "ProcurePrep UG — Final System (Week 8)", fill="#111", font=title_f)
    layers = [
        (40, 90, "SME officer", "#E8F1FB"),
        (40, 200, "Bounded agent + Gemini tools", "#FFF4D6"),
        (40, 310, "Guardrails / traces / memory", "#E6F4EA"),
        (40, 420, "CSV data + Chroma corpus", "#F4F4F4"),
        (40, 530, "Human approval boundary", "#EDE7F6"),
    ]
    for x, y, label, fill in layers:
        _draw_box(d, (x, y, 700, y + 80), label, box_f, fill=fill)
        if y < 530:
            _arrow(d, (370, y + 80), (370, y + 110))
    _draw_box(d, (780, 90, 1440, 280), "Deterministic:\nreorder, validate, allow-list", small_f, fill="#E6F4EA")
    _draw_box(d, (780, 320, 1440, 510), "Probabilistic:\ncompare, explain, draft text", small_f, fill="#E8F1FB")
    _draw_box(d, (780, 550, 1440, 760), "Out of scope:\npayment, award, live PO", small_f, fill="#FDECEA")
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
    week7 = SUBMISSION / "WEEK7"
    week8 = SUBMISSION / "WEEK8"
    week7.mkdir(parents=True, exist_ok=True)
    week8.mkdir(parents=True, exist_ok=True)

    save_week7_architecture(week7 / "Evaluation_Guardrails.jpg")
    save_week8_architecture(week8 / "Final_Architecture.jpg")

    build_week1_style_progress(
        "Week 7 Progress Report",
        PROJECT_ROOT / "docs/weekly-reports/week7.md",
        week7 / "BSE4104 Week 7 Progress Report.docx",
    )
    build_week1_style_progress(
        "Week 8 Progress Report",
        PROJECT_ROOT / "docs/weekly-reports/week8.md",
        week8 / "BSE4104 Week 8 Progress Report.docx",
    )

    build_doc("32-Scenario Evaluation Results", PROJECT_ROOT / "results/week7_evaluation.md", week7 / "ProcurePrep UG Evaluation Results.docx")
    build_doc("Guardrail Implementation Evidence", PROJECT_ROOT / "docs/evaluation/guardrails.md", week7 / "ProcurePrep UG Guardrail Evidence.docx")
    build_doc("Failure Catalogue", PROJECT_ROOT / "docs/evaluation/failure-catalogue.md", week7 / "ProcurePrep UG Failure Catalogue.docx")

    build_doc("Final Engineering Report", PROJECT_ROOT / "docs/final-engineering-report.md", week8 / "ProcurePrep UG Final Engineering Report.docx")
    build_doc("Demonstration Outline", PROJECT_ROOT / "docs/presentation.md", week8 / "ProcurePrep UG Demonstration Outline.docx")
    build_doc("Known Limitations", PROJECT_ROOT / "docs/known-limitations.md", week8 / "ProcurePrep UG Known Limitations.docx")
    build_doc("Evaluation Evidence Pack", PROJECT_ROOT / "results/week7_evaluation.md", week8 / "ProcurePrep UG Evaluation Evidence Pack.docx")
    print("Done.")


if __name__ == "__main__":
    main()
