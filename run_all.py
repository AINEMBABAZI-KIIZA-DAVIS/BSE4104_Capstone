"""
ProcurePrep – Batch Runner
----------------------------
Runs all test cases automatically and writes results to a markdown file.

Usage:
    /opt/anaconda3/bin/python3 run_all.py              # baseline (no RAG)
    /opt/anaconda3/bin/python3 run_all.py --rag        # RAG-augmented

Optional flags:
    --checklist    checklist.txt       (default)
    --prompt       prompt_v1.txt       (default, ignored in --rag mode)
    --output       results_filled.md   (default)
    --rag                              run through rag_checker instead of bare Gemini
    --rag-prompt   prompt_v2.txt       (default when --rag is set)
    --rag-output   results_rag.md      (default when --rag is set)
    --submissions  1 2 3               (run specific submissions only)
"""

import os
import sys
import time
import argparse

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Parse arguments
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="ProcurePrep – Batch Runner")
parser.add_argument("--checklist",   default="checklist.txt",    help="Checklist file")
parser.add_argument("--prompt",      default="prompt_v1.txt",    help="System prompt file (baseline mode)")
parser.add_argument("--output",      default="results_filled.md", help="Output results file (baseline mode)")
parser.add_argument("--rag",         action="store_true",         help="Use RAG-augmented checker")
parser.add_argument("--rag-prompt",  default="prompt_v2.txt",    help="System prompt for RAG mode")
parser.add_argument("--rag-output",  default="results_rag.md",   help="Output file for RAG mode")
parser.add_argument("--submissions", nargs="+", type=int,
                    default=list(range(1, 11)),
                    help="Submission numbers to run (e.g. --submissions 1 2 3)")
args = parser.parse_args()

if args.rag:
    from src.rag_checker import rag_check
    effective_prompt_file = args.rag_prompt
    effective_output_file = args.rag_output
else:
    effective_prompt_file = args.prompt
    effective_output_file = args.output

# ---------------------------------------------------------------------------
# 2. API key
# ---------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    print("Run:  export GEMINI_API_KEY='your-key-here'")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. Read shared files
# ---------------------------------------------------------------------------
with open(args.checklist, "r") as f:
    checklist_text = f.read()

with open(effective_prompt_file, "r") as f:
    system_prompt = f.read()

# ---------------------------------------------------------------------------
# 4. Test case metadata (expected results for reference)
# ---------------------------------------------------------------------------
TEST_CASES = {
    1:  {"file": "submission_1.txt",  "expected": "None – all 8 items present",
         "description": "Fully complete submission"},
    2:  {"file": "submission_2.txt",  "expected": "Bid Security (Tender Bond)",
         "description": "Missing 1 item – Bid Security"},
    3:  {"file": "submission_3.txt",  "expected": "Reference Letters; Signed Cover Letter",
         "description": "Missing 2 items"},
    4:  {"file": "submission_4.txt",  "expected": "7 of 8 items missing (all except Financial Proposal)",
         "description": "Mostly empty – only Financial Proposal present"},
    5:  {"file": "submission_5.txt",  "expected": "CANNOT DETERMINE on most items",
         "description": "Ambiguous / vague descriptions"},
    6:  {"file": "submission_6.txt",  "expected": "CANNOT DETERMINE – Tax Clearance & Bid Security expired",
         "description": "Expired documents"},
    7:  {"file": "submission_7.txt",  "expected": "All 8 present (wrong tender ref – completeness only)",
         "description": "All docs present but wrong tender reference"},
    8:  {"file": "submission_8.txt",  "expected": "Reference Letters (only 1 of 2 provided)",
         "description": "Only one reference letter"},
    9:  {"file": "submission_9.txt",  "expected": "Signed Cover Letter (cover letter unsigned)",
         "description": "Cover letter present but unsigned"},
    10: {"file": "submission_10.txt", "expected": "CANNOT DETERMINE – conflicting/duplicate documents",
         "description": "Duplicate and conflicting documents"},
}

