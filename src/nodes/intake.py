"""INTAKE stage node - validate and persist invoice payload."""

import uuid
import time
from datetime import datetime
from typing import Dict, Any
from src.state.models import WorkflowState, IntakeOutput
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker


def intake_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    INTAKE node: Validate payload schema and persist raw invoice.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with intake output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    
    try:
        log_node_entry("INTAKE", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        
        # Validate schema
        required_fields = ["invoice_id", "vendor_name", "amount", "line_items"]
        validated = True
        for field in required_fields:
            if field not in invoice_payload:
                validated = False
                break
        
        # Select storage tool via Bigtool
        storage_tool = bigtool_picker.select(
            capability="storage",
            pool_hint=["local_fs", "s3", "gcs"]
        )
        storage_tool.executor()  # Mock storage initialization
        
        # Generate raw ID and timestamp
        raw_id = str(uuid.uuid4())
        ingest_ts = datetime.utcnow().isoformat()
        
        output = IntakeOutput(
            raw_id=raw_id,
            ingest_ts=ingest_ts,
            validated=validated
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("INTAKE", thread_id, ["intake"], duration_ms)
        log_state_update("INTAKE", {"intake": output})
        
        return {
            "intake": output,
            "workflow_status": "IN_PROGRESS"
        }
    except Exception as e:
        log_error("INTAKE", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "INTAKE", "message": str(e)},
            "workflow_status": "FAILED"
        }

