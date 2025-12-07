"""Bigtool picker for dynamic tool selection."""

from typing import Dict, Any, List, Optional, Callable
from src.logging.logger import log_bigtool_selection


class ToolHandle:
    """Handle to a selected tool with metadata."""
    
    def __init__(self, name: str, capability: str, executor: Callable, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.capability = capability
        self.executor = executor
        self.metadata = metadata or {}


class BigtoolPicker:
    """
    Bigtool picker for capability-based tool selection.
    
    Selects tools from pools based on capability and context.
    For demo, uses simple rule-based selection with logging.
    """
    
    def __init__(self):
        """Initialize Bigtool picker with tool registry."""
        self._tool_registry: Dict[str, Dict[str, ToolHandle]] = {}
        self._setup_default_tools()
    
    def _setup_default_tools(self):
        """Setup default tool registry with mock implementations."""
        
        # OCR tools
        self._register_tool("ocr", "tesseract", self._ocr_tesseract, {"latency": "low", "cost": "free"})
        self._register_tool("ocr", "google_vision", self._ocr_google_vision, {"latency": "medium", "cost": "paid"})
        self._register_tool("ocr", "aws_textract", self._ocr_aws_textract, {"latency": "medium", "cost": "paid"})
        
        # Enrichment tools
        self._register_tool("enrichment", "vendor_db", self._enrichment_vendor_db, {"latency": "low", "cost": "internal"})
        self._register_tool("enrichment", "clearbit", self._enrichment_clearbit, {"latency": "medium", "cost": "paid"})
        self._register_tool("enrichment", "people_data_labs", self._enrichment_pdl, {"latency": "medium", "cost": "paid"})
        
        # ERP connectors
        self._register_tool("erp_connector", "mock_erp", self._erp_mock, {"latency": "low", "type": "mock"})
        self._register_tool("erp_connector", "sap_sandbox", self._erp_sap, {"latency": "high", "type": "real"})
        self._register_tool("erp_connector", "netsuite", self._erp_netsuite, {"latency": "medium", "type": "real"})
        
        # DB tools
        self._register_tool("db", "sqlite", self._db_sqlite, {"latency": "low", "type": "embedded"})
        self._register_tool("db", "postgres", self._db_postgres, {"latency": "medium", "type": "server"})
        self._register_tool("db", "dynamodb", self._db_dynamodb, {"latency": "medium", "type": "server"})
        
        # Storage tools
        self._register_tool("storage", "local_fs", self._storage_local, {"latency": "low", "type": "local"})
        self._register_tool("storage", "s3", self._storage_s3, {"latency": "medium", "type": "cloud"})
        self._register_tool("storage", "gcs", self._storage_gcs, {"latency": "medium", "type": "cloud"})
        
        # Email tools
        self._register_tool("email", "sendgrid", self._email_sendgrid, {"latency": "low", "cost": "paid"})
        self._register_tool("email", "smartlead", self._email_smartlead, {"latency": "low", "cost": "paid"})
        self._register_tool("email", "ses", self._email_ses, {"latency": "low", "cost": "paid"})
    
    def _register_tool(self, capability: str, name: str, executor: Callable, metadata: Dict[str, Any]):
        """Register a tool in the registry."""
        if capability not in self._tool_registry:
            self._tool_registry[capability] = {}
        self._tool_registry[capability][name] = ToolHandle(name, capability, executor, metadata)
    
    def select(
        self,
        capability: str,
        pool_hint: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolHandle:
        """
        Select a tool from the pool for the given capability.
        
        Args:
            capability: Capability name (ocr, enrichment, erp_connector, db, email, storage)
            pool_hint: Optional list of preferred tool names
            context: Optional context for selection logic
            
        Returns:
            Selected ToolHandle
        """
        context = context or {}
        
        # Get available tools for this capability
        available_tools = self._tool_registry.get(capability, {})
        
        if not available_tools:
            raise ValueError(f"No tools available for capability: {capability}")
        
        # Filter by pool_hint if provided
        candidate_pool = {}
        if pool_hint:
            for tool_name in pool_hint:
                if tool_name in available_tools:
                    candidate_pool[tool_name] = available_tools[tool_name]
        else:
            candidate_pool = available_tools
        
        if not candidate_pool:
            # Fallback to any available tool
            candidate_pool = available_tools
        
        # Selection logic (for demo, prefer mock/low-cost options)
        selected_tool = None
        reason = "default_selection"
        
        # Prefer mock tools for demo
        for tool_name, tool_handle in candidate_pool.items():
            if "mock" in tool_name.lower() or "local" in tool_name.lower() or "sqlite" in tool_name.lower():
                selected_tool = tool_handle
                reason = f"prefer_demo_tool_{tool_name}"
                break
        
        # If no mock found, use first available
        if not selected_tool:
            selected_tool = list(candidate_pool.values())[0]
            reason = f"first_available_{selected_tool.name}"
        
        log_bigtool_selection(
            capability=capability,
            pool=list(candidate_pool.keys()),
            selected_tool=selected_tool.name,
            reason=reason
        )
        
        return selected_tool
    
    # Mock tool implementations
    
    def _ocr_tesseract(self, *args, **kwargs):
        """Tesseract OCR implementation."""
        return {"provider": "tesseract", "text": "Mock OCR text"}
    
    def _ocr_google_vision(self, *args, **kwargs):
        """Google Vision OCR implementation."""
        return {"provider": "google_vision", "text": "Mock OCR text"}
    
    def _ocr_aws_textract(self, *args, **kwargs):
        """AWS Textract OCR implementation."""
        return {"provider": "aws_textract", "text": "Mock OCR text"}
    
    def _enrichment_vendor_db(self, *args, **kwargs):
        """Vendor DB enrichment implementation."""
        return {"provider": "vendor_db", "data": {}}
    
    def _enrichment_clearbit(self, *args, **kwargs):
        """Clearbit enrichment implementation."""
        return {"provider": "clearbit", "data": {}}
    
    def _enrichment_pdl(self, *args, **kwargs):
        """People Data Labs enrichment implementation."""
        return {"provider": "people_data_labs", "data": {}}
    
    def _erp_mock(self, *args, **kwargs):
        """Mock ERP connector."""
        return {"provider": "mock_erp", "data": {}}
    
    def _erp_sap(self, *args, **kwargs):
        """SAP ERP connector."""
        return {"provider": "sap_sandbox", "data": {}}
    
    def _erp_netsuite(self, *args, **kwargs):
        """NetSuite ERP connector."""
        return {"provider": "netsuite", "data": {}}
    
    def _db_sqlite(self, *args, **kwargs):
        """SQLite DB connector."""
        return {"provider": "sqlite", "conn": None}
    
    def _db_postgres(self, *args, **kwargs):
        """PostgreSQL DB connector."""
        return {"provider": "postgres", "conn": None}
    
    def _db_dynamodb(self, *args, **kwargs):
        """DynamoDB connector."""
        return {"provider": "dynamodb", "conn": None}
    
    def _storage_local(self, *args, **kwargs):
        """Local filesystem storage."""
        return {"provider": "local_fs", "path": "./storage"}
    
    def _storage_s3(self, *args, **kwargs):
        """S3 storage."""
        return {"provider": "s3", "bucket": "invoices"}
    
    def _storage_gcs(self, *args, **kwargs):
        """Google Cloud Storage."""
        return {"provider": "gcs", "bucket": "invoices"}
    
    def _email_sendgrid(self, *args, **kwargs):
        """SendGrid email provider."""
        return {"provider": "sendgrid", "sent": True}
    
    def _email_smartlead(self, *args, **kwargs):
        """SmartLead email provider."""
        return {"provider": "smartlead", "sent": True}
    
    def _email_ses(self, *args, **kwargs):
        """AWS SES email provider."""
        return {"provider": "ses", "sent": True}


# Global instance
bigtool_picker = BigtoolPicker()

