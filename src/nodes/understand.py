"""UNDERSTAND stage node - OCR extraction and NLP parsing."""

import time
import re
from typing import Dict, Any
from src.state.models import WorkflowState, UnderstandOutput, ParsedInvoice
from src.logging.logger import log_node_entry, log_node_exit, log_error, log_state_update
from src.tools.bigtool_picker import bigtool_picker
from src.mcp_clients.atlas_client import ATLASClient


def understand_node(state: WorkflowState, config: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    """
    UNDERSTAND node: Run OCR and parse line items.
    
    Args:
        state: Current workflow state
        config: Node configuration
        runtime: Runtime context
        
    Returns:
        State updates with understand output
    """
    start_time = time.time()
    thread_id = state.get("thread_id")
    atlas_client = ATLASClient()
    
    try:
        log_node_entry("UNDERSTAND", thread_id, state)
        
        invoice_payload = state.get("invoice_payload", {})
        attachments = invoice_payload.get("attachments", [])
        
        # Filter out empty strings and ensure we have valid file paths
        valid_attachments = [att for att in attachments if att and isinstance(att, str)]
        
        # If no attachments provided, use invoice data directly
        if not valid_attachments:
            log_node_entry("UNDERSTAND", thread_id, state)
            # Fallback: use invoice data directly
            parsed_invoice = ParsedInvoice(
                invoice_text="No attachments provided - using invoice data directly",
                parsed_line_items=invoice_payload.get("line_items", []),
                detected_pos=[],
                currency=invoice_payload.get("currency", "USD"),
                parsed_dates={
                    "invoice_date": invoice_payload.get("invoice_date", ""),
                    "due_date": invoice_payload.get("due_date", "")
                }
            )
            output = UnderstandOutput(parsed_invoice=parsed_invoice)
            duration_ms = (time.time() - start_time) * 1000
            log_node_exit("UNDERSTAND", thread_id, ["understand"], duration_ms)
            return {"understand": output}
        
        # Select OCR tool via Bigtool
        ocr_tool = bigtool_picker.select(
            capability="ocr",
            pool_hint=["google_vision", "tesseract", "aws_textract"]
        )
        
        # Run OCR on actual files via ATLAS
        ocr_result = atlas_client.ocr_extract(valid_attachments, provider=ocr_tool.name)
        invoice_text = ocr_result.get("text", "")
        
        # Parse line items from text (simple regex-based parsing for demo)
        # In production, use proper NLP/NER
        parsed_line_items = []
        po_references = []
        
        # Extract line items from OCR text
        line_item_pattern = r"Line Item \d+: (.+?) - Qty: (\d+), Price: \$?([\d.]+), Total: \$?([\d.]+)"
        matches = re.findall(line_item_pattern, invoice_text)
        for match in matches:
            parsed_line_items.append({
                "desc": match[0],
                "qty": float(match[1]),
                "unit_price": float(match[2]),
                "total": float(match[3])
            })
        
        # Extract PO references
        po_pattern = r"PO[-\s]?(\w+[-]?\d+)"
        po_matches = re.findall(po_pattern, invoice_text, re.IGNORECASE)
        po_references = [f"PO-{match}" if not match.startswith("PO") else match for match in po_matches]
        
        # Extract dates
        date_pattern = r"(\d{4}-\d{2}-\d{2})"
        dates = re.findall(date_pattern, invoice_text)
        parsed_dates = {}
        if dates:
            parsed_dates["invoice_date"] = dates[0] if len(dates) > 0 else invoice_payload.get("invoice_date", "")
            parsed_dates["due_date"] = dates[1] if len(dates) > 1 else invoice_payload.get("due_date", "")
        
        # Use invoice payload as fallback
        if not parsed_line_items:
            parsed_line_items = invoice_payload.get("line_items", [])
        
        parsed_invoice = ParsedInvoice(
            invoice_text=invoice_text,
            parsed_line_items=parsed_line_items,
            detected_pos=po_references,
            currency=invoice_payload.get("currency", "USD"),
            parsed_dates=parsed_dates
        )
        
        output = UnderstandOutput(parsed_invoice=parsed_invoice)
        
        duration_ms = (time.time() - start_time) * 1000
        log_node_exit("UNDERSTAND", thread_id, ["understand"], duration_ms)
        log_state_update("UNDERSTAND", {"understand": output})
        
        return {"understand": output}
    except Exception as e:
        log_error("UNDERSTAND", e, {"thread_id": thread_id})
        return {
            "error": {"stage": "UNDERSTAND", "message": str(e)},
            "workflow_status": "FAILED"
        }

