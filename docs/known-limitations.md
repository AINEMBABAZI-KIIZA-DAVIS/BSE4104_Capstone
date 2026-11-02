# Known Limitations (Week 8)

F-01 and F-02 (false missing-terms flag, and a partial RAG question answered as “cannot determine”) were improved in prompt_rag_v1.0.txt. We re-ran those two cases once on 18 October, temperature 0.1. They did not come back on that run. That is n=1, so the model can still do it again. RQ-10 also cited supplier_code_of_conduct_addendum.txt in a way that was only loosely relevant. See results/live_rag_retest.md.

The knowledge base is twelve short documents. top_k=4 is noisy when the question is really about a price or a stock figure. Those numbers have to come from the CSV tools.

Approval is a y/n in the terminal. There is no web page for it.

Memory is one json file on disk. It is not multi-user and it is not encrypted. Old item rows are dropped after 90 days.

The MCP piece is a Python wrapper, not a server another program can connect to.

We do not create purchase orders, pay anyone, or award a supplier. That is the charter. The agent stops at DRAFT or PENDING_APPROVAL.

chroma_db/ is not in git. After clone you need python src/embed_store.py (and a Gemini key) if you want RAG.

Gemini is needed for week 2 reports, week 3 RAG, and the week 4 live tool demo. Weeks 5–7 run without a key.

The 32 scenarios check reorder gating, validation, allow-list, roles, confirmation, and stop reasons. They do not score how good the Gemini comparison text is. That is still the week 2 table (10 cases) and the week 3 RAG set (15 questions). A live Gemini scenario pack is future work.
