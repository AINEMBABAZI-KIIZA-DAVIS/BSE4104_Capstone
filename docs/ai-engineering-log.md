# AI engineering log — ProcurePrep UG

Notes of where a model was actually in the loop, taken from git dates, the prompt files, the failure catalogue, and the results folders. The brief asks for this. We did not keep chat exports.

We own the code and tests. The agent does not spend money.

| When | What we used | What came out | What we changed | How we checked |
| :--- | :--- | :--- | :--- | :--- |
| 7–11 Sep 2026 | Gemini later in main.py; early repo setup | First commits (f74074d, be06db2) and a merge (5329e0a) | Early tender-checker direction was the wrong charter | TODO if anyone still has the original chats |
| 16 Sep 2026 | gemini-3.5-flash-lite in main.py | Week 2 rebuild (4664f46), prompts v1.0 and v1.1, week 3 RAG (bd4470f). Tender files moved to legacy/ (a980485) | Stopped using tender_checklist.txt | results/week2_evaluation.md; week 3 table (not all 15 questions were live that week) |
| 23 Sep 2026 | No Gemini in the bounded-agent traces | ITEM-004 draft, ITEM-002 early stop, ITEM-005 Q-109 then Q-110 (results/week5_execution_traces.md) | Left the first draft attempt on the cheapest quote so expiry is visible | tests/test_bounded_agent.py |
| 1 Oct 2026 | None in scripts/run_week7_evaluation.py | 32/32 in results/week7_evaluation.md | — | Re-run the same script |
| 16 Oct 2026 | Still no Gemini in the 32 suite | Guardrails, catalogue, week 7 report | F-01/F-02 not re-run live yet | tests/test_guardrails.py |
| 18 Oct 2026 | gemini-3.5-flash-lite via src/rag_reorder_checker.py | results/live_rag_retest.md (that file used to be named as if there were a week 9; there is not) | Did not call F-01/F-02 “gone forever”. Noted the week 3 “13/15” line does not match the table. Left the TC-10 working-capital mislabel as a lesson | results/live_rag_retest.md |
| 23 Oct 2026 | Gemini still only in the comparison/RAG/embed path | Final report, README, this log | Did not add extra workflow tools the brief never asked for | python -m unittest discover -s tests -q; python scripts/run_week7_evaluation.py |

Prompts: prompt_v1.0.txt, prompt_v1.1.txt, prompt_rag_v1.0.txt, all aimed at gemini-3.5-flash-lite.

Failures F-01 and F-02: prompt. F-03: prices via CSV, not RAG. F-04, F-05, F-06: code.

We do not have the chat logs, and the CSVs are synthetic.
