# BSE4104 AI-Native & Agentic Engineering Capstone

## Week 3 Progress Report

**Project:** ProcurePrep UG — AI-Native SME Procurement-Preparation Agent  
**Week:** Week 3  
**Week Ending:** 18 September 2026

### 1. Work Completed

During Week 3, the team added retrieval-augmented generation on top of the Week 2 deterministic reorder gate. A twelve-document SME procurement corpus was registered, ingested, embedded with Gemini embeddings and stored in ChromaDB.

`src/rag_reorder_checker.py` retrieves top-k chunks, injects a RELEVANT KNOWLEDGE block and requires a SOURCES USED section. Fifteen policy questions (answerable, partially answerable and deliberately unanswerable) were evaluated, plus one grounded quotation-comparison run on ITEM-001.

`tender_checklist.txt` was removed from the active corpus because it belongs to the archived tender-checker use case.

### 2. Key Engineering Decisions

RAG is used only after the reorder gate and only when quotations exist. Retrieval does not decide whether to reorder.

The corpus was limited to internal SME policy, templates and evaluation criteria. External tender-submission material stays in `legacy/`.

The prompt contract requires source filenames so unsupported answers can be refused instead of invented.

### 3. Challenges

Three retrieval or grounding failures were documented. The model sometimes raised `[MISSING TERMS]` when delivery method was present but transport cost was unclear. A dispute-resolution question was treated as fully unanswerable even though the corpus names it as a negotiation topic. A small twelve-chunk corpus also returns noisy top-4 hits for operational-data questions, though the model still refused those correctly.

### 4. Repository and Task Evidence

**GitHub Repository:** https://github.com/AINEMBABAZI-KIIZA-DAVIS/BSE4104_Capstone  
**ClickUp Project:** https://app.clickup.com/1200430000003901/v/li/1200430000006616  
**Architecture Evidence:** `submission/WEEK3/RAG_Architecture.jpg`

### 5. Individual Contributions

| Member | Responsibility | Evidence |
| :--- | :--- | :--- |
| Nasiwa Hafswa | Corpus register and provenance | `docs/corpus_register.md`, `knowledge/` |
| Armand Shematsi | RAG architecture and pipeline | `src/ingest.py`, `src/embed_store.py`, `src/retrieve.py` |
| Ainembabazi Kiiza Davis | RAG prompt and grounded comparison | `prompts/prompt_rag_v1.0.txt`, `src/rag_reorder_checker.py` |
| Alvin Mayega Kenneth | 15-question RAG evaluation and failure notes | `results/week3_rag_evaluation.md` |
| All members | Documentation / GitHub / ClickUp | Week 3 submission pack |

### 6. Plan for Week 4

During Week 4, the team will define at least two callable tools with schemas and failure behaviour, implement function calling, retrieve live application data or create a draft requisition, test missing, unauthorized and unavailable cases, and require human approval before routing a requisition.

### 7. Week 3 Status

**Overall status:** On track

The application now answers from a controlled, cited corpus. Deterministic reorder control is unchanged. Documented retrieval failures will inform Week 4 prompt and tool validation work.
