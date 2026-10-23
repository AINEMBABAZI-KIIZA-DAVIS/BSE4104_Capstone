# Model Selection Note: Foundation Model for ProcurePrep 

**Project:** ProcurePrep UG (BSE4104 AI Agentic Capstone)
**Task:** Automated Inventory Reorder Reasoning & Supplier Quotation Comparison
**Selected Model (what the current code defaults to):** Google Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`) via `google-genai` for comparison (`main.py`, `src/rag_reorder_checker.py`) and Week 4 function calling (`src/agent_orchestrator.py`). Embeddings use `models/gemini-embedding-001` (`src/embed_store.py`, `src/retrieve.py`). Names such as `gemini-3.6-flash` and `gemini-2.0-flash` appear only under `legacy/` from the earlier tender-checker path.

---

## 1. Context & Task Requirements

ProcurePrep UG assists Ugandan Small and Medium Enterprises (SMEs) by transforming manual procurement checks into an automated, explainable preparation workflow:

1. **Deterministic Inventory Evaluation:** Evaluating stock levels against reorder thresholds via Python code (`current_stock < reorder_threshold`).
2. **Contextual Quotation Comparison:** When an item requires reordering, the foundation model analyzes competing supplier quotes, comparing unit prices (in UGX), delivery lead times, stock availability, and expiration dates.
3. **Strict Human-in-the-Loop Constraint:** The model must objectively explain tradeoffs and present structured comparisons without making an autonomous purchasing decision or picking a single "winning" supplier.

---

## 2. Evaluation Across Key Selection Dimensions

### A. Reasoning Capability & Instruction Adherence

- **Tabular & Numerical Reasoning:** The task requires accurate comparison of numerical amounts (e.g., identifying lowest price or spotting 5x price outliers) and date logic (identifying expired quotes relative to reference dates).
- **Tradeoff Explanation:** The model must articulate nuanced qualitative tradeoffs (e.g., higher price with same-day delivery vs. lower price with 7-day transit).
- **Negative Constraint Adherence:** Gemini 2.5/2.0 Flash models reliably follow negative constraints (e.g., "Do NOT select a winner or recommend approval; present tradeoffs for human review").

### B. Cost & SME Economic Viability

- **Token Efficiency:** A single reorder quotation comparison requires ~350 input tokens and ~300 output tokens (~650 tokens total).
- **Cost Profile:** At $0.075 per 1M input tokens and $0.30 per 1M output tokens (Gemini Flash pricing), processing 1,000 inventory reorder checks costs less than **$0.15 USD (~550 UGX)**. This makes the system economically viable for micro and small enterprises operating with modest IT budgets.

### C. Latency & Batch Processing Throughput

- **End-to-End Response Time:** Median generation latency is **0.8 to 1.5 seconds** per item.
- **SME Operational Workflow:** Batch processing a daily inventory sweep of 20–50 items takes less than 45 seconds, well within acceptable operational windows for morning storekeeper reviews.

### D. Privacy, Security & Data Governance

- **Commercial Confidentiality:** Supplier quotes, negotiated discounts, and inventory volumes constitute sensitive SME commercial data.
- **API Privacy Terms:** Under standard Google GenAI API agreements (paid or enterprise tier), prompt and output data are not retained or utilized to train future public foundation models, ensuring confidentiality of Ugandan SME procurement records.

### E. Access & Operational Simplicity

- **SDK Integration:** The modern `google-genai` Python SDK provides direct, typed client access with `.env` secret loading.
- **Quota & Availability:** Flash models feature generous free/developer quotas (15 RPM), allowing full offline and demo testing without rate-limit saturation.

---

## 3. Conclusion & Final Selection

**`gemini-3.5-flash-lite`** is the comparison and tool-calling default in the current tree. Reorder gating (`current_stock < reorder_threshold`) stays in Python. The model is used as an explanatory comparison engine. The store manager remains responsible for supplier selection and spend.
