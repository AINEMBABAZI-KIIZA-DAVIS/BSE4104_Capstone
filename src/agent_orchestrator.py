"""
agent_orchestrator.py – Gemini function-calling orchestration for ProcurePrep Week 4.

The model decides which tools to invoke based on the user task. Low-risk read/write
draft tools run automatically; route_requisition_for_approval requires explicit
human confirmation before execution.

Usage:
    python src/agent_orchestrator.py "Check quotations for ITEM-004 and draft a requisition for 20 units using the cheapest valid quote. Requested by Jane Okello."
    python src/agent_orchestrator.py --demo --transcript results/week4_tool_demo.md
"""

from __future__ import annotations

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from google import genai
from google.genai import types

from src.tools import (
    CONFIRMATION_REQUIRED_TOOLS,
    TOOL_REGISTRY,
    create_requisition_draft,
    dispatch_tool,
    get_reorder_status,
    get_supplier_quotations,
    route_requisition_for_approval,
)

# Week 2 rebuild finalized model (see main.py, docs/model-selection-note.md)
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_TOOL_TURNS = 8

SYSTEM_INSTRUCTION = """You are ProcurePrep, an SME procurement preparation assistant for Uganda.

You have tools to:
- get_reorder_status: check deterministic reorder need for an item
- get_supplier_quotations: fetch current supplier quotes from application data
- create_requisition_draft: create a DRAFT requisition (does NOT approve or spend)
- route_requisition_for_approval: route a DRAFT to a human approver (high-impact; may require human confirmation)

Use tools based on the user's task. When comparing quotations, prefer valid (non-expired) quotes.
Operating reference date for validity is 2026-09-16.
Do not invent quotation IDs or prices — always retrieve them with get_supplier_quotations first.
After creating a draft, summarize the requisition details for the human reviewer.
Only call route_requisition_for_approval when the user explicitly asks to route/submit for approval.
"""


def build_tool_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[
            get_supplier_quotations,
            get_reorder_status,
            create_requisition_draft,
            route_requisition_for_approval,
        ],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        temperature=0.1,
    )


def _log(transcript: list[str], message: str) -> None:
    print(message)
    transcript.append(message)


def _confirm_tool_execution(tool_name: str, args: dict[str, Any], auto_confirm: bool) -> bool:
    print("\n" + "=" * 70)
    print("HUMAN APPROVAL REQUIRED — higher-impact tool staged")
    print(f"  Tool: {tool_name}")
    print(f"  Arguments: {json.dumps(args, indent=2)}")
    print("=" * 70)
    if auto_confirm:
        print("[demo mode] Auto-confirmed by operator.")
        return True
    answer = input("Execute this tool? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def run_agent_turn(
    client: genai.Client,
    model: str,
    contents: list[Any],
    config: types.GenerateContentConfig,
    transcript: list[str],
    *,
    auto_confirm: bool = False,
    confirm_callback: Callable[[str, dict[str, Any]], bool] | None = None,
) -> tuple[str, list[Any]]:
    """Run tool-calling loop until model returns text or max turns."""
    confirm_fn = confirm_callback or (
        lambda name, args: _confirm_tool_execution(name, args, auto_confirm)
    )

    for turn in range(MAX_TOOL_TURNS):
        _log(transcript, f"\n--- Model turn {turn + 1} ---")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        if response.function_calls:
            for fc in response.function_calls:
                name = fc.name
                args = dict(fc.args) if fc.args else {}
                _log(transcript, f"\n[TOOL CALL] {name}({json.dumps(args)})")

                if name in CONFIRMATION_REQUIRED_TOOLS:
                    if not confirm_fn(name, args):
                        result = {
                            "error": "HUMAN_DECLINED",
                            "message": "Human reviewer declined to execute this tool.",
                        }
                        _log(transcript, f"[SKIPPED] {name} — human declined")
                    else:
                        result = dispatch_tool(name, args)
                        _log(transcript, f"[TOOL RESULT] {json.dumps(result, indent=2)}")
                else:
                    result = dispatch_tool(name, args)
                    _log(transcript, f"[TOOL RESULT] {json.dumps(result, indent=2)}")

                contents.append(response.candidates[0].content)
                fn_response_kwargs: dict[str, Any] = {
                    "name": name,
                    "response": {"result": result},
                }
                if getattr(fc, "id", None):
                    fn_response_kwargs["id"] = fc.id
                contents.append(
                    types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(**fn_response_kwargs)],
                    )
                )
            continue

        text = response.text or ""
        _log(transcript, f"\n[MODEL RESPONSE]\n{text}")
        return text, contents

    return "[Max tool turns reached without final response.]", contents


def run_agent(
    user_message: str,
    *,
    model: str = DEFAULT_MODEL,
    auto_confirm: bool = False,
    confirm_callback: Callable[[str, dict[str, Any]], bool] | None = None,
    api_client: genai.Client | None = None,
) -> tuple[str, list[str]]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_client is None and not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = api_client or genai.Client(api_key=api_key)
    config = build_tool_config()
    contents: list[Any] = [user_message]
    transcript: list[str] = [
        f"Model: {model}",
        f"User: {user_message}",
    ]

    try:
        final_text, _ = run_agent_turn(
            client,
            model,
            contents,
            config,
            transcript,
            auto_confirm=auto_confirm,
            confirm_callback=confirm_callback,
        )
    except Exception as exc:
        transcript.append(f"\n[ORCHESTRATOR ERROR] {type(exc).__name__}: {exc}")
        raise AgentOrchestratorError(str(exc), transcript=transcript) from exc

    return final_text, transcript


class AgentOrchestratorError(Exception):
    def __init__(self, message: str, transcript: list[str] | None = None):
        super().__init__(message)
        self.transcript = transcript or []


def main() -> None:
    parser = argparse.ArgumentParser(description="ProcurePrep Week 4 agent orchestrator")
    parser.add_argument("message", nargs="?", default=None, help="User task message")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--demo", action="store_true", help="Run built-in demo prompt")
    parser.add_argument("--auto-confirm", action="store_true", help="Auto-approve gated tools (demo/transcript)")
    parser.add_argument("--transcript", default=None, help="Write full transcript to this markdown file")
    args = parser.parse_args()

    if args.demo:
        user_message = (
            "For ITEM-004 (Thermal POS Receipt Rolls): use get_reorder_status and "
            "get_supplier_quotations, then create a DRAFT requisition for 20 cartons "
            "using the cheapest quotation that is still valid on 2026-09-16. "
            "Requested by Jane Okello."
        )
    elif args.message:
        user_message = args.message
    else:
        parser.error("Provide a message or use --demo")

    print(f"ProcurePrep Agent | model={args.model}")
    print("=" * 70)

    final, transcript = run_agent(
        user_message,
        model=args.model,
        auto_confirm=args.auto_confirm,
    )

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(final)

    if args.transcript:
        out = Path(args.transcript)
        out.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(transcript)
        out.write_text(
            f"# ProcurePrep Week 4 – Tool Demo Transcript\n\n"
            f"**Date:** {datetime.now().isoformat(timespec='seconds')}  \n"
            f"**Model:** `{args.model}`  \n"
            f"**Prompt:** {user_message}\n\n"
            f"## Transcript\n\n```\n{body}\n```\n\n"
            f"## Final Model Response\n\n{final}\n",
            encoding="utf-8",
        )
        print(f"\nTranscript saved to: {out}")


if __name__ == "__main__":
    main()
