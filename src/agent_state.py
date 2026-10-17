"""Explicit workflow/session state for the ProcurePrep bounded agent (Weeks 5–6)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

PHASES = ("SENSE", "PLAN", "ACT", "OBSERVE", "STOP")
GOAL_PREPARE_REQUISITION = "PREPARE_REQUISITION"

STOP_REASONS = (
    "GOAL_COMPLETE",
    "NO_REORDER_NEEDED",
    "NO_QUOTATIONS",
    "NO_VALID_QUOTATION",
    "ITEM_NOT_FOUND",
    "MISSING_ITEM_ID",
    "HUMAN_DECLINED",
    "HUMAN_HANDOFF",
    "MAX_ITERATIONS",
    "RECOVERY_EXHAUSTED",
    "UNKNOWN_TOOL",
    "TOOL_ERROR",
    "INPUT_REJECTED",
    "INJECTION_BLOCKED",
    "UNAUTHORIZED_ROLE",
)


@dataclass
class WorkflowState:
    """Session state for one bounded requisition-preparation run."""

    session_id: str
    goal: str = GOAL_PREPARE_REQUISITION
    phase: str = "SENSE"
    item_id: str | None = None
    requested_by: str | None = None
    quantity: int | None = None
    wants_routing: bool = False
    iteration: int = 0
    max_iterations: int = 8
    max_recoveries: int = 2
    recovery_attempts: int = 0
    reorder: dict[str, Any] | None = None
    quotations: list[dict[str, Any]] | None = None
    excluded_quotation_ids: list[str] = field(default_factory=list)
    selected_quotation_id: str | None = None
    requisition_id: str | None = None
    requisition_status: str | None = None
    last_tool: str | None = None
    last_result: dict[str, Any] | None = None
    last_error: str | None = None
    stop_reason: str | None = None
    outcome: str | None = None
    memory_hints_used: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_session(
    *,
    item_id: str | None = None,
    requested_by: str | None = None,
    quantity: int | None = None,
    wants_routing: bool = False,
    max_iterations: int = 8,
) -> WorkflowState:
    return WorkflowState(
        session_id=f"SES-{uuid4().hex[:10]}",
        item_id=item_id,
        requested_by=requested_by,
        quantity=quantity,
        wants_routing=wants_routing,
        max_iterations=max_iterations,
    )
