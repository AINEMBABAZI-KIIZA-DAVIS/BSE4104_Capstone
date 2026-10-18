"""
MCP-style tool interface for ProcurePrep (Week 6 interoperability).

Exposes the Week 4 tools as a capability catalogue: name, inputs, outputs,
permissions and security boundary. This is an in-process adapter, not a
network MCP server.
"""

from __future__ import annotations

from typing import Any

from src.guardrails import assert_tool_allowed, authorize_role, require_confirmation
from src.tools import TOOL_REGISTRY, dispatch_tool

ALLOWED_ROLES = frozenset({"procurement_officer", "store_manager"})

MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_reorder_status",
        "description": "Deterministic reorder decision for one inventory item.",
        "inputSchema": {
            "type": "object",
            "required": ["item_id"],
            "properties": {"item_id": {"type": "string"}},
        },
        "permissions": {"roles": ["procurement_officer", "store_manager"], "confirmation": False},
        "side_effect": "none",
        "security_boundary": "Read-only CSV. No spend. No write.",
    },
    {
        "name": "get_supplier_quotations",
        "description": "Current supplier quotations for one inventory item.",
        "inputSchema": {
            "type": "object",
            "required": ["item_id"],
            "properties": {"item_id": {"type": "string"}},
        },
        "permissions": {"roles": ["procurement_officer", "store_manager"], "confirmation": False},
        "side_effect": "none",
        "security_boundary": "Read-only CSV. Prices are commercial data; not logged to public traces in production.",
    },
    {
        "name": "create_requisition_draft",
        "description": "Create a DRAFT requisition. Does not approve or spend.",
        "inputSchema": {
            "type": "object",
            "required": ["item_id", "quantity", "selected_quotation_id", "requested_by"],
            "properties": {
                "item_id": {"type": "string"},
                "quantity": {"type": "integer", "minimum": 1},
                "selected_quotation_id": {"type": "string"},
                "requested_by": {"type": "string"},
            },
        },
        "permissions": {"roles": ["procurement_officer", "store_manager"], "confirmation": False},
        "side_effect": "local_draft_write",
        "security_boundary": "Local JSON only. Cannot create PENDING_APPROVAL or a purchase order.",
    },
    {
        "name": "route_requisition_for_approval",
        "description": "Route a DRAFT to a human approver (high impact).",
        "inputSchema": {
            "type": "object",
            "required": ["requisition_id"],
            "properties": {"requisition_id": {"type": "string"}},
        },
        "permissions": {"roles": ["procurement_officer"], "confirmation": True},
        "side_effect": "workflow_state_change",
        "security_boundary": "Requires explicit human confirmation. No payment or award.",
    },
]


def list_mcp_tools() -> list[dict[str, Any]]:
    return [dict(t) for t in MCP_TOOLS]


def call_mcp_tool(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    role: str = "procurement_officer",
    confirmed: bool = False,
) -> dict[str, Any]:
    spec = next((t for t in MCP_TOOLS if t["name"] == name), None)
    allow = assert_tool_allowed(name)
    if spec is None or name not in TOOL_REGISTRY or not allow.allowed:
        return {"error": "UNKNOWN_TOOL", "tool": name}

    if role not in spec["permissions"]["roles"]:
        return {
            "error": "UNAUTHORIZED_ROLE",
            "tool": name,
            "role": role,
            "message": "Role is not permitted to call this capability.",
        }
    role_check = authorize_role(role)
    if not role_check.allowed:
        return {"error": role_check.reason, "tool": name, "role": role, "message": role_check.message}

    confirm = require_confirmation(name, confirmed)
    if spec["permissions"]["confirmation"] or not confirm.allowed:
        if not confirmed:
            return {
                "error": "CONFIRMATION_REQUIRED",
                "tool": name,
                "message": "Human confirmation is required before this capability may run.",
            }

    return dispatch_tool(name, arguments or {})
