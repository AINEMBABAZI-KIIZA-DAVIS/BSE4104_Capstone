# ProcurePrep UG — Demonstration outline

About 12–15 minutes, then questions. Show the running program, one log or table, and one thing that went wrong. Do not only show ITEM-004 working.

## 1. Problem (1–2 min)

Storekeeper / owner in Uganda preparing one reorder, not running PPDA e-procurement. Gemini writes comparison text. Python decides whether stock is below the line, whether a quote is expired, and whether routing is allowed.

## 2. How it grew (2 min)

Week 2: model and two prompts. Week 3: RAG over twelve files. Week 4: four tools. Week 5: the loop. Week 6: state plus a small memory file. Week 7: 32 tests and guardrails.

## 3. Live success (4 min)

python src/bounded_agent.py --item ITEM-004

Expect stock 5 against 25 (deficit 20), quotes Q-107 and Q-108, draft on Q-107, status DRAFT. Do not route unless we ask.

## 4. Evidence (2 min)

Open results/week7_evaluation.md (32/32) or one line in results/traces/week7_eval.jsonl. Say clearly that those 32 cases test the Python layer, not Gemini’s writing. Gemini evidence is still week 2 and week 3.

## 5. Failure (2 min)

python src/bounded_agent.py --item ITEM-005

Q-109 is expired, the tool says QUOTATION_EXPIRED, then it drafts Q-110. If they ask about RAG, F-01/F-02 were prompt fixes; one live re-test on 18 Oct did not repeat them; the model can still vary.

## 6. Guardrails (1–2 min)

Unknown tools are rejected. award_contract is not a tool. Routing needs y. Strings about ignoring instructions or approving payment are blocked. End with: we did not create a purchase order.

Checklist before the slot: venv on, tests green, ITEM-004, ITEM-005, one results file visible.
