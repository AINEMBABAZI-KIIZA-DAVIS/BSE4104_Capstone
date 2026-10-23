# Known Limitations (Week 8)

1. **RAG false flags (F-01) and partial answers (F-02)** — Mitigated. The failure did not recur in one live re-test (n=1, temperature 0.1); residual variability remains. Evidence: `results/live_rag_retest.md` (2026-10-18, Week 8 hardening — not a ninth week). Note that for RQ-10 the answer's second citation (`supplier_code_of_conduct_addendum.txt`) was only loosely relevant.
2. **Small 12-chunk corpus** — `top_k=4` is often noisy for operational questions. Prices and stock must be read from CSV tools.
3. **Human approval is CLI-only** — a headless or web deployment needs an equivalent confirmation UI.
4. **Memory is a local JSON file** — not multi-user, not encrypted at rest, 90-day prune only.
5. **MCP adapter is in-process** — not a networked Model Context Protocol server.
6. **No purchase order, payment or supplier award** — by charter. The agent stops at DRAFT / PENDING_APPROVAL.
7. **Chroma index is not in git** — RAG requires `python src/embed_store.py` after clone.
8. **Gemini is required** for Week 2 comparison, Week 3 RAG and Week 4 live function calling. The Week 5–7 bounded suite runs without it.
9. **The 32-scenario suite tests the deterministic layer (reorder gate, validation, guardrails, roles, confirmation, stop conditions). It does not evaluate LLM comparison quality. LLM behaviour is covered by the 10-case Week 2 table and the 15-question Week 3 RAG set; a live Gemini scenario set is future work.**
