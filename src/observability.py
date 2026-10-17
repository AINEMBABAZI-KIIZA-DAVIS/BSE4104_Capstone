"""JSONL observability for model/tool/agent events (Week 7)."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRACE_PATH = PROJECT_ROOT / "results" / "traces" / "agent_events.jsonl"


class AgentTracer:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_TRACE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: dict[str, Any]) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")

    def span(self, **fields: Any):
        return _Span(self, fields)


class _Span:
    def __init__(self, tracer: AgentTracer, fields: dict[str, Any]):
        self.tracer = tracer
        self.fields = fields
        self.start = 0.0

    def __enter__(self) -> _Span:
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        latency_ms = round((time.perf_counter() - self.start) * 1000, 2)
        event = {**self.fields, "latency_ms": latency_ms}
        if exc is not None:
            event["error"] = f"{exc_type.__name__}: {exc}"
        self.tracer.emit(event)


_default_tracer: AgentTracer | None = None


def get_tracer() -> AgentTracer:
    global _default_tracer
    if _default_tracer is None:
        _default_tracer = AgentTracer()
    return _default_tracer
