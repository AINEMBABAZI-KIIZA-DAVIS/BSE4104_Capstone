# Known Limitations (Week 8)

1. **RAG false flags (F-01) and partial answers (F-02) resolved in live re-test** — verified live against Gemini in Week 9 (`results/week9_rag_rerun.md`): Q-103 no longer triggers false `[MISSING TERMS]` alerts, and RQ-10 now produces a grounded partial answer citing negotiation guidelines rather than an uninformative refusal.
2. **Small 12-chunk corpus** — `top_k=4` is often noisy for operational questions. Prices and stock must be read from CSV tools.
3. **Human approval is CLI-only** — a headless or web deployment needs an equivalent confirmation UI.
4. **Memory is a local JSON file** — not multi-user, not encrypted at rest, 90-day prune only.
5. **MCP adapter is in-process** — not a networked Model Context Protocol server.
6. **No purchase order, payment or supplier award** — by charter. The agent stops at DRAFT / PENDING_APPROVAL.
7. **Chroma index is not in git** — RAG requires `python src/embed_store.py` after clone.
8. **Gemini is required** for Week 2 comparison, Week 3 RAG and Week 4 live function calling. The Week 5–7 bounded suite runs without it.
