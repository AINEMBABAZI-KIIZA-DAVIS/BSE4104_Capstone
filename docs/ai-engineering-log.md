# AI Engineering Log — ProcurePrep UG

Built from git history (`git log --date=short`), prompt files, `docs/evaluation/failure-catalogue.md`, weekly packs under `docs/weekly-reports/`, and evaluation files under `results/`. Personal prompting sessions that are not in git are marked TODO (team to confirm).

The BSE4104 brief (section 6) requires a concise AI Engineering Log for material AI-assisted decisions. There is no Week 9 in that brief.

Human-responsibility line: the team owns the code, tests and decisions; the agent never authorizes spend.

| Date | Tool (from repo evidence) | What was generated or committed | What the team changed or rejected | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| 2026-09-07 | TODO (team to confirm) | Commit `f74074d` Initial commit | TODO (team to confirm) | TODO (team to confirm) |
| 2026-09-11 | TODO (team to confirm) | Commit `be06db2` Initial commit; merge `5329e0a` | TODO (team to confirm) | TODO (team to confirm) |
| 2026-09-16 | Gemini API (`gemini-3.5-flash-lite` in `main.py`) | Week 3 RAG: commit `bd4470f`. Prompts `prompt_v1.0.txt` / `prompt_v1.1.txt` dated 2026-09-16 in `prompts/prompt_version_history.md`. Week 2 rebuild commit `4664f46`. Legacy tender files moved in `a980485`. | Tender-checker / `tender_checklist.txt` isolated in `legacy/` as charter drift. | Week 2 table in `results/week2_evaluation.md`; Week 3 table in `results/week3_rag_evaluation.md` (that file records that not all 15 questions were live in Week 3). |
| 2026-09-23 | No Gemini in the bounded-agent traces | `results/week5_execution_traces.md` records ITEM-004 success, ITEM-002 early stop, ITEM-005 Q-109 `QUOTATION_EXPIRED` then Q-110 `DRAFT`. | Planner still proposed expired Q-109 first; Python rejected it (F-05). | `tests/test_bounded_agent.py`; Trace 3 in `results/week5_execution_traces.md`. |
| 2026-10-01 | None in `scripts/run_week7_evaluation.py` | `results/week7_evaluation.md` header date 2026-10-01T14:31:56; 32/32 recorded in that file. | N/A | Re-run of `python scripts/run_week7_evaluation.py` (deterministic runner; does not call Gemini). |
| 2026-10-16 | Gemini not required for Week 7 suite | Week 7 progress report `docs/weekly-reports/week7.md` (week ending 16 October 2026): guardrails, failure catalogue, 32 scenarios. | Live F-01/F-02 re-test was still pending at that freeze. | `tests/test_guardrails.py`; `results/week7_evaluation.md`. |
| 2026-10-18 | Gemini API `gemini-3.5-flash-lite` via `src/rag_reorder_checker.py` | Live RAG verification now stored as `results/live_rag_retest.md` (renamed from a file that had been labelled Week 9). Commits `50ff3eb`, `004ac03`, `aff262d`, plus report-length commits `d6c9bbf` and `8a80003`. | F-01/F-02 treated as mitigated with residual risk, not as permanently gone. Week 3 “13/15” summary called out as not matching the table recount. TC-10 mislabel of working capital documented rather than rewritten as a live pass. | `results/live_rag_retest.md`; failure catalogue re-test notes. |
| 2026-10-23 | Cursor coding agent (Week 8 hardening) | AI-use declaration and this log; wording alignment to the 8-week brief; removal of an optional n8n/API path that is not in the assignment. | n8n / Gmail Send-and-Wait is out of scope for this capstone. Do not invent a ninth week. | `python -m unittest discover -s tests -q`; `python scripts/run_week7_evaluation.py`. |

## Prompt files and versions (from `prompts/`)

| File | Role | Target model recorded in-repo |
| :--- | :--- | :--- |
| `prompts/prompt_v1.0.txt` | Week 2 baseline comparison | `gemini-3.5-flash-lite` (`prompts/prompt_version_history.md`) |
| `prompts/prompt_v1.1.txt` | Risk-flag comparison | `gemini-3.5-flash-lite` |
| `prompts/prompt_rag_v1.0.txt` | RAG comparison + policy Q&A; F-01/F-02 contract | default CLI `gemini-3.5-flash-lite` in `src/rag_reorder_checker.py` |

## Failure catalogue (from `docs/evaluation/failure-catalogue.md`)

| ID | Class | Status in catalogue |
| :--- | :--- | :--- |
| F-01 | Prompt | Mitigated. The failure did not recur in one live re-test (n=1, temperature 0.1); residual variability remains. |
| F-02 | Prompt | Same status sentence as F-01. |
| F-03 | Architecture | Prices stay in CSV tools, not RAG. |
| F-04 | Code | Gemini SDK `id` — fixed in orchestrator. |
| F-05 | Code | Expired-quote recovery — ITEM-005. |
| F-06 | Code | `retrieve` import no longer `sys.exit` on missing key. |

## Not in the repository

- Exact chat logs of who prompted Cursor/Antigravity, and which suggestions were clicked: TODO (team to confirm).
- Whether any production (non-synthetic) quotes were ever pasted into Gemini: TODO (team to confirm). Default data files are the CSVs in `data/`.
- Drive copies of the Word/PowerPoint packs: TODO (team to confirm) after a human replaces them.
