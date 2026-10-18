"""
rag_reorder_checker.py – RAG-augmented reorder quotation comparison for ProcurePrep.

Extends the Week 2 reorder flow by retrieving relevant corpus chunks before LLM
explanation. Outputs include a RELEVANT KNOWLEDGE block (in the prompt) and
SOURCES USED (in the model response).

Run from the project root:
    python src/rag_reorder_checker.py
    python src/rag_reorder_checker.py --items ITEM-001 ITEM-008
    python src/rag_reorder_checker.py --question "What should a goods requisition include?"
"""

import os
import sys
import csv
import time
import argparse
from datetime import datetime

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
sys.path.insert(0, PROJECT_ROOT)

from google import genai
from google.genai import types

from src.retrieve import retrieve_relevant_chunks

REFERENCE_DATE_DEFAULT = "2026-09-16"
LOG_FILE = os.path.join(PROJECT_ROOT, "retrieval_log.txt")


def load_inventory(filepath):
    items = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["current_stock"] = float(row["current_stock"])
            row["reorder_threshold"] = float(row["reorder_threshold"])
            items.append(row)
    return items


def load_quotations(filepath):
    quotes_by_item = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row["item_id"]
            if item_id not in quotes_by_item:
                quotes_by_item[item_id] = []
            quotes_by_item[item_id].append(row)
    return quotes_by_item


def check_reorder_need(current_stock, reorder_threshold):
    return current_stock < reorder_threshold


def format_quotations_table(quotes):
    headers = [
        "Quotation ID", "Supplier Name", "Unit Price (UGX)",
        "Qty Available", "Delivery Terms", "Valid Until", "Notes",
    ]
    lines = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    for q in quotes:
        row = [
            q.get("quotation_id", ""),
            q.get("supplier_name", ""),
            str(q.get("unit_price", "")),
            str(q.get("quantity_available", "")),
            q.get("delivery_terms", "").strip() or "[Not Specified]",
            q.get("quotation_valid_until", "").strip() or "[Not Specified]",
            q.get("notes", "").strip() or "None",
        ]
        lines.append(" | ".join(row))
    return "\n".join(lines)


def build_comparison_payload(item, quotes, reference_date):
    deficit = max(0.0, item["reorder_threshold"] - item["current_stock"])
    table_str = format_quotations_table(quotes)
    return f"""OPERATIONAL REFERENCE DATE: {reference_date}

INVENTORY ITEM DETAILS:
- Item ID: {item['item_id']}
- Item Name: {item['item_name']}
- Category: {item['category']}
- Current Stock: {item['current_stock']:g} {item['unit']}
- Reorder Threshold: {item['reorder_threshold']:g} {item['unit']}
- Replenishment Deficit: {deficit:g} {item['unit']}

SUPPLIER QUOTATIONS ON FILE ({len(quotes)} quote(s)):
{table_str}

Please generate the objective REORDER QUOTATION COMPARISON REPORT following your system instructions.
"""


def build_retrieval_query(item=None, quotes=None, question=None):
    """Build a retrieval query tailored to comparison or policy Q&A."""
    if question:
        return question

    parts = [
        "SME procurement reorder quotation comparison",
        "vendor evaluation criteria delivery terms validity",
        "supplier terms payment UGX reorder policy",
    ]
    if item:
        parts.append(
            f"item {item['item_name']} category {item['category']} "
            f"replenishment deficit reorder threshold"
        )
    if quotes:
        suppliers = ", ".join({q.get("supplier_name", "") for q in quotes})
        parts.append(f"suppliers {suppliers} unit price delivery MOQ")
    return " ".join(parts)


def build_knowledge_block(chunks):
    lines = ["RELEVANT KNOWLEDGE:", "-------------------"]
    for chunk in chunks:
        lines.append(f"[Source: {chunk['source_filename']}]")
        lines.append(chunk["text"])
        lines.append("")
    return "\n".join(lines)


def log_retrieval(label, chunks):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Context: {label}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        for i, c in enumerate(chunks, 1):
            f.write(
                f"  [{i}] {c['source_filename']} "
                f"(chunk {c['chunk_index']}, score={c['score']})\n"
            )
        f.write(f"{'=' * 60}\n")


def call_gemini(client, model_name, system_instruction, user_content, temperature=0.1):
    response = client.models.generate_content(
        model=model_name,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        ),
    )
    return response.text


def rag_answer_question(
    client,
    model_name,
    system_instruction,
    question,
    top_k=4,
    tc_label="policy-question",
):
    """Answer a standalone policy/template question with RAG grounding."""
    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    log_retrieval(tc_label, chunks)
    knowledge_block = build_knowledge_block(chunks)

    user_message = f"""{knowledge_block}

POLICY / TEMPLATE QUESTION:
---------------------------
{question}

Please answer using Policy Question Mode in your system instructions.
"""

    report = call_gemini(client, model_name, system_instruction, user_message)
    return {"report": report, "chunks_used": chunks, "question": question}


def rag_compare_quotations(
    client,
    model_name,
    system_instruction,
    item,
    quotes,
    reference_date,
    top_k=4,
):
    """Run RAG-augmented quotation comparison for a single reorder item."""
    query = build_retrieval_query(item=item, quotes=quotes)
    chunks = retrieve_relevant_chunks(query, top_k=top_k)
    log_retrieval(item["item_id"], chunks)

    knowledge_block = build_knowledge_block(chunks)
    comparison_payload = build_comparison_payload(item, quotes, reference_date)
    user_message = f"""{knowledge_block}

{comparison_payload}
"""

    report = call_gemini(client, model_name, system_instruction, user_message)
    return {"report": report, "chunks_used": chunks}


