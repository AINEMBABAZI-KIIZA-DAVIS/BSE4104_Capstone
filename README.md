# ProcurePrep UG

ProcurePrep UG is a deterministic procurement-preparation tool for a small retail or office operation in Uganda. It checks stock, compares supplier quotations, drafts a requisition, and blocks any automatic spend or payment action until a human approves the route.

The project now runs as a real local application:
- a Python backend exposes live procurement logic over HTTP
- a browser dashboard reads live inventory and evaluation state
- the Week 7 scenario suite runs against the same Python logic used by the app

## What the system does

- Reads inventory and quotation data from the local CSV files
- Evaluates reorder need using deterministic thresholds
- Retrieves valid supplier quotes
- Creates DRAFT requisitions without issuing a purchase order
- Enforces safety guardrails for item IDs, roles, quantity, and tool access
- Requires human confirmation before a requisition is routed for approval

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
./start.sh
```

Then open:
- backend: http://127.0.0.1:8000
- dashboard: http://127.0.0.1:8001/demo_dashboard.html

## Environment configuration

The app reads values from `.env` if present. The defaults are defined in `.env.example`:

```env
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8001
DEBUG=0
GEMINI_API_KEY=
ALLOWED_ORIGINS=http://127.0.0.1:8001,http://localhost:8001
```

## Run manually

If you do not want to use the start script:

```bash
# backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# dashboard
python -m http.server 8001 --directory .
```

Then open the dashboard at `http://127.0.0.1:8001/demo_dashboard.html`.

## Validation and evaluation

Run the automated checks:

```bash
python -m unittest tests.test_api_smoke tests.test_live_evaluation -v
```

Run the live 32-scenario evaluation suite:

```bash
python scripts/run_week7_evaluation.py
```

The project also exposes a live API route for the evaluation data:

```bash
curl http://127.0.0.1:8000/api/evaluation
```

This returns the full live pass/fail result from the deterministic Python layer. The project currently reports `32 / 32` passing for the Week 7 suite.

## Repository layout

```text
app.py             FastAPI backend entry point
config.py          environment/settings loader
start.sh           starts backend + dashboard in one step
demo_dashboard.html browser-driven demo UI
src/               procurement logic, guardrails, agent, tool registry
src/tools.py       deterministic business logic
src/guardrails.py input validation and access controls
data/             inventory, quotations, requisition, memory state
knowledge/        policy and reference data for procurement decisions
results/          evaluation outputs and execution traces
tests/            backend and API validation tests
docs/             architecture and project evidence logs
legacy/           older experimental files kept for reference
```

## Safety model

- No automatic spend or PO issuance occurs
- Human confirmation is required before routing moves to approval
- Unknown tools fail closed
- Invalid item IDs, bad quantities, or unauthorized roles are rejected
- Injection patterns such as override, award, payment, or SQL-style payloads are blocked

## Notes

This project is intentionally deterministic for the procurement decision path. The browser UI and API are connected to the same Python logic so the demo reflects real backend behavior instead of static mock data.
