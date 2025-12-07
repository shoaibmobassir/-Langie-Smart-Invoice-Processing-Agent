"""POSTING stage node - post to ERP and schedule payment."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, PostingOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker
from src.mcp_clients.atlas_client import ATLASClient


def posting_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    POSTING node: Post journal entries to ERP and schedule payment.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with posting output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    atlas_client = ATLASClient()
    
    try:
        log_node_entry("POSTING", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        reconcile_output = state.get("reconcile", {})
        accounting_entries = reconcile_output.get("accounting_entries", [])
        
        # Select ERP connector via Bigtool
        erp_tool = bigtool_picker.select(
            capability="erp_connector",
            pool_hint=["sap_sandbox", "netsuite", "mock_erp"]
        )
        
        # Post to ERP via ATLAS
        erp_result = atlas_client.post_to_erp(
            accounting_entries,
            invoice_payload,
            erp_connector=erp_tool.name
        )
        
        erp_txn_id = erp_result.get("erp_txn_id")
        
        # Schedule payment via ATLAS
        due_date = invoice_payload.get("due_date", "")
        amount = invoice_payload.get("amount", 0)
        
        payment_result = atlas_client.schedule_payment(
            invoice_payload,
            amount,
            due_date
        )
        
        scheduled_payment_id = payment_result.get("scheduled_payment_id")
        
        output = PostingOutput(
            posted=True,
            erp_txn_id=erp_txn_id,
            scheduled_payment_id=scheduled_payment_id
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("POSTING", thread_id, ["posting"], duration_ms)
        log_state_update("POSTING", {"posting": output})
        
        return {"posting": output}
    except Exception as e:
        log_error("POSTING", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "POSTING", "message": str(e)},
            "workflow_status": "FAILED"
        }

