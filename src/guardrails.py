"""
Week 7 guardrails: input validation, tool allow-list, role checks,
approval flags and prompt-injection awareness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

ITEM_ID_RE = re.compile(r"^ITEM-\d{3}$")
APPROVED_TOOLS = frozenset({
    "get_reorder_status",
    "get_supplier_quotations",
    "create_requisition_draft",
    "route_requisition_for_approval",
})
ALLOWED_ROLES = frozenset({"procurement_officer", "store_manager"})
HIGH_IMPACT_TOOLS = frozenset({"route_requisition_for_approval"})

_INJECTION = re.compile(
    r"(ignore\s+(all\s+)?(previous|prior)\s+instructions"
    r"|disregard\s+(your\s+)?(rules|guardrails|constraints)"
    r"|you\s+are\s+now\s+"
    r"|system\s+prompt"
    r"|award\s+(the\s+)?(contract|supplier|tender)"
    r"|approve\s+(the\s+)?(purchase|payment|wire)"
    r"|drop\s+table"
    r"|<\|.*\|>)",
    re.IGNORECASE,
)


@dataclass
class GuardDecision:
    allowed: bool
    reason: str | None = None
    message: str | None = None


def validate_item_id(item_id: str | None) -> GuardDecision:
    if item_id is None or str(item_id).strip() == "":
        return GuardDecision(False, "MISSING_ITEM_ID", "item_id is required.")
    if not ITEM_ID_RE.match(str(item_id).strip()):
        return GuardDecision(False, "INPUT_REJECTED", "item_id must match ITEM-NNN.")
    return GuardDecision(True)


def validate_quantity(quantity: int | None, *, required: bool = False) -> GuardDecision:
    if quantity is None:
        if required:
            return GuardDecision(False, "INPUT_REJECTED", "quantity is required.")
        return GuardDecision(True)
    try:
        value = int(quantity)
    except (TypeError, ValueError):
        return GuardDecision(False, "INPUT_REJECTED", "quantity must be an integer.")
    if value <= 0:
        return GuardDecision(False, "INPUT_REJECTED", "quantity must be greater than zero.")
    return GuardDecision(True)


def detect_injection(*texts: str | None) -> GuardDecision:
    for text in texts:
        if text and _INJECTION.search(str(text)):
            return GuardDecision(
                False,
                "INJECTION_BLOCKED",
                "Input looks like an instruction-override or unauthorized award/payment request.",
            )
    return GuardDecision(True)


def assert_tool_allowed(name: str, allow_list: Iterable[str] = APPROVED_TOOLS) -> GuardDecision:
    if name not in set(allow_list):
        return GuardDecision(False, "UNKNOWN_TOOL", f"Tool '{name}' is not on the allow-list.")
    return GuardDecision(True)


def authorize_role(role: str, allowed: Iterable[str] = ALLOWED_ROLES) -> GuardDecision:
    if role not in set(allowed):
        return GuardDecision(False, "UNAUTHORIZED_ROLE", f"Role '{role}' is not permitted.")
    return GuardDecision(True)


def require_confirmation(tool: str, confirmed: bool) -> GuardDecision:
    if tool in HIGH_IMPACT_TOOLS and not confirmed:
        return GuardDecision(
            False,
            "CONFIRMATION_REQUIRED",
            "Human confirmation is required before this tool may run.",
        )
    return GuardDecision(True)


def screen_session_inputs(
    *,
    item_id: str | None,
    requested_by: str | None = None,
    quantity: int | None = None,
    user_text: str | None = None,
    role: str = "procurement_officer",
) -> GuardDecision:
    role_check = authorize_role(role)
    if not role_check.allowed:
        return role_check
    injection = detect_injection(item_id, requested_by, user_text)
    if not injection.allowed:
        return injection
    item_check = validate_item_id(item_id)
    if not item_check.allowed:
        return item_check
    return validate_quantity(quantity, required=False)
