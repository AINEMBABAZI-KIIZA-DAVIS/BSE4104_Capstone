#!/usr/bin/env python3
"""Build the Week 8 PowerPoint and How-to-Run Word document."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PptRGB
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches as PptInches, Pt as PptPt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEEK8 = PROJECT_ROOT / "submission" / "WEEK8"
DOCS = PROJECT_ROOT / "docs"

NAVY = PptRGB(0x1F, 0x3A, 0x5F)
GOLD = PptRGB(0xC4, 0xA3, 0x5A)
WHITE = PptRGB(0xFF, 0xFF, 0xFF)
INK = PptRGB(0x22, 0x22, 0x22)
MUTED = PptRGB(0x55, 0x55, 0x55)
LIGHT = PptRGB(0xF4, 0xF1, 0xEA)

DOC_NAVY = RGBColor(0x1F, 0x3A, 0x5F)


def _set_run(run, size=18, bold=False, color=INK, name="Calibri"):
    run.font.size = PptPt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def _fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _bar(slide, prs):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Emu(360000))
    _fill(bar, NAVY)
    foot = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, prs.slide_height - Emu(320000), prs.slide_width, Emu(320000))
    _fill(foot, NAVY)
    tb = foot.text_frame
    tb.clear()
    p = tb.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = "  ProcurePrep UG  ·  BSE4104  ·  Makerere University  ·  2026"
    _set_run(run, 11, False, WHITE)


def _title_box(slide, text, top=0.55, left=0.6, width=12.0, height=0.7, size=28):
    box = slide.shapes.add_textbox(PptInches(left), PptInches(top), PptInches(width), PptInches(height))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    _set_run(run, size, True, NAVY)
    return box


def _bullets(slide, items, top=1.4, left=0.7, width=12.0, height=5.2, size=18):
    box = slide.shapes.add_textbox(PptInches(left), PptInches(top), PptInches(width), PptInches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = PptPt(10)
        run = p.add_run()
        run.text = "•  " + item
        _set_run(run, size, False, INK)


def _code(slide, text, top=4.6, left=0.7, width=12.0, height=0.7):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, PptInches(left), PptInches(top), PptInches(width), PptInches(height))
    _fill(box, PptRGB(0x23, 0x2B, 0x36))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "  " + text
    _set_run(run, 16, False, WHITE, "Consolas")


def build_pptx(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = PptInches(13.333)
    prs.slide_height = PptInches(7.5)

    # 1 Title
    s = _blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    _fill(bg, NAVY)
    accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Emu(140000), prs.slide_height)
    _fill(accent, GOLD)
    box = s.shapes.add_textbox(PptInches(0.9), PptInches(1.7), PptInches(11.5), PptInches(1.2))
    p = box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "ProcurePrep UG"
    _set_run(run, 44, True, WHITE)
    box = s.shapes.add_textbox(PptInches(0.9), PptInches(3.0), PptInches(11.5), PptInches(1.4))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "AI-Native SME Procurement-Preparation Agent"
    _set_run(run, 24, False, GOLD)
    box = s.shapes.add_textbox(PptInches(0.9), PptInches(4.6), PptInches(11.5), PptInches(1.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "BSE4104  ·  Makerere University  ·  2026/2027\nNasiwa Hafswa  ·  Armand Shematsi  ·  Ainembabazi Kiiza Davis  ·  Alvin Mayega Kenneth"
    _set_run(run, 16, False, WHITE)

    # 2 Problem
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "1. Problem and target user")
    _bullets(s, [
        "User: SME procurement officer or owner-manager in Uganda",
        "Pain: stock checks and quote comparison are done by hand — late reorders, expired quotes, cash locked in MOQs",
        "Task: prepare one purchase, not run a national e-procurement platform",
        "Workflow: inventory → reorder check → quotation comparison → draft requisition → human approval",
        "Why AI: tradeoff explanation and drafting; not threshold math or spend authorization",
    ])

    # 3 Boundary
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "2. Where AI stops — the boundary")
    _bullets(s, [
        "AI may: compare quotes, explain risks, draft a requisition, choose the next approved tool",
        "Python must: decide reorder (current_stock < threshold), validate quotes, enforce the tool allow-list",
        "Human must: confirm routing and make the buying decision",
        "The agent must not: purchase, pay, award a supplier, or issue a purchase order",
        "This is the Week 1 AI Boundary Matrix, kept through Week 8",
    ])

    # 4 Progression
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "3. Eight-week architecture progression")
    _bullets(s, [
        "Week 2 — Gemini + versioned prompts; 10-case comparison baseline",
        "Week 3 — RAG over a 12-document SME corpus with source citations",
        "Week 4 — Four tools; human gate on route_requisition_for_approval",
        "Week 5 — Bounded Sense → Plan → Act → Observe → Stop loop",
        "Week 6 — Explicit session state, justified memory, MCP-style interface",
        "Week 7 — 32-scenario evaluation, traces, guardrails, failure catalogue",
        "Week 8 — Hardened README, final report, this demonstration",
    ], size=17)

    # 5 Live success
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "4. Live success — prepare a draft (ITEM-004)")
    _bullets(s, [
        "Thermal POS Receipt Rolls: stock 5 / threshold 25 → deficit 20 cartons",
        "Quotes: Q-107 UGX 45,000 (valid) and Q-108 UGX 48,000 (valid)",
        "Agent drafts on cheapest valid quote Q-107 — status stays DRAFT",
        "No routing unless the officer asks and confirms",
        "State clearly in the viva: no purchase order was created",
    ])
    _code(s, "python src/bounded_agent.py --item ITEM-004")

    # 6 Evidence
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "5. Evidence view — evaluation and traces")
    _bullets(s, [
        "Week 7 suite: 32 scenarios, 32 passed",
        "Categories: normal, edge, incorrect information, adversarial, tool-failure, unauthorized",
        "Criteria: task completion, tool selection, instruction following, safety, latency",
        "Each ACT is logged with session_id, tool, latency_ms and outcome",
        "Open results/week7_evaluation.md or results/traces/week7_eval.jsonl",
    ])
    _code(s, "python scripts/run_week7_evaluation.py")

    # 7 Failure
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "6. Real failure and recovery — ITEM-005")
    _bullets(s, [
        "Cheapest quote Q-109 (UGX 38,000) expired on 2026-08-15",
        "create_requisition_draft returns QUOTATION_EXPIRED — validation is Python, not the model",
        "Observer excludes Q-109; planner re-plans onto valid Q-110",
        "This is the required Week 5 failure/recovery trace",
        "Residual RAG limit: F-01 false [MISSING TERMS] was a prompt issue, not this path",
    ])
    _code(s, "python src/bounded_agent.py --item ITEM-005")

    # 8 Guardrails
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "7. Guardrails and lessons")
    _bullets(s, [
        "Tool allow-list of four names — award_contract is UNKNOWN_TOOL",
        "Roles: only procurement_officer / store_manager; vendors are rejected",
        "Routing requires explicit human confirmation",
        "Injection strings (ignore instructions, award, approve payment, DROP TABLE) are blocked",
        "Lesson: keep spend decisions out of the model; evaluate fail-closed behaviour, not only the happy path",
    ])

    # 9 Limitations
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "8. Known limitations")
    _bullets(s, [
        "Small 12-chunk corpus — RAG top-4 can be noisy for price questions (use CSV tools)",
        "F-01 / F-02 prompt fixes were not fully re-run on live Gemini",
        "Human approval is CLI-only; memory is a local JSON file",
        "MCP adapter is in-process, not a networked server",
        "Gemini is required for Weeks 2–4; Weeks 5–7 run without an API key",
    ])

    # 10 How to run (pointer)
    s = _blank(prs)
    _bar(s, prs)
    _title_box(s, "9. How to run (see the run guide)")
    _bullets(s, [
        "Create a venv, install requirements.txt, copy .env.example to .env",
        "Set GEMINI_API_KEY only if you need Week 2/3/4 Gemini features",
        "Demo without API key: bounded agent ITEM-004 then ITEM-005",
        "Tests: python -m unittest discover -s tests -q",
        "Full commands are in: How to Run ProcurePrep UG.docx",
    ])
    _code(s, "python -m unittest discover -s tests -q")

    # 11 Close
    s = _blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    _fill(bg, NAVY)
    accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Emu(140000), prs.slide_height)
    _fill(accent, GOLD)
    box = s.shapes.add_textbox(PptInches(0.9), PptInches(2.3), PptInches(11.5), PptInches(1.2))
    p = box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "Questions"
    _set_run(run, 44, True, WHITE)
    box = s.shapes.add_textbox(PptInches(0.9), PptInches(3.7), PptInches(11.5), PptInches(1.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Build the smallest useful agentic system that you can test, explain and safely control."
    _set_run(run, 20, False, GOLD)

    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    print(f"  Created {path.relative_to(PROJECT_ROOT)}")


def _doc_run(p, text, *, size=11, bold=False, italic=False, color=None, name="Calibri"):
    run = p.add_run(text)
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rPr.insert(0, rFonts)
    return run


def _heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = DOC_NAVY
        run.font.name = "Calibri"


def _para(doc, text, bold=False):
    p = doc.add_paragraph()
    _doc_run(p, text, bold=bold)
    return p


def _code_para(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = _doc_run(p, text, name="Consolas", size=10)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F2F2F2")
    shd.set(qn("w:val"), "clear")
    run._element.get_or_add_rPr().append(shd)


def _add_page_numbers(doc):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = "PAGE"
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run._r.append(fld_begin)
        run._r.append(instr)
        run._r.append(fld_sep)
        run._r.append(fld_end)


def build_run_docx(path: Path) -> None:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _doc_run(p, "BSE4104 AI-Native & Agentic Engineering Capstone", size=16, bold=True, color=DOC_NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _doc_run(p, "How to Run ProcurePrep UG", size=18, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _doc_run(p, "Setup, commands, demonstration script and troubleshooting", size=12, italic=True)

    _heading(doc, "1. What this system is")
    _para(
        doc,
        "ProcurePrep UG prepares an SME purchase in Uganda: it checks stock, compares supplier quotations, "
        "drafts a requisition and can route that draft for human approval. It does not buy, pay or award a supplier.",
    )
    _para(
        doc,
        "Weeks 5–7 (bounded agent, memory, 32-scenario evaluation) run without a Gemini API key. "
        "Weeks 2–4 (comparison reports, RAG, live function calling) need GEMINI_API_KEY.",
    )

    _heading(doc, "2. Prerequisites")
    for item in (
        "Python 3.10 or later",
        "Windows, macOS or Linux",
        "Internet access only if you will call Gemini or build the Chroma index",
        "A Gemini API key in .env for Week 2 / 3 / 4 only",
    ):
        doc.add_paragraph(item, style="List Bullet")

    _heading(doc, "3. One-time setup (Windows)")
    _para(doc, "Open a terminal in the project root (the folder that contains main.py).")
    for line in (
        "python -m venv venv",
        "venv\\Scripts\\activate",
        "pip install -r requirements.txt",
        "copy .env.example .env",
    ):
        _code_para(doc, line)
    _para(doc, "Edit .env and set GEMINI_API_KEY=your_key if you need Gemini. Do not commit .env.")

    _heading(doc, "3b. One-time setup (macOS / Linux)")
    for line in (
        "python3 -m venv venv",
        "source venv/bin/activate",
        "pip install -r requirements.txt",
        "cp .env.example .env",
    ):
        _code_para(doc, line)

    _heading(doc, "4. Optional: build the RAG index")
    _para(doc, "Required only for Week 3 RAG. Needs GEMINI_API_KEY. chroma_db/ is not in git.")
    _code_para(doc, "python src/embed_store.py")

    _heading(doc, "5. Recommended demonstration (no API key)")
    _para(doc, "Use this sequence in the viva. Activate the venv first.")
    _para(doc, "Step A — confirm tests", bold=True)
    _code_para(doc, "python -m unittest discover -s tests -q")
    _para(doc, "Expect: OK (34 tests).")

    _para(doc, "Step B — successful draft (ITEM-004)", bold=True)
    _code_para(doc, "python src/bounded_agent.py --item ITEM-004")
    _para(
        doc,
        "Expect: reorder needed (deficit 20), quotes Q-107 and Q-108, DRAFT on cheapest valid Q-107, "
        "stop reason GOAL_COMPLETE. Say out loud: no purchase order was created.",
    )

    _para(doc, "Step C — failure and recovery (ITEM-005)", bold=True)
    _code_para(doc, "python src/bounded_agent.py --item ITEM-005")
    _para(
        doc,
        "Expect: first draft attempt on expired Q-109 → QUOTATION_EXPIRED → re-plan onto Q-110 → GOAL_COMPLETE.",
    )

    _para(doc, "Step D — evaluation evidence", bold=True)
    _code_para(doc, "python scripts/run_week7_evaluation.py")
    _para(doc, "Expect: 32/32 passed. Open results/week7_evaluation.md or results/traces/week7_eval.jsonl.")

    _para(doc, "Step E — optional routing (human gate)", bold=True)
    _code_para(doc, "python src/bounded_agent.py --item ITEM-004 --route")
    _para(doc, "Type n to decline. Status stays DRAFT. Type y only if you want PENDING_APPROVAL (still not a PO).")

    _heading(doc, "6. Commands that need Gemini")
    table = doc.add_table(rows=5, cols=2)
    table.style = "Table Grid"
    rows = [
        ("Purpose", "Command"),
        ("Week 2 comparison batch", "python main.py --prompt prompts/prompt_v1.1.txt --output results/reorder_reports_v1.1.md"),
        ("Week 3 RAG on ITEM-001", "python src/rag_reorder_checker.py --items ITEM-001"),
        ("Week 3 policy question", 'python src/rag_reorder_checker.py --question "How many quotations are required between UGX 500,000 and 5,000,000?"'),
        ("Week 4 live tool demo", "python src/agent_orchestrator.py --demo"),
    ]
    for i, (a, b) in enumerate(rows):
        table.rows[i].cells[0].text = a
        table.rows[i].cells[1].text = b
    doc.add_paragraph()

    _heading(doc, "7. Other useful commands")
    for line in (
        "python src/bounded_agent.py --item ITEM-002     # safe stop: stock sufficient",
        "python src/bounded_agent.py --item ITEM-007     # stop: no quotations",
        "python src/bounded_agent.py --traces results/week5_execution_traces.md",
        "python src/retrieve.py \"What should a goods requisition include?\"",
    ):
        _code_para(doc, line)

    _heading(doc, "8. Project folders you will open in the demo")
    for item in (
        "data/inventory.csv and data/quotations.csv — operational data",
        "results/week7_evaluation.md — 32-scenario table",
        "results/week5_execution_traces.md — three agent traces",
        "submission/WEEK8/ — final report, this run guide, PowerPoint",
    ):
        doc.add_paragraph(item, style="List Bullet")

    _heading(doc, "9. Troubleshooting")
    items = [
        ("cannot import name 'genai' from 'google'", "Activate the venv and run pip install -r requirements.txt."),
        ("GEMINI_API_KEY not found", "Create .env from .env.example, or skip Gemini and use the Week 5 commands."),
        ("Collection procureprep_corpus not found", "Run python src/embed_store.py after setting the API key."),
        ("Human approval prompt hangs", "That is expected for --route. Type y or n. Use --auto-confirm only for transcripts."),
        ("Wrong folder", "Run all commands from the repository root (the folder that contains main.py)."),
    ]
    for problem, fix in items:
        p = doc.add_paragraph()
        _doc_run(p, problem + " — ", bold=True)
        _doc_run(p, fix)

    _heading(doc, "10. Safety reminder")
    _para(
        doc,
        "Never commit .env. Drafts write to data/requisitions.json (gitignored). "
        "Memory writes to data/agent_memory.json (gitignored). "
        "The agent must not be described as placing orders or paying suppliers.",
    )

    _add_page_numbers(doc)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    print(f"  Created {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    WEEK8.mkdir(parents=True, exist_ok=True)
    build_pptx(WEEK8 / "ProcurePrep UG Final Presentation.pptx")
    build_run_docx(WEEK8 / "ProcurePrep UG How to Run.docx")
    # copies in docs for easy find
    build_pptx(DOCS / "ProcurePrep UG Final Presentation.pptx")
    build_run_docx(DOCS / "ProcurePrep UG How to Run.docx")
    print("Done.")


if __name__ == "__main__":
    main()
