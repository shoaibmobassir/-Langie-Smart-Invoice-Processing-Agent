"""NOTIFY stage node - send notifications."""

import time
from typing import Dict, Any
from src.state.models import WorkflowState, NotifyOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker
from src.mcp_clients.atlas_client import ATLASClient


def notify_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTIFY node: Send notifications to vendor and finance team.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with notify output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    atlas_client = ATLASClient()
    
    try:
        log_node_entry("NOTIFY", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        prepare_output = state.get("prepare", {})
        vendor_profile = prepare_output.get("vendor_profile", {})
        
        # Select email provider via Bigtool
        email_tool = bigtool_picker.select(
            capability="email",
            pool_hint=["sendgrid", "smartlead", "ses"]
        )
        
        # Mock vendor email (in production, get from vendor profile)
        vendor_email = f"vendor@{invoice_payload.get('vendor_name', '').lower().replace(' ', '')}.com"
        
        # Notify vendor via ATLAS
        vendor_notification = atlas_client.notify_vendor(
            vendor_email,
            invoice_payload,
            email_provider=email_tool.name
        )
        
        # Notify finance team via ATLAS
        finance_message = f"Invoice {invoice_payload.get('invoice_id')} processed and posted."
        finance_notification = atlas_client.notify_finance_team(finance_message)
        
        notify_status = {
            "vendor": vendor_notification,
            "finance_team": finance_notification
        }
        
        notified_parties = ["vendor", "finance_team"]
        
        output = NotifyOutput(
            notify_status=notify_status,
            notified_parties=notified_parties
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("NOTIFY", thread_id, ["notify"], duration_ms)
        log_state_update("NOTIFY", {"notify": output})
        
        return {"notify": output}
    except Exception as e:
        log_error("NOTIFY", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "NOTIFY", "message": str(e)},
            "workflow_status": "FAILED"
        }

