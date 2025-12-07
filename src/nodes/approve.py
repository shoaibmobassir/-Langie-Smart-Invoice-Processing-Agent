"""APPROVE stage node - apply approval policies."""

import time
from typing import Dict, Any, Optional
from src.state.models import WorkflowState, ApproveOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update


def approve_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    APPROVE node: Apply approval policies (auto-approve or escalate).
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with approve output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    
    try:
        log_node_entry("APPROVE", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        amount = invoice_payload.get("amount", 0)
        
        # Approval policy: auto-approve if amount < 10000, else escalate
        approval_threshold = 10000.0
        
        if amount < approval_threshold:
            approval_status = "AUTO_APPROVED"
            approver_id = None
        else:
            approval_status = "REQUIRES_APPROVAL"
            approver_id = "approver_001"  # In production, assign to approver
        
        output = ApproveOutput(
            approval_status=approval_status,
            approver_id=approver_id
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("APPROVE", thread_id, ["approve"], duration_ms)
        log_state_update("APPROVE", {"approve": output})
        
        return {"approve": output}
    except Exception as e:
        log_error("APPROVE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "APPROVE", "message": str(e)},
            "workflow_status": "FAILED"
        }