def main():
    parser = argparse.ArgumentParser(
        description="ProcurePrep – RAG-augmented Reorder Quotation Comparison"
    )
    parser.add_argument("--inventory", default="data/inventory.csv")
    parser.add_argument("--quotations", default="data/quotations.csv")
    parser.add_argument("--prompt", default="prompts/prompt_rag_v1.0.txt")
    parser.add_argument("--output", default="results/reorder_reports_rag.md")
    parser.add_argument("--date", default=REFERENCE_DATE_DEFAULT)
    parser.add_argument("--items", nargs="+", default=None)
    parser.add_argument("--model", default="gemini-3.5-flash-lite")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument(
        "--question",
        default=None,
        help="Answer a standalone policy/template question with RAG (skips batch run)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment or .env file.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    prompt_path = os.path.join(PROJECT_ROOT, args.prompt)
    if not os.path.exists(prompt_path):
        print(f"ERROR: Prompt file not found: {prompt_path}")
        sys.exit(1)

    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    if args.question:
        print(f"Policy question: {args.question}")
        print("=" * 70)
        result = rag_answer_question(
            client,
            args.model,
            system_instruction,
            args.question,
            top_k=args.top_k,
            tc_label=f"Q: {args.question[:60]}",
        )
        print(f"Retrieved {len(result['chunks_used'])} chunk(s):")
        for c in result["chunks_used"]:
            print(f"  - {c['source_filename']} (chunk {c['chunk_index']}, score={c['score']})")
        print()
        print(result["report"])
        return

    inventory_path = os.path.join(PROJECT_ROOT, args.inventory)
    quotations_path = os.path.join(PROJECT_ROOT, args.quotations)
    inventory = load_inventory(inventory_path)
    quotations = load_quotations(quotations_path)

    if args.items:
        inventory = [item for item in inventory if item["item_id"] in args.items]

    print(f"Loaded {len(inventory)} inventory item(s).")
    print(f"Prompt: {args.prompt} | RAG top_k: {args.top_k} | Model: {args.model}")
    print("=" * 70)

    report_sections = [
        "# ProcurePrep UG – RAG-Augmented Procurement Preparation Reports\n",
        f"**Operating Date:** {args.date}  ",
        f"**Prompt:** `{args.prompt}`  ",
        f"**Model:** `{args.model}`  ",
        f"**Retrieval:** top-{args.top_k} from `procureprep_corpus`\n",
        "---\n",
    ]

    reorder_count = 0
    ok_count = 0
    no_quotes_count = 0

    for item in inventory:
        item_id = item["item_id"]
        item_name = item["item_name"]
        curr_stock = item["current_stock"]
        threshold = item["reorder_threshold"]
        unit = item["unit"]

        print(f"\nEvaluating {item_id}: {item_name} (Stock: {curr_stock:g}/{threshold:g} {unit})")

        if not check_reorder_need(curr_stock, threshold):
            ok_count += 1
            status_text = (
                f"### STATUS: SUFFICIENT STOCK – NO REORDER NEEDED\n"
                f"- **Item:** {item_name} (`{item_id}`)\n"
                f"- **Current Stock:** {curr_stock:g} {unit} >= **Reorder Threshold:** {threshold:g} {unit}\n"
                f"- **Action:** Deterministic check passed. No RAG retrieval or LLM call required.\n"
            )
            print("  --> [PASS] Stock sufficient. RAG/LLM skipped.")
            report_sections.append(status_text + "\n---\n")
            continue

        reorder_count += 1
        deficit = threshold - curr_stock
        quotes = quotations.get(item_id, [])

        print(f"  --> [REORDER NEEDED] Deficit: {deficit:g} {unit}. Quotes: {len(quotes)}")

        if not quotes:
            no_quotes_count += 1
            status_text = (
                f"### REORDER REQUIRED – NO SUPPLIER QUOTATIONS AVAILABLE\n"
                f"- **Item:** {item_name} (`{item_id}`)\n"
                f"- **Stock Level:** Current: {curr_stock:g} {unit} | Threshold: {threshold:g} {unit} | Deficit: {deficit:g} {unit}\n"
                f"- **Action Required:** Solicit quotations from registered suppliers before comparison.\n"
            )
            print("  --> [NO QUOTES] RAG/LLM skipped.")
            report_sections.append(status_text + "\n---\n")
            continue

        try:
            result = rag_compare_quotations(
                client,
                args.model,
                system_instruction,
                item,
                quotes,
                args.date,
                top_k=args.top_k,
            )
            chunks = result["chunks_used"]
            print(f"  --> [RAG] Retrieved {len(chunks)} chunk(s):")
            for c in chunks:
                print(f"        {c['source_filename']} (chunk {c['chunk_index']}, score={c['score']})")
            print("  --> [SUCCESS] RAG comparison report generated.")
            report_sections.append(result["report"].strip() + "\n\n---\n")
        except Exception as e:
            print(f"  --> [ERROR] {e}")
            report_sections.append(f"### ERROR FOR {item_id}\n`{e}`\n\n---\n")

        time.sleep(1)

    output_path = os.path.join(PROJECT_ROOT, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))

    print("\n" + "=" * 70)
    print("Batch run completed:")
    print(f"  - Total items: {len(inventory)}")
    print(f"  - Sufficient stock (skipped): {ok_count}")
    print(f"  - Reorder, no quotes: {no_quotes_count}")
    print(f"  - Reorder, RAG compared: {reorder_count - no_quotes_count}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