# ---------------------------------------------------------------------------
# 5. Gemini client
# ---------------------------------------------------------------------------
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------------------------
# 6. Run each test case
# ---------------------------------------------------------------------------
import json

# RAG and baseline runs use separate cache files so they never share entries.
CACHE_FILE = "cache_rag.json" if args.rag else "cache.json"
cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    except Exception:
        pass

results = {}

for tc_num in sorted(args.submissions):
    tc = TEST_CASES.get(tc_num)
    if not tc:
        print(f"[SKIP] TC-{tc_num:02d}: no test case defined")
        continue

    tc_str = str(tc_num)
    # RAG runs are never served from cache — retrieval is part of the evaluation.
    if not args.rag and tc_str in cache and "API ERROR" not in cache[tc_str]:
        print(f"\n{'='*60}")
        print(f"TC-{tc_num:02d}: {tc['description']}")
        print(f"[CACHED] Skipping API call, using saved result.")
        print("="*60)
        results[tc_num] = {"output": cache[tc_str], **tc}
        continue

    sub_file = tc["file"]
    if not os.path.exists(sub_file):
        print(f"[SKIP] TC-{tc_num:02d}: {sub_file} not found")
        results[tc_num] = {"error": f"{sub_file} not found", **tc}
        continue

    with open(sub_file, "r") as f:
        submission_text = f.read()

    user_message = f"""
CHECKLIST:
----------
{checklist_text}

TENDER SUBMISSION:
------------------
{submission_text}
"""

    print(f"\n{'='*60}")
    print(f"Running TC-{tc_num:02d}: {tc['description']} {'[RAG]' if args.rag else ''}")
    print(f"File: {sub_file}")
    print("="*60)

    try:
        if args.rag:
            # RAG path – retrieve, inject knowledge, generate.
            result = rag_check(
                submission_text=submission_text,
                checklist_text=checklist_text,
                system_prompt=system_prompt,
                tc_label=f"TC-{tc_num:02d}",
            )
            model_output = result["report"]
        else:
            # Baseline path – direct Gemini call with cache.
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            model_output = response.text
            # Save successful baseline result to cache immediately.
            cache[tc_str] = model_output
            with open(CACHE_FILE, "w") as f:
                json.dump(cache, f, indent=4)

        print(model_output)
        results[tc_num] = {"output": model_output, **tc}

    except Exception as e:
        error_msg = f"API ERROR: {e}"
        print(error_msg)
        results[tc_num] = {"output": error_msg, **tc}

    # Respect rate limits – pause between calls
    if tc_num != sorted(args.submissions)[-1]:
        time.sleep(5)

# ---------------------------------------------------------------------------
# 7. Write results_filled.md
# ---------------------------------------------------------------------------
mode_label = "RAG-Augmented" if args.rag else "Baseline"
model_label = "gemini-2.0-flash (RAG)" if args.rag else "gemini-3.5-flash-lite (baseline)"

md_lines = [
    f"# ProcurePrep – Test Results Log [{mode_label}] (Auto-generated)\n",
    "",
    f"**Mode:** {mode_label}  ",
    f"**Model:** {model_label}  ",
    f"**Prompt Version:** {effective_prompt_file}  ",
    f"**Checklist:** {args.checklist} (8 items)  ",
    "",
    "---",
    "",
    "## Results\n",
]

for tc_num in sorted(results.keys()):
    r = results[tc_num]
    md_lines.append(f"### TC-{tc_num:02d} – {r['description']}")
    md_lines.append(f"**File:** `{r['file']}`  ")
    md_lines.append(f"**Expected Missing:** {r['expected']}  ")
    md_lines.append("")
    md_lines.append("**Model Output:**")
    md_lines.append("```")
    md_lines.append(r.get("output", r.get("error", "N/A")))
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

with open(effective_output_file, "w") as f:
    f.write("\n".join(md_lines))

print(f"\n✅ Done! Results written to: {effective_output_file}")
print(f"   {len(results)} test case(s) processed.")
