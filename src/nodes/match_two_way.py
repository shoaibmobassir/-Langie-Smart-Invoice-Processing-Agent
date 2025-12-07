"""MATCH_TWO_WAY stage node - compute match score between invoice and PO."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, MatchTwoWayOutput, MatchResult
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.mcp_clients.common_client import COMMONClient


def match_two_way_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    MATCH_TWO_WAY node: Compute 2-way match score.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with match_two_way output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    common_client = COMMONClient()
    
    try:
        log_node_entry("MATCH_TWO_WAY", thread_id, state)
        
        workflow_config = state.get("config", {})
        match_threshold = workflow_config.get("match_threshold", 0.90)
        tolerance_pct = workflow_config.get("two_way_tolerance_pct", 5.0)
        
        prepare_output = state.get("prepare", {})
        normalized_invoice = prepare_output.get("normalized_invoice", {})
        invoice_line_items = normalized_invoice.get("line_items", [])
        
        retrieve_output = state.get("retrieve", {})
        matched_pos = retrieve_output.get("matched_pos", [])
        
        # Extract PO line items
        po_line_items = []
        for po in matched_pos:
            po_line_items.extend(po.get("line_items", []))
        
        # Compute match score via COMMON
        match_result_data = common_client.compute_match_score(
            invoice_line_items,
            po_line_items,
            tolerance_pct
        )
        
        match_score = match_result_data.get("match_score", 0.0)
        match_evidence = match_result_data.get("evidence", {})
        
        # Determine match result
        if match_score >= match_threshold:
            match_result = MatchResult.MATCHED.value
        else:
            match_result = MatchResult.FAILED.value
        
        output = MatchTwoWayOutput(
            match_score=match_score,
            match_result=match_result,
            tolerance_pct=tolerance_pct,
            match_evidence=match_evidence
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("MATCH_TWO_WAY", thread_id, ["match_two_way"], duration_ms)
        log_state_update("MATCH_TWO_WAY", {"match_two_way": output})
        
        return {"match_two_way": output}
    except Exception as e:
        log_error("MATCH_TWO_WAY", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "MATCH_TWO_WAY", "message": str(e)},
            "workflow_status": "FAILED"
        }

