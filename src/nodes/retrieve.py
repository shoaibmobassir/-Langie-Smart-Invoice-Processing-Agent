"""RETRIEVE stage node - fetch POs, GRNs, and history from ERP."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, RetrieveOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker
from src.mcp_clients.atlas_client import ATLASClient


def retrieve_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    RETRIEVE node: Fetch POs, GRNs, and historical invoices.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with retrieve output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    atlas_client = ATLASClient()
    
    try:
        log_node_entry("RETRIEVE", thread_id, state)
        
        understand_output = state.get("understand", {})
        parsed_invoice = understand_output.get("parsed_invoice", {})
        prepare_output = state.get("prepare", {})
        vendor_profile = prepare_output.get("vendor_profile", {})
        
        po_references = parsed_invoice.get("detected_pos", [])
        normalized_vendor_name = vendor_profile.get("normalized_name", "")
        
        # Select ERP connector via Bigtool
        erp_tool = bigtool_picker.select(
            capability="erp_connector",
            pool_hint=["sap_sandbox", "netsuite", "mock_erp"]
        )
        
        # Fetch POs via ATLAS
        matched_pos = atlas_client.fetch_po(po_references, erp_connector=erp_tool.name)
        
        # Extract PO IDs for GRN lookup
        po_ids = [po.get("po_id") for po in matched_pos if po.get("po_id")]
        
        # Fetch GRNs via ATLAS
        matched_grns = atlas_client.fetch_grn(po_ids, erp_connector=erp_tool.name)
        
        # Fetch history via ATLAS
        history = atlas_client.fetch_history(normalized_vendor_name, erp_connector=erp_tool.name)
        
        output = RetrieveOutput(
            matched_pos=matched_pos,
            matched_grns=matched_grns,
            history=history
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("RETRIEVE", thread_id, ["retrieve"], duration_ms)
        log_state_update("RETRIEVE", {"retrieve": output})
        
        return {"retrieve": output}
    except Exception as e:
        log_error("RETRIEVE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "RETRIEVE", "message": str(e)},
            "workflow_status": "FAILED"
        }

