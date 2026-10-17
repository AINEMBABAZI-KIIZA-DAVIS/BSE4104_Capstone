# ProcurePrep MCP-Style Interface Specification (Week 6)

**Implementation:** `src/mcp_interface.py`  
**Mode:** In-process capability adapter (not a networked MCP server)

The assignment allows either an external integration or an MCP-style interface. ProcurePrep documents the four Week 4 tools as callable capabilities with inputs, outputs, permissions and a security boundary so another agent runtime could host them later.

---

## Catalogue

| Capability | Inputs | Side effect | Confirmation | Roles |
| :--- | :--- | :--- | :--- | :--- |
| `get_reorder_status` | `item_id` | None | No | procurement_officer, store_manager |
| `get_supplier_quotations` | `item_id` | None | No | procurement_officer, store_manager |
| `create_requisition_draft` | `item_id`, `quantity`, `selected_quotation_id`, `requested_by` | Local DRAFT write | No | procurement_officer, store_manager |
| `route_requisition_for_approval` | `requisition_id` | Status → PENDING_APPROVAL | **Yes** | procurement_officer |

## Call contract

```
list_mcp_tools() -> list of capability descriptors
call_mcp_tool(name, arguments, role=..., confirmed=False) -> JSON result
```

Failure codes:

- `UNKNOWN_TOOL` — name not in the catalogue
- `UNAUTHORIZED_ROLE` — caller role is not listed
- `CONFIRMATION_REQUIRED` — high-impact tool without `confirmed=True`
- Plus all deterministic tool errors (`MISSING_PARAMETER`, `QUOTATION_EXPIRED`, …)

## Security boundary

- No network bind, no arbitrary shell, no payment API.
- Allow-list only; `award_contract` and similar names are rejected.
- Routing cannot run through this adapter without an explicit confirmation flag.
- Commercial quotation data stays in local CSV; the adapter does not export it to a public host.

## Example

```python
from src.mcp_interface import call_mcp_tool

call_mcp_tool("get_reorder_status", {"item_id": "ITEM-004"}, role="procurement_officer")
```
