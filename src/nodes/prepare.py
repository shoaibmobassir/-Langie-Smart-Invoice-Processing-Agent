"""PREPARE stage node - normalize vendor and enrich data."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, PrepareOutput, VendorProfile, Flags
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker
from src.mcp_clients.common_client import COMMONClient
from src.mcp_clients.atlas_client import ATLASClient


def prepare_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    PREPARE node: Normalize vendor, enrich profile, compute flags.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with prepare output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    common_client = COMMONClient()
    atlas_client = ATLASClient()
    
    try:
        log_node_entry("PREPARE", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        understand_output = state.get("understand", {})
        parsed_invoice = understand_output.get("parsed_invoice", {})
        
        vendor_name = invoice_payload.get("vendor_name", "")
        vendor_tax_id = invoice_payload.get("vendor_tax_id", "")
        
        # Normalize vendor via COMMON
        normalized_name = common_client.normalize_vendor(vendor_name, vendor_tax_id)
        
        # Select enrichment tool via Bigtool
        enrichment_tool = bigtool_picker.select(
            capability="enrichment",
            pool_hint=["clearbit", "people_data_labs", "vendor_db"]
        )
        
        # Enrich vendor via ATLAS
        enriched_data = atlas_client.enrich_vendor(
            normalized_name,
            vendor_tax_id,
            provider=enrichment_tool.name
        )
        
        vendor_profile = VendorProfile(
            normalized_name=enriched_data.get("normalized_name", normalized_name),
            tax_id=enriched_data.get("tax_id", vendor_tax_id),
            enrichment_meta=enriched_data.get("enrichment_meta", {}),
            credit_score=enriched_data.get("enrichment_meta", {}).get("credit_score"),
            risk_score=enriched_data.get("enrichment_meta", {}).get("risk_score")
        )
        
        # Compute flags via COMMON
        flags = common_client.compute_flags(vendor_profile, invoice_payload)
        
        # Normalize invoice
        normalized_invoice = {
            "amount": invoice_payload.get("amount", 0),
            "currency": invoice_payload.get("currency", "USD"),
            "line_items": parsed_invoice.get("parsed_line_items", invoice_payload.get("line_items", []))
        }
        
        output = PrepareOutput(
            vendor_profile=vendor_profile,
            normalized_invoice=normalized_invoice,
            flags=flags
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("PREPARE", thread_id, ["prepare"], duration_ms)
        log_state_update("PREPARE", {"prepare": output})
        
        return {"prepare": output}
    except Exception as e:
        log_error("PREPARE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "PREPARE", "message": str(e)},
            "workflow_status": "FAILED"
        }

