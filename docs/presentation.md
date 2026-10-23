# ProcurePrep UG — Final Demonstration Outline

**Duration:** 12–15 minutes plus questions  
**Rule:** Show the engineered system, one evidence view and one real failure. Do not only play a happy path.

---

## Slide 1 — Problem and user (1–2 min)

SME procurement officer / owner-manager in Uganda. Task: prepare a reorder, not run a national e-procurement platform. AI compares quotes and drafts. Python owns thresholds, validation and approval.

## Slide 2 — Architecture progression (2 min)

Week 2 model + prompts → Week 3 RAG → Week 4 tools → Week 5 bounded loop → Week 6 state/memory → Week 7 eval/guardrails.

## Slide 3 — Live success (4 min)

```
python src/bounded_agent.py --item ITEM-004
```

Show: deficit 20 cartons, quotes Q-107 / Q-108, DRAFT on cheapest valid Q-107, no route unless asked.

## Slide 4 — Evidence view (2 min)

Open `results/week7_evaluation.md` (32/32) or a JSONL line from `results/traces/week7_eval.jsonl` (session, tool, latency_ms, outcome). The 32-scenario suite tests the deterministic layer (reorder gate, validation, guardrails, roles, confirmation, stop conditions). It does not evaluate LLM comparison quality. LLM behaviour is covered by the 10-case Week 2 table and the 15-question Week 3 RAG set; a live Gemini scenario set is future work.

## Slide 5 — Real failure and recovery (2 min)

```
python src/bounded_agent.py --item ITEM-005
```

Q-109 expired → `QUOTATION_EXPIRED` → re-plan Q-110. Also mention F-01/F-02 prompt mitigations and live re-test (n=1, temp 0.1) with residual model variability if asked about RAG limits.

## Slide 6 — Guardrails and lessons (1–2 min)

Injection and award/payment strings blocked. Unknown tools rejected. Routing needs a human. Lesson: keep spend decisions out of the model.

---

### Demo checklist

- [ ] venv active; `python -m unittest discover -s tests -q` green  
- [ ] ITEM-004 success  
- [ ] ITEM-005 recovery  
- [ ] One eval or trace file on screen  
- [ ] State clearly: no purchase order was created  
