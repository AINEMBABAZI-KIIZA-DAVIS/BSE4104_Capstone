"""
ProcurePrep – Week 2 baseline
--------------------------------
Reads a procurement checklist and a tender submission from text files,
builds a prompt, sends it to the Gemini API, and prints the response.

Usage:
    export GEMINI_API_KEY="your-key-here"
    python main.py --checklist checklist.txt --submission submission_1.txt

The model is used ONLY as a completeness checker.
It never scores, ranks, or recommends approval/rejection.
"""

import os
import sys
import argparse
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# 1. Parse command-line arguments
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="ProcurePrep – AI completeness checker")
parser.add_argument("--checklist",  default="checklist.txt",   help="Path to the checklist file")
parser.add_argument("--submission", default="submission_1.txt", help="Path to the submission file")
parser.add_argument("--prompt",     default="prompt_v1.txt",   help="Path to the system prompt file")
args = parser.parse_args()


# ---------------------------------------------------------------------------
# 2. Read the API key from the environment
# ---------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    print("Run:  export GEMINI_API_KEY='your-key-here'")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 3. Read the three input files
# ---------------------------------------------------------------------------
with open(args.checklist, "r") as f:
    checklist_text = f.read()

with open(args.submission, "r") as f:
    submission_text = f.read()

with open(args.prompt, "r") as f:
    system_prompt = f.read()


# ---------------------------------------------------------------------------
# 4. Build the user message that combines checklist + submission
# ---------------------------------------------------------------------------
user_message = f"""
CHECKLIST:
----------
{checklist_text}

TENDER SUBMISSION:
------------------
{submission_text}
"""


# ---------------------------------------------------------------------------
# 5. Configure the Gemini client and choose the model
# ---------------------------------------------------------------------------
client = genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# 6. Send the request and print the response
# ---------------------------------------------------------------------------
print("=" * 60)
print(f"Checklist : {args.checklist}")
print(f"Submission: {args.submission}")
print("=" * 60)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=user_message,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
    ),
)

print(response.text)
print("=" * 60)
