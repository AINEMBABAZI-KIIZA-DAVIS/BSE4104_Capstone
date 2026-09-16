#!/usr/bin/env python3
"""
ProcurePrep UG – AI-Native SME Procurement Preparation Engine
-------------------------------------------------------------
Automates the initial stages of procurement preparation for Ugandan SMEs:
1. Deterministic Inventory Check: Evaluates current_stock against reorder_threshold.
2. Supplier Quotation Extraction: Gathers active supplier quotations for deficit items.
3. Foundation Model Reasoning: Calls Gemini with structured prompt specifications
   to compare price, availability, delivery terms, and validity.
4. Human-in-the-Loop Safeguard: Compares tradeoffs without picking a winner.

Usage:
    /opt/anaconda3/bin/python3 main.py
    /opt/anaconda3/bin/python3 main.py --prompt prompts/prompt_v1.1.txt --output results/reorder_reports_v1.1.md
"""

import os
import sys
import csv
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from google import genai
from google.genai import types

REFERENCE_DATE_DEFAULT = "2026-09-16"


def load_inventory(filepath):
    """Loads inventory items from CSV into a list of dicts."""
    items = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["current_stock"] = float(row["current_stock"])
            row["reorder_threshold"] = float(row["reorder_threshold"])
            items.append(row)
    return items


def load_quotations(filepath):
    """Loads supplier quotations from CSV into a dictionary grouped by item_id."""
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
    """
    DETERMINISTIC RULE:
    Returns True if current stock is strictly below the reorder threshold.
    """
    return current_stock < reorder_threshold


def format_quotations_table(quotes):
    """Formats list of quotation dicts into a markdown table for the LLM prompt."""
    headers = [
        "Quotation ID", "Supplier Name", "Unit Price (UGX)", 
        "Qty Available", "Delivery Terms", "Valid Until", "Notes"
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
            q.get("notes", "").strip() or "None"
        ]
        lines.append(" | ".join(row))
    return "\n".join(lines)


def build_comparison_payload(item, quotes, reference_date):
    """Constructs the user message payload containing item and quotation data."""
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


def call_gemini(client, model_name, system_instruction, user_content):
    """Calls the Gemini API using the official google-genai SDK."""
    response = client.models.generate_content(
        model=model_name,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,  # Low temperature for factual, deterministic comparisons
        )
    )
    return response.text


def main():
    parser = argparse.ArgumentParser(description="ProcurePrep UG – Reorder Evaluation Engine")
    parser.add_argument("--inventory", default="data/inventory.csv", help="Path to inventory CSV")
    parser.add_argument("--quotations", default="data/quotations.csv", help="Path to quotations CSV")
    parser.add_argument("--prompt", default="prompts/prompt_v1.0.txt", help="Path to system prompt file")
    parser.add_argument("--output", default="results/reorder_reports.md", help="Output markdown path")
    parser.add_argument("--date", default=REFERENCE_DATE_DEFAULT, help="Reference date (YYYY-MM-DD)")
    parser.add_argument("--items", nargs="+", default=None, help="Specific item IDs to process")
    parser.add_argument("--model", default="gemini-3.5-flash-lite", help="Gemini model identifier")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment or .env file.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if not os.path.exists(args.prompt):
        print(f"ERROR: Prompt file not found: {args.prompt}")
        sys.exit(1)

    with open(args.prompt, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    inventory = load_inventory(args.inventory)
    quotations = load_quotations(args.quotations)

    if args.items:
        inventory = [item for item in inventory if item["item_id"] in args.items]

    print(f"Loaded {len(inventory)} inventory item(s).")
    print(f"Prompt: {args.prompt} | Reference Date: {args.date} | Model: {args.model}")
    print("=" * 70)

    report_sections = [
        f"# ProcurePrep UG – Procurement Preparation Reports\n",
        f"**Operating Date:** {args.date}  ",
        f"**Prompt:** `{args.prompt}`  ",
        f"**Model:** `{args.model}`  \n",
        "---\n"
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

        # 1. Deterministic Reorder Evaluation in Code
        needs_reorder = check_reorder_need(curr_stock, threshold)

        if not needs_reorder:
            ok_count += 1
            status_text = (
                f"### STATUS: SUFFICIENT STOCK – NO REORDER NEEDED\n"
                f"- **Item:** {item_name} (`{item_id}`)\n"
                f"- **Current Stock:** {curr_stock:g} {unit} >= **Reorder Threshold:** {threshold:g} {unit}\n"
                f"- **Action:** Deterministic check passed. No supplier quotation comparison required.\n"
            )
            print(f"  --> [PASS] Stock sufficient. LLM call skipped.")
            report_sections.append(status_text + "\n---\n")
            continue

        reorder_count += 1
        deficit = threshold - curr_stock
        quotes = quotations.get(item_id, [])

        print(f"  --> [REORDER NEEDED] Deficit: {deficit:g} {unit}. Available quotes: {len(quotes)}")

        # 2. Edge Case: No Quotations On File
        if len(quotes) == 0:
            no_quotes_count += 1
            status_text = (
                f"### REORDER REQUIRED – NO SUPPLIER QUOTATIONS AVAILABLE\n"
                f"- **Item:** {item_name} (`{item_id}`)\n"
                f"- **Stock Level:** Current Stock: {curr_stock:g} {unit} | Reorder Threshold: {threshold:g} {unit} | Deficit: {deficit:g} {unit}\n"
                f"- **Action Required:** Reorder is urgently needed, but 0 quotations are on record. Store manager must solicit quotations from registered suppliers before comparison can take place.\n"
            )
            print(f"  --> [NO QUOTES] LLM call skipped; deterministic alert logged.")
            report_sections.append(status_text + "\n---\n")
            continue

        # 3. Quotations Present -> Call Foundation Model for Tradeoff Comparison
        user_content = build_comparison_payload(item, quotes, args.date)
        try:
            llm_report = call_gemini(client, args.model, system_instruction, user_content)
            print("  --> [SUCCESS] Comparison report generated by Gemini.")
            report_sections.append(llm_report.strip() + "\n\n---\n")
        except Exception as e:
            err_msg = f"  --> [ERROR] Gemini API call failed for {item_id}: {e}"
            print(err_msg)
            report_sections.append(f"### ERROR GENERATING REPORT FOR {item_id}\n`{e}`\n\n---\n")

        # Brief pause to respect API rate limits
        time.sleep(1)

    # Save outputs
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))

    print("\n" + "=" * 70)
    print(f"Batch run completed:")
    print(f"  - Total items evaluated: {len(inventory)}")
    print(f"  - Sufficient stock (LLM skipped): {ok_count}")
    print(f"  - Reorder needed (No quotes): {no_quotes_count}")
    print(f"  - Reorder needed (LLM compared): {reorder_count - no_quotes_count}")
    print(f"Output saved to: {args.output}")


if __name__ == "__main__":
    main()
