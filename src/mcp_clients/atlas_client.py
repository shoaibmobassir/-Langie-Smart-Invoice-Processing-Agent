"""ATLAS MCP client - abilities requiring external systems."""

import os
from typing import Dict, Any, List, Optional
import time
from src.logging.logger import log_mcp_call
from src.state.models import VendorProfile, InvoicePayload

# Optional imports for OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None


class ATLASClient:
    """
    ATLAS MCP client wrapper.
    
    Handles abilities that require external systems:
    - OCR (if remote)
    - Enrichment APIs
    - ERP fetch/post
    - Notifications
    """
    
    def __init__(self):
        """Initialize ATLAS client."""
        # In production, this would connect to actual MCP server
        # For demo, we use mocked implementations
        pass
    
    def ocr_extract(self, attachments: List[str], provider: str = "tesseract") -> Dict[str, Any]:
        """
        Extract text from invoice attachments using OCR.
        
        Args:
            attachments: List of file paths/URLs
            provider: OCR provider name
            
        Returns:
            Dict with extracted text and metadata
        """
        start_time = time.time()
        try:
            extracted_text = ""
            all_text = []
            
            for attachment_path in attachments:
                try:
                    # Normalize path (handle relative paths)
                    if not os.path.isabs(attachment_path):
                        # Try relative to current directory
                        full_path = os.path.abspath(attachment_path)
                    else:
                        full_path = attachment_path
                    
                    # Try to read PDF file
                    if attachment_path.lower().endswith('.pdf'):
                        # Try PyPDF2 first
                        try:
                            import PyPDF2
                            with open(full_path, 'rb') as file:
                                pdf_reader = PyPDF2.PdfReader(file)
                                page_text = []
                                for page in pdf_reader.pages:
                                    page_text.append(page.extract_text())
                                file_text = "\n".join(page_text)
                                if file_text.strip():
                                    all_text.append(file_text)
                                else:
                                    # Empty PDF, use fallback
                                    all_text.append(f"PDF file {attachment_path} processed (no text extracted)")
                        except (ImportError, Exception) as e:
                            # Fallback to reading as text file (for mock PDFs)
                            try:
                                with open(full_path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                    if content.strip():
                                        all_text.append(content)
                            except Exception:
                                # If file doesn't exist or can't read, generate mock based on filename
                                filename = os.path.basename(attachment_path)
                                if 'invoice_001' in filename or 'invoice_001' in attachment_path:
                                    all_text.append("""INVOICE
Invoice ID: INV-2024-001
Vendor: Acme Corporation
Tax ID: TAX-123456
Invoice Date: 2024-01-15
Due Date: 2024-02-15

Line Item 1: Widget A - Qty: 10, Price: $50.00, Total: $500.00
Line Item 2: Widget B - Qty: 5, Price: $100.00, Total: $500.00

PO Reference: PO-2024-001
Total: $1000.00""")
                                elif 'invoice_002' in filename or 'invoice_002' in attachment_path:
                                    all_text.append("""INVOICE
Invoice ID: INV-2024-002
Vendor: Beta Industries
Tax ID: TAX-789012
Invoice Date: 2024-01-20
Due Date: 2024-02-20

Line Item 1: Unknown Item - Qty: 100, Price: $60.00, Total: $6000.00

Total: $6000.00""")
                                else:
                                    all_text.append(f"Invoice text extracted from {filename} using {provider}")
                    elif attachment_path.lower().endswith(('.png', '.jpg', '.jpeg', '.jpe', '.bmp', '.tiff', '.tif')):
                        # Image file - use Tesseract OCR
                        if not OCR_AVAILABLE:
                            all_text.append(f"Image file {os.path.basename(attachment_path)} detected but OCR libraries (pytesseract/PIL) not installed. Install with: pip install pytesseract pillow")
                        else:
                            try:
                                # Open image using PIL
                                img = Image.open(full_path)
                                
                                # Perform OCR based on provider
                                if provider.lower() == "tesseract" or provider.lower() in ["google_vision", "aws_textract"]:
                                    # Use Tesseract OCR (or as fallback for other providers)
                                    try:
                                        extracted_image_text = pytesseract.image_to_string(img)
                                        if extracted_image_text.strip():
                                            all_text.append(f"=== OCR Text from {os.path.basename(attachment_path)} ===\n{extracted_image_text}")
                                        else:
                                            all_text.append(f"Image file {os.path.basename(attachment_path)} processed but no text detected by OCR")
                                    except Exception as ocr_error:
                                        error_msg = str(ocr_error)
                                        if "tesseract" in error_msg.lower() or "command not found" in error_msg.lower():
                                            all_text.append(f"Image file {os.path.basename(attachment_path)} detected but Tesseract OCR binary not found. Please install Tesseract OCR: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
                                        else:
                                            all_text.append(f"Error during OCR processing of {os.path.basename(attachment_path)}: {error_msg}")
                                else:
                                    # Default to Tesseract
                                    try:
                                        extracted_image_text = pytesseract.image_to_string(img)
                                        if extracted_image_text.strip():
                                            all_text.append(f"=== OCR Text from {os.path.basename(attachment_path)} ===\n{extracted_image_text}")
                                        else:
                                            all_text.append(f"Image file {os.path.basename(attachment_path)} processed but no text detected")
                                    except Exception as ocr_error:
                                        all_text.append(f"Error during OCR: {str(ocr_error)}")
                            except Exception as img_error:
                                # Error opening/processing image
                                error_msg = str(img_error)
                                all_text.append(f"Error processing image {os.path.basename(attachment_path)}: {error_msg}")
                    else:
                        # Try to read as text file
                        try:
                            with open(full_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                if content.strip():
                                    all_text.append(content)
                        except Exception:
                            all_text.append(f"File {os.path.basename(attachment_path)} processed")
                except FileNotFoundError:
                    # Generate mock text based on invoice patterns
                    filename = os.path.basename(attachment_path)
                    all_text.append(f"Invoice text extracted from {filename} using {provider}")
                except Exception as e:
                    # Log error but continue
                    all_text.append(f"Error processing {attachment_path}: {str(e)}")
            
            extracted_text = "\n\n".join(all_text) if all_text else "No text extracted"
            
            result = {
                "text": extracted_text,
                "provider": provider,
                "confidence": 0.95 if all_text else 0.0,
                "metadata": {
                    "page_count": len(attachments),
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "files_processed": len(attachments)
                }
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "ocr_extract", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "ocr_extract", False, duration_ms, str(e))
            # Return minimal result instead of raising
            return {
                "text": f"Error extracting text: {str(e)}",
                "provider": provider,
                "confidence": 0.0,
                "metadata": {"error": str(e)}
            }
    
    def enrich_vendor(
        self,
        vendor_name: str,
        tax_id: Optional[str] = None,
        provider: str = "vendor_db"
    ) -> Dict[str, Any]:
        """
        Enrich vendor data from external sources.
        
        Args:
            vendor_name: Vendor name
            tax_id: Optional tax ID
            provider: Enrichment provider
            
        Returns:
            Enriched vendor data
        """
        start_time = time.time()
        try:
            # Mock enrichment
            # In production, this would call Clearbit/PDL/Vendor DB via MCP
            enrichment_meta = {
                "provider": provider,
                "credit_score": 0.85,
                "risk_score": 0.25,
                "verified": True,
                "enrichment_date": "2024-01-15T00:00:00Z"
            }
            
            if provider == "clearbit":
                enrichment_meta["company_data"] = {
                    "domain": f"{vendor_name.lower().replace(' ', '')}.com",
                    "industry": "Manufacturing"
                }
            elif provider == "people_data_labs":
                enrichment_meta["contact_data"] = {
                    "email": f"contact@{vendor_name.lower().replace(' ', '')}.com"
                }
            
            result = {
                "normalized_name": vendor_name,
                "tax_id": tax_id or "TAX-123456",
                "enrichment_meta": enrichment_meta
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "enrich_vendor", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "enrich_vendor", False, duration_ms, str(e))
            raise
    
    def fetch_po(self, po_references: List[str], erp_connector: str = "mock_erp") -> List[Dict[str, Any]]:
        """
        Fetch Purchase Orders from ERP.
        
        Args:
            po_references: List of PO IDs/references
            erp_connector: ERP connector name
            
        Returns:
            List of PO data
        """
        start_time = time.time()
        try:
            # Mock PO fetch
            # In production, this would call SAP/NetSuite/etc via MCP
            pos = []
            for po_ref in po_references or ["PO-2024-001"]:
                pos.append({
                    "po_id": po_ref,
                    "vendor": "Acme Corp",
                    "total": 1000.00,
                    "status": "OPEN",
                    "line_items": [
                        {"desc": "Widget A", "qty": 10, "unit_price": 50.00, "total": 500.00, "po_id": po_ref},
                        {"desc": "Widget B", "qty": 5, "unit_price": 100.00, "total": 500.00, "po_id": po_ref}
                    ],
                    "created_date": "2024-01-01"
                })
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_po", True, duration_ms)
            
            return pos
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_po", False, duration_ms, str(e))
            raise
    
    def fetch_grn(self, po_ids: List[str], erp_connector: str = "mock_erp") -> List[Dict[str, Any]]:
        """
        Fetch Goods Received Notes from ERP.
        
        Args:
            po_ids: List of PO IDs
            erp_connector: ERP connector name
            
        Returns:
            List of GRN data
        """
        start_time = time.time()
        try:
            # Mock GRN fetch
            grns = []
            for po_id in po_ids:
                grns.append({
                    "grn_id": f"GRN-{po_id}",
                    "po_id": po_id,
                    "received_date": "2024-01-10",
                    "status": "RECEIVED"
                })
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_grn", True, duration_ms)
            
            return grns
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_grn", False, duration_ms, str(e))
            raise
    
    def fetch_history(self, vendor_name: str, erp_connector: str = "mock_erp") -> List[Dict[str, Any]]:
        """
        Fetch historical invoices for vendor.
        
        Args:
            vendor_name: Vendor name
            erp_connector: ERP connector name
            
        Returns:
            List of historical invoice data
        """
        start_time = time.time()
        try:
            # Mock history fetch
            history = [
                {
                    "invoice_id": "INV-2023-001",
                    "vendor": vendor_name,
                    "amount": 5000.00,
                    "status": "PAID",
                    "date": "2023-12-01"
                }
            ]
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_history", True, duration_ms)
            
            return history
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "fetch_history", False, duration_ms, str(e))
            raise
    
    def post_to_erp(
        self,
        accounting_entries: List[Dict[str, Any]],
        invoice: InvoicePayload,
        erp_connector: str = "mock_erp"
    ) -> Dict[str, Any]:
        """
        Post journal entries to ERP.
        
        Args:
            accounting_entries: Accounting entries
            invoice: Invoice payload
            erp_connector: ERP connector name
            
        Returns:
            Dict with ERP transaction ID and status
        """
        start_time = time.time()
        try:
            # Mock ERP posting
            erp_txn_id = f"TXN-{invoice.get('invoice_id', 'UNKNOWN')}-{int(time.time())}"
            
            result = {
                "erp_txn_id": erp_txn_id,
                "posted": True,
                "posted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "post_to_erp", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "post_to_erp", False, duration_ms, str(e))
            raise
    
    def schedule_payment(
        self,
        invoice: InvoicePayload,
        payment_amount: float,
        due_date: str
    ) -> Dict[str, Any]:
        """
        Schedule payment for invoice.
        
        Args:
            invoice: Invoice payload
            payment_amount: Payment amount
            due_date: Payment due date
            
        Returns:
            Dict with scheduled payment ID
        """
        start_time = time.time()
        try:
            # Mock payment scheduling
            scheduled_payment_id = f"PAY-{invoice.get('invoice_id', 'UNKNOWN')}-{int(time.time())}"
            
            result = {
                "scheduled_payment_id": scheduled_payment_id,
                "amount": payment_amount,
                "due_date": due_date,
                "status": "SCHEDULED"
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "schedule_payment", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "schedule_payment", False, duration_ms, str(e))
            raise
    
    def notify_vendor(
        self,
        vendor_email: str,
        invoice: InvoicePayload,
        email_provider: str = "sendgrid"
    ) -> Dict[str, Any]:
        """
        Send notification to vendor.
        
        Args:
            vendor_email: Vendor email address
            invoice: Invoice payload
            email_provider: Email provider name
            
        Returns:
            Dict with notification status
        """
        start_time = time.time()
        try:
            # Mock email notification
            result = {
                "sent": True,
                "provider": email_provider,
                "recipient": vendor_email,
                "message_id": f"msg-{int(time.time())}"
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "notify_vendor", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "notify_vendor", False, duration_ms, str(e))
            raise
    
    def notify_finance_team(
        self,
        message: str,
        slack_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Notify finance team (Slack/email).
        
        Args:
            message: Notification message
            slack_key: Optional Slack webhook key
            
        Returns:
            Dict with notification status
        """
        start_time = time.time()
        try:
            # Mock notification
            result = {
                "sent": True,
                "channel": "finance-team",
                "message_id": f"msg-{int(time.time())}"
            }
            
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "notify_finance_team", True, duration_ms)
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_mcp_call("ATLAS", "notify_finance_team", False, duration_ms, str(e))
            raise

