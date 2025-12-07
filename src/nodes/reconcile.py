"""RECONCILE stage node - build accounting entries."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, ReconciliationOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.mcp_clients.common_client import COMMONClient


def reconcile_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    RECONCILE node: Build accounting entries and reconciliation report.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with reconcile output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    common_client = COMMONClient()
    
    try:
        log_node_entry("RECONCILE", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        retrieve_output = state.get("retrieve", {})
        matched_pos = retrieve_output.get("matched_pos", [])
        
        # Get first PO as reference (in production, use best match)
        po_data = matched_pos[0] if matched_pos else None
        
        # Build accounting entries via COMMON
        accounting_entries = common_client.build_accounting_entries(invoice_payload, po_data)
        
        # Build reconciliation report
        reconciliation_report = {
            "invoice_id": invoice_payload.get("invoice_id"),
            "invoice_amount": invoice_payload.get("amount"),
            "matched_pos": [po.get("po_id") for po in matched_pos],
            "accounting_entries_count": len(accounting_entries),
            "reconciled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        output = ReconciliationOutput(
            accounting_entries=accounting_entries,
            reconciliation_report=reconciliation_report
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("RECONCILE", thread_id, ["reconcile"], duration_ms)
        log_state_update("RECONCILE", {"reconcile": output})
        
        return {"reconcile": output}
    except Exception as e:
        log_error("RECONCILE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "RECONCILE", "message": str(e)},
            "workflow_status": "FAILED"
        }

