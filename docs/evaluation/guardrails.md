# ProcurePrep Guardrail Implementation Evidence (Week 7)

**Code:** `src/guardrails.py`, wired through `src/bounded_agent.py` and `src/mcp_interface.py`

| Control | Implementation | Evidence |
| :--- | :--- | :--- |
| Input validation | `ITEM-NNN` format; quantity > 0 | EV-16, EV-17, EV-26 |
| Tool allow-list | Four named tools only | EV-23 `UNKNOWN_TOOL` |
| Authorization | Officer / store manager roles | EV-29, EV-31, EV-32 |
| Agent iteration limits | Max 8 iterations, 2 recoveries | `WorkflowState.max_iterations` |
| Approval control | Routing requires confirmation | EV-24, EV-25 |
| Prompt-injection awareness | Regex on user text, requester, item_id | EV-20, EV-21, EV-22 |
| Output / side-effect bound | Draft cannot become a PO or payment | EV-25 leaves `DRAFT` |

Observability: each ACT is timed and appended to `results/traces/week7_eval.jsonl` (`src/observability.py`). Fields include `session_id`, `phase`, `tool`, `latency_ms`, `stop_reason`, `outcome`.
