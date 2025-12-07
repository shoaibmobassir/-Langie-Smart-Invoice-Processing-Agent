"""CHECKPOINT_HITL stage node - create checkpoint and pause workflow."""

import uuid
import time
import json
from datetime import datetime
from typing import Dict, Any
from src.state.models import WorkflowState, CheckpointHitlOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_checkpoint_created, log_state_update
from src.tools.bigtool_picker import bigtool_picker


def checkpoint_hitl_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    CHECKPOINT_HITL node: Create checkpoint and pause workflow.
    
    This node is only executed if match_result == "FAILED".
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context (includes checkpointer)
        
    Returns:
        State updates with checkpoint output and paused flag
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    
    try:
        log_node_entry("CHECKPOINT_HITL", thread_id, state)
        
        match_output = state.get("match_two_way", {})
        match_result = match_output.get("match_result", "")
        
        # Only create checkpoint if match failed
        if match_result != "FAILED":
            # Skip checkpoint creation
            return {}
        
        invoice_payload = state.get("invoice_payload", {})
        invoice_id = invoice_payload.get("invoice_id", "unknown")
        vendor_name = invoice_payload.get("vendor_name", "unknown")
        amount = invoice_payload.get("amount", 0)
        
        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())
        
        # Select DB tool via Bigtool
        db_tool = bigtool_picker.select(
            capability="db",
            pool_hint=["postgres", "sqlite", "dynamodb"]
        )
        
        # Serialize state for storage
        state_blob = json.dumps({
            "workflow_state": state,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # In production, persist to DB using the selected tool
        # For demo, this will be handled by the checkpoint store
        
        # Generate review URL
        review_url = f"/human-review/{checkpoint_id}"
        
        # Prepare checkpoint data for human review queue
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "invoice_id": invoice_id,
            "vendor_name": vendor_name,
            "amount": amount,
            "created_at": datetime.utcnow().isoformat(),
            "reason_for_hold": "MATCH_FAILED_HITL",
            "review_url": review_url,
            "state_blob": state_blob,
            "thread_id": thread_id
        }
        
        # Store checkpoint in human review repository
        if "human_review_repo" in runtime:
            runtime["human_review_repo"].save_checkpoint(checkpoint_data)
        
        output = CheckpointHitlOutput(
            cp_id=checkpoint_id,
            review_url=review_url,
            paused_reason="MATCH_FAILED_HITL"
        )
        
        log_checkpoint_created(checkpoint_id, invoice_id, "MATCH_FAILED_HITL", thread_id or "unknown")
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("CHECKPOINT_HITL", thread_id, ["checkpoint", "paused", "paused_reason"], duration_ms)
        log_state_update("CHECKPOINT_HITL", {"checkpoint": output})
        
        return {
            "checkpoint": output,
            "paused": True,
            "paused_reason": "MATCH_FAILED_HITL",
            "hitl_checkpoint_id": checkpoint_id,
            "workflow_status": "PAUSED"
        }
    except Exception as e:
        log_error("CHECKPOINT_HITL", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "CHECKPOINT_HITL", "message": str(e)},
            "workflow_status": "FAILED"
        }

