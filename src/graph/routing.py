"""Routing logic for LangGraph workflow."""

from typing import Literal
from src.state.models import WorkflowState, MatchResult


def route_after_match(state: WorkflowState) -> Literal["CHECKPOINT_HITL", "RECONCILE"]:
    """
    Route after MATCH_TWO_WAY stage.
    
    If match_result == "FAILED", route to CHECKPOINT_HITL.
    Otherwise, route to RECONCILE.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name
    """
    match_output = state.get("match_two_way", {})
    match_result = match_output.get("match_result", "")
    
    if match_result == MatchResult.FAILED.value:
        return "CHECKPOINT_HITL"
    else:
        return "RECONCILE"


def route_after_hitl(state: WorkflowState) -> Literal["RECONCILE", "COMPLETE", "__end__"]:
    """
    Route after HITL_DECISION stage.
    
    If human decision is ACCEPT, route to RECONCILE.
    If REJECT, route to COMPLETE.
    If no decision yet, route to END (pause).
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name
    """
    hitl_output = state.get("hitl")
    if not hitl_output:
        # No HITL output yet - pause workflow
        return "__end__"
    
    human_decision = hitl_output.get("human_decision", "") if isinstance(hitl_output, dict) else ""
    
    if not human_decision or human_decision not in ["ACCEPT", "REJECT"]:
        # No decision yet - pause workflow
        return "__end__"
    
    if human_decision == "ACCEPT":
        return "RECONCILE"
    else:
        return "COMPLETE"


def should_checkpoint(state: WorkflowState) -> bool:
    """
    Determine if checkpoint should be created.
    
    Args:
        state: Current workflow state
        
    Returns:
        True if checkpoint should be created
    """
    match_output = state.get("match_two_way", {})
    match_result = match_output.get("match_result", "")
    
    return match_result == MatchResult.FAILED.value

