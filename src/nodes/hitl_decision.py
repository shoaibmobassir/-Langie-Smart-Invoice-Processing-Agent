"""HITL_DECISION stage node - process human decision."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, HitlDecisionOutput, HumanDecision
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_human_decision, log_state_update


def hitl_decision_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    HITL_DECISION node: Process human decision (ACCEPT/REJECT).
    
    This is a non-deterministic node triggered by human API call.
    
    Args:
        state: Current workflow state (loaded from checkpoint)
        config: Node configuration
        runtime: Runtime context (includes human decision data)
        
    Returns:
        State updates with hitl decision output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    
    try:
        log_node_entry("HITL_DECISION", thread_id, state)
        
        # Get human decision from runtime context or state
        # This is set by the API when resuming workflow
        human_decision_data = runtime.get("human_decision", {})
        
        # Check if decision already exists in state (from previous execution)
        existing_hitl = state.get("hitl", {})
        if existing_hitl and existing_hitl.get("human_decision"):
            decision = existing_hitl.get("human_decision")
            reviewer_id = existing_hitl.get("reviewer_id", "unknown")
        else:
            decision = human_decision_data.get("decision", "").upper()
            reviewer_id = human_decision_data.get("reviewer_id", "unknown")
        
        notes = human_decision_data.get("notes", "")
        checkpoint_id = state.get("hitl_checkpoint_id", "") or state.get("checkpoint", {}).get("cp_id", "") or state.get("checkpoint", {}).get("checkpoint_id", "")
        
        # If no decision yet, return empty (workflow will pause/wait)
        if not decision or decision not in [HumanDecision.ACCEPT.value, HumanDecision.REJECT.value]:
            # No decision yet - return empty state update to pause
            return {
                "paused": True,
                "workflow_status": "PAUSED"
            }
        
        log_human_decision(checkpoint_id, decision, reviewer_id)
        
        if decision == HumanDecision.ACCEPT.value:
            # Accept: continue to RECONCILE
            next_stage = "RECONCILE"
            resume_token = f"{thread_id}:{checkpoint_id}"
            
            output = HitlDecisionOutput(
                human_decision=decision,
                reviewer_id=reviewer_id,
                resume_token=resume_token,
                next_stage=next_stage
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_node_exit("HITL_DECISION", thread_id, ["hitl"], duration_ms)
            log_state_update("HITL_DECISION", {"hitl": output})
            
            return {
                "hitl": output,
                "paused": False,
                "workflow_status": "IN_PROGRESS"
            }
        else:
            # Reject: finalize with MANUAL_HANDOFF
            next_stage = "COMPLETE"
            resume_token = f"{thread_id}:{checkpoint_id}"
            
            output = HitlDecisionOutput(
                human_decision=decision,
                reviewer_id=reviewer_id,
                resume_token=resume_token,
                next_stage=next_stage
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_node_exit("HITL_DECISION", thread_id, ["hitl"], duration_ms)
            log_state_update("HITL_DECISION", {"hitl": output})
            
            return {
                "hitl": output,
                "paused": False,
                "workflow_status": "IN_PROGRESS"
            }
    except Exception as e:
        log_error("HITL_DECISION", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "HITL_DECISION", "message": str(e)},
            "workflow_status": "FAILED"
        }

