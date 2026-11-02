#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  cp .env.example .env
  set -a
  source .env
  set +a
fi

BACKEND_HOST="${API_HOST:-0.0.0.0}"
BACKEND_PORT="${API_PORT:-8000}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8001}"

python -m uvicorn app:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" > /tmp/procureprep_backend.log 2>&1 &
BACKEND_PID=$!

python -m http.server "$DASHBOARD_PORT" --directory . > /tmp/procureprep_dashboard.log 2>&1 &
DASHBOARD_PID=$!

cleanup() {
  kill "$BACKEND_PID" "$DASHBOARD_PID" 2>/dev/null || true
}
trap cleanup EXIT

printf '\nProcurePrep UG is running.\n'
printf 'Backend: http://%s:%s\n' "$BACKEND_HOST" "$BACKEND_PORT"
printf 'Dashboard: http://127.0.0.1:%s/demo_dashboard.html\n\n' "$DASHBOARD_PORT"

wait "$BACKEND_PID" "$DASHBOARD_PID"
