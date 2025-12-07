"""COMPLETE stage node - finalize workflow and produce output."""

import time
from datetime import datetime
from typing import Dict, Any
from src.state.models import WorkflowState, CompleteOutput, WorkflowStatus
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker


def complete_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    COMPLETE node: Produce final payload and audit log.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with complete output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    
    try:
        log_node_entry("COMPLETE", thread_id, state)
        
        # Check if this was a rejection
        hitl_output = state.get("hitl")
        human_decision = hitl_output.get("human_decision", "") if hitl_output and isinstance(hitl_output, dict) else ""
        
        if human_decision == "REJECT":
            status = WorkflowStatus.REQUIRES_MANUAL_HANDLING.value
        else:
            status = WorkflowStatus.COMPLETED.value
        
        # Build final payload
        final_payload = {
            "invoice_id": state.get("invoice_payload", {}).get("invoice_id"),
            "workflow_status": status,
            "processed_at": datetime.utcnow().isoformat(),
            "stages_completed": [
                "INTAKE", "UNDERSTAND", "PREPARE", "RETRIEVE", "MATCH_TWO_WAY"
            ],
            "intake": state.get("intake"),
            "understand": state.get("understand"),
            "prepare": state.get("prepare"),
            "retrieve": state.get("retrieve"),
            "match_two_way": state.get("match_two_way"),
        }
        
        # Add optional stages if present
        if state.get("hitl"):
            final_payload["stages_completed"].append("HITL_DECISION")
            final_payload["hitl"] = state.get("hitl")
        
        if state.get("reconcile"):
            final_payload["stages_completed"].append("RECONCILE")
            final_payload["reconcile"] = state.get("reconcile")
        
        if state.get("approve"):
            final_payload["stages_completed"].append("APPROVE")
            final_payload["approve"] = state.get("approve")
        
        if state.get("posting"):
            final_payload["stages_completed"].append("POSTING")
            final_payload["posting"] = state.get("posting")
        
        if state.get("notify"):
            final_payload["stages_completed"].append("NOTIFY")
            final_payload["notify"] = state.get("notify")
        
        # Build audit log
        audit_log = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": "COMPLETE",
                "action": "workflow_finalized",
                "status": status,
                "thread_id": thread_id
            }
        ]
        
        # Select DB tool via Bigtool for audit persistence
        db_tool = bigtool_picker.select(
            capability="db",
            pool_hint=["postgres", "sqlite", "dynamodb"]
        )
        
        # In production, persist audit log to DB
        # For demo, just log it
        
        output = CompleteOutput(
            final_payload=final_payload,
            audit_log=audit_log,
            status=status
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("COMPLETE", thread_id, ["complete"], duration_ms)
        log_state_update("COMPLETE", {"complete": output})
        
        return {
            "complete": output,
            "workflow_status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        log_error("COMPLETE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "COMPLETE", "message": str(e)},
            "workflow_status": "FAILED"
        }

