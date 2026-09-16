"""
rag_checker.py – RAG-augmented completeness checker for ProcurePrep.

Exposes:
    rag_check(submission_text, checklist_text, system_prompt) -> dict
        Returns: { "report": str, "chunks_used": list[dict] }

Run from the project root:
    /opt/anaconda3/bin/python3 src/rag_checker.py --submission submission_1.txt
"""

import os
import sys
import time
import argparse

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
sys.path.insert(0, PROJECT_ROOT)

from google import genai
from google.genai import types
from src.retrieve import retrieve_relevant_chunks

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

LOG_FILE = os.path.join(PROJECT_ROOT, "retrieval_log.txt")


def _build_knowledge_block(chunks: list[dict]) -> str:
    """Format retrieved chunks into a RELEVANT KNOWLEDGE block."""
    lines = ["RELEVANT KNOWLEDGE:", "-------------------"]
    for chunk in chunks:
        lines.append(f"[Source: {chunk['source_filename']}]")
        lines.append(chunk["text"])
        lines.append("")
    return "\n".join(lines)


def _log_retrieval(tc_label: str, chunks: list[dict]) -> None:
    """Append a retrieval audit entry to retrieval_log.txt."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"TC: {tc_label}\n")
        for i, c in enumerate(chunks, 1):
            f.write(
                f"  [{i}] {c['source_filename']} "
                f"(chunk {c['chunk_index']}, score={c['score']})\n"
            )
        f.write(f"{'='*60}\n")


def rag_check(
    submission_text: str,
    checklist_text: str,
    system_prompt: str,
    top_k: int = 4,
    tc_label: str = "unknown",
) -> dict:
    """
    Run a RAG-augmented completeness check.

    Returns a dict with:
        report       – the model's COMPLETENESS CHECK REPORT string
        chunks_used  – list of chunk dicts returned by retrieve_relevant_chunks
    """
    chunks = retrieve_relevant_chunks(submission_text, top_k=top_k)

    # Log to stdout for immediate visibility.
    print(f"  [RAG] Retrieved {len(chunks)} chunk(s):")
    for c in chunks:
        print(f"        {c['source_filename']} (chunk {c['chunk_index']}, score={c['score']})")

    # Persist to audit log.
    _log_retrieval(tc_label, chunks)

    knowledge_block = _build_knowledge_block(chunks)

    user_message = f"""{knowledge_block}

CHECKLIST:
----------
{checklist_text}

TENDER SUBMISSION:
------------------
{submission_text}
"""

    MAX_RETRIES = 3
    BACKOFF = 10  # seconds; doubles each retry

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            return {
                "report": response.text,
                "chunks_used": chunks,
            }
        except Exception as e:
            err_str = str(e)
            if ("503" in err_str or "429" in err_str) and attempt < MAX_RETRIES:
                wait = BACKOFF * (2 ** (attempt - 1))
                print(f"  [RETRY {attempt}/{MAX_RETRIES}] {e} – waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("Exceeded max retries for Gemini generation call.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ProcurePrep RAG checker – single submission")
    parser.add_argument("--submission", default="submission_1.txt", help="Submission file")
    parser.add_argument("--checklist",  default="checklist.txt",    help="Checklist file")
    parser.add_argument("--prompt",     default="prompt_v2.txt",    help="System prompt file")
    args = parser.parse_args()

    for path, label in [
        (args.submission, "submission"),
        (args.checklist,  "checklist"),
        (args.prompt,     "prompt"),
    ]:
        full = os.path.join(PROJECT_ROOT, path)
        if not os.path.exists(full):
            print(f"ERROR: {label} file not found: {full}")
            sys.exit(1)

    with open(os.path.join(PROJECT_ROOT, args.submission), "r") as f:
        submission_text = f.read()
    with open(os.path.join(PROJECT_ROOT, args.checklist), "r") as f:
        checklist_text = f.read()
    with open(os.path.join(PROJECT_ROOT, args.prompt), "r") as f:
        system_prompt = f.read()

    print("=" * 60)
    print(f"Submission : {args.submission}")
    print(f"Prompt     : {args.prompt}")
    print("=" * 60)

    result = rag_check(
        submission_text=submission_text,
        checklist_text=checklist_text,
        system_prompt=system_prompt,
        tc_label=args.submission,
    )

    print()
    print(result["report"])
    print("=" * 60)
