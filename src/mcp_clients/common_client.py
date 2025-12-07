"""COMMON MCP client - abilities requiring no external data."""

from typing import Dict, Any, List, Optional
import time
from src.logging.logger import log_mcp_call
from src.state.models import VendorProfile, InvoicePayload, Flags


class COMMONClient:
    """
    COMMON MCP client wrapper.
    
    Handles abilities that don't require external/ERP systems:
    - normalize_vendor
    - compute_flags
    - MatchEngine
    - General utilities
    """
    
    def __init__(self):
        """Initialize COMMON client."""
        # In production, this would connect to actual MCP server
        # For demo, we use mocked implementations
        pass
    
    def normalize_vendor(self, vendor_name: str, tax_id: Optional[str] = None) -> str:
        """
        Normalize vendor name (remove extra spaces, standardize format).
        
        Args:
            vendor_name: Raw vendor name
            tax_id: Optional tax ID for disambiguation
            
        Returns:
            Normalized vendor name
        """
        start_time = time.time()
        try:
            # Simple normalization: strip, title case, remove extra spaces
            normalized = " ".join(vendor_name.strip().title().split())
            
            # In production, this might use fuzzy matching against vendor DB
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "normalize_vendor", True, duration_ms)
            
            return normalized
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "normalize_vendor", False, duration_ms, str(e))
            raise
    
    def compute_flags(self, vendor_profile: VendorProfile, invoice: InvoicePayload) -> Flags:
        """
        Compute validation flags (risk, missing info).
        
        Args:
            vendor_profile: Vendor profile data
            invoice: Invoice payload
            
        Returns:
            Flags dict with missing_info and risk_score
        """
        start_time = time.time()
        try:
            missing_info = []
            risk_score = 0.0
            
            # Check for missing information
            if not invoice.get("vendor_tax_id"):
                missing_info.append("vendor_tax_id")
            if not invoice.get("line_items") or len(invoice.get("line_items", [])) == 0:
                missing_info.append("line_items")
            if not invoice.get("invoice_date"):
                missing_info.append("invoice_date")
            
            # Compute risk score (0-1, higher = riskier)
            # Factors: missing info, amount, vendor risk
            base_risk = len(missing_info) * 0.1
            
            amount = invoice.get("amount", 0)
            if amount > 100000:
                base_risk += 0.2
            elif amount > 50000:
                base_risk += 0.1
            
            vendor_risk = vendor_profile.get("risk_score", 0.5)
            risk_score = min(1.0, base_risk + (vendor_risk * 0.5))
            
            flags = Flags(
                missing_info=missing_info,
                risk_score=risk_score
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "compute_flags", True, duration_ms)
            
            return flags
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "compute_flags", False, duration_ms, str(e))
            raise
    
    def compute_match_score(
        self,
        invoice_line_items: List[Dict[str, Any]],
        po_line_items: List[Dict[str, Any]],
        tolerance_pct: float = 5.0
    ) -> Dict[str, Any]:
        """
        Compute 2-way match score between invoice and PO.
        
        Args:
            invoice_line_items: Invoice line items
            po_line_items: PO line items
            tolerance_pct: Tolerance percentage for amount matching
            
        Returns:
            Dict with match_score (0-1), evidence, and details
        """
        start_time = time.time()
        try:
            if not po_line_items:
                # No PO to match against
                result = {
                    "match_score": 0.0,
                    "evidence": {
                        "po_ids": [],
                        "line_item_matches": [],
                        "amount_diff": 0.0,
                        "tolerance_exceeded": True,
                        "reason": "No matching PO found"
                    }
                }
                duration_ms = (time.time() - start_time) * 1000
                log_mcp_call("COMMON", "compute_match_score", True, duration_ms)
                return result
            
            # Simple matching algorithm:
            # 1. Match line items by description (fuzzy)
            # 2. Compare quantities and amounts
            # 3. Compute overall score
            
            invoice_total = sum(item.get("total", 0) for item in invoice_line_items)
            po_total = sum(item.get("total", 0) for item in po_line_items)
            
            amount_diff = abs(invoice_total - po_total)
            amount_diff_pct = (amount_diff / po_total * 100) if po_total > 0 else 100.0
            
            tolerance_exceeded = amount_diff_pct > tolerance_pct
            
            # Line item matching (simplified)
            line_item_matches = []
            matched_count = 0
            
            for inv_item in invoice_line_items:
                for po_item in po_line_items:
                    # Simple description match (in production, use fuzzy matching)
                    if inv_item.get("desc", "").lower() in po_item.get("desc", "").lower():
                        matched_count += 1
                        line_item_matches.append({
                            "invoice_desc": inv_item.get("desc"),
                            "po_desc": po_item.get("desc"),
                            "invoice_total": inv_item.get("total"),
                            "po_total": po_item.get("total"),
                            "qty_match": abs(inv_item.get("qty", 0) - po_item.get("qty", 0)) < 0.01
                        })
                        break
            
            # Compute score: 50% amount match, 50% line item match
            amount_score = 1.0 - min(1.0, amount_diff_pct / tolerance_pct) if not tolerance_exceeded else 0.0
            line_score = matched_count / len(invoice_line_items) if invoice_line_items else 0.0
            
            match_score = (amount_score * 0.5) + (line_score * 0.5)
            
            po_ids = [item.get("po_id", "unknown") for item in po_line_items if item.get("po_id")]
            
            result = {
                "match_score": match_score,
                "evidence": {
                    "po_ids": list(set(po_ids)),
                    "line_item_matches": line_item_matches,
                    "amount_diff": amount_diff,
                    "tolerance_exceeded": tolerance_exceeded,
                    "amount_diff_pct": amount_diff_pct
                }
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "compute_match_score", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "compute_match_score", False, duration_ms, str(e))
            raise
    
    def build_accounting_entries(
        self,
        invoice: InvoicePayload,
        po_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Build accounting entries (debits/credits).
        
        Args:
            invoice: Invoice payload
            po_data: Optional PO data
            
        Returns:
            List of accounting entries
        """
        start_time = time.time()
        try:
            entries = [
                {
                    "account": "Accounts Payable",
                    "debit": 0,
                    "credit": invoice.get("amount", 0),
                    "description": f"Invoice {invoice.get('invoice_id')} - AP"
                },
                {
                    "account": "Expense Account",
                    "debit": invoice.get("amount", 0),
                    "credit": 0,
                    "description": f"Invoice {invoice.get('invoice_id')} - Expense"
                }
            ]
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "build_accounting_entries", True, duration_ms)
            
            return entries
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("COMMON", "build_accounting_entries", False, duration_ms, str(e))
            raise

