"""State models for LangGraph invoice processing workflow."""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    REQUIRES_MANUAL_HANDLING = "REQUIRES_MANUAL_HANDLING"
    FAILED = "FAILED"


class MatchResult(str, Enum):
    """Match result enumeration."""
    MATCHED = "MATCHED"
    FAILED = "FAILED"


class HumanDecision(str, Enum):
    """Human decision enumeration."""
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class WorkflowConfig(TypedDict, total=False):
    """Workflow configuration."""
    match_threshold: float
    two_way_tolerance_pct: float
    human_review_queue: str
    checkpoint_table: str
    default_db: str


class InvoicePayload(TypedDict, total=False):
    """Invoice payload input."""
    invoice_id: str
    vendor_name: str
    vendor_tax_id: str
    invoice_date: str
    due_date: str
    amount: float
    currency: str
    line_items: List[Dict[str, Any]]
    attachments: List[str]


class IntakeOutput(TypedDict, total=False):
    """INTAKE stage output."""
    raw_id: str
    ingest_ts: str
    validated: bool


class ParsedInvoice(TypedDict, total=False):
    """Parsed invoice data."""
    invoice_text: str
    parsed_line_items: List[Dict[str, Any]]
    detected_pos: List[str]
    currency: str
    parsed_dates: Dict[str, str]


class UnderstandOutput(TypedDict, total=False):
    """UNDERSTAND stage output."""
    parsed_invoice: ParsedInvoice


class VendorProfile(TypedDict, total=False):
    """Vendor profile."""
    normalized_name: str
    tax_id: str
    enrichment_meta: Dict[str, Any]
    credit_score: Optional[float]
    risk_score: Optional[float]


class Flags(TypedDict, total=False):
    """Validation flags."""
    missing_info: List[str]
    risk_score: float


class PrepareOutput(TypedDict, total=False):
    """PREPARE stage output."""
    vendor_profile: VendorProfile
    normalized_invoice: Dict[str, Any]
    flags: Flags


class RetrieveOutput(TypedDict, total=False):
    """RETRIEVE stage output."""
    matched_pos: List[Dict[str, Any]]
    matched_grns: List[Dict[str, Any]]
    history: List[Dict[str, Any]]


class MatchEvidence(TypedDict, total=False):
    """Match evidence."""
    po_ids: List[str]
    line_item_matches: List[Dict[str, Any]]
    amount_diff: float
    tolerance_exceeded: bool


class MatchTwoWayOutput(TypedDict, total=False):
    """MATCH_TWO_WAY stage output."""
    match_score: float
    match_result: str
    tolerance_pct: float
    match_evidence: MatchEvidence


class CheckpointHitlOutput(TypedDict, total=False):
    """CHECKPOINT_HITL stage output."""
    cp_id: str  # Renamed from checkpoint_id to avoid LangGraph reserved name conflict
    review_url: str
    paused_reason: str


class HitlDecisionOutput(TypedDict, total=False):
    """HITL_DECISION stage output."""
    human_decision: str
    reviewer_id: str
    resume_token: str
    next_stage: str


class ReconciliationOutput(TypedDict, total=False):
    """RECONCILE stage output."""
    accounting_entries: List[Dict[str, Any]]
    reconciliation_report: Dict[str, Any]


class ApproveOutput(TypedDict, total=False):
    """APPROVE stage output."""
    approval_status: str
    approver_id: Optional[str]


class PostingOutput(TypedDict, total=False):
    """POSTING stage output."""
    posted: bool
    erp_txn_id: Optional[str]
    scheduled_payment_id: Optional[str]


class NotifyOutput(TypedDict, total=False):
    """NOTIFY stage output."""
    notify_status: Dict[str, Any]
    notified_parties: List[str]


class CompleteOutput(TypedDict, total=False):
    """COMPLETE stage output."""
    final_payload: Dict[str, Any]
    audit_log: List[Dict[str, Any]]
    status: str


class WorkflowState(TypedDict, total=False):
    """
    Global workflow state that persists across all nodes.
    
    This is the main state object that LangGraph manages.
    """
    # Configuration
    config: WorkflowConfig
    
    # Input
    invoice_payload: InvoicePayload
    
    # HITL tracking
    paused: bool
    paused_reason: Optional[str]
    hitl_checkpoint_id: Optional[str]  # Renamed from checkpoint_id (reserved by LangGraph)
    thread_id: Optional[str]
    current_stage: Optional[str]
    resume_token: Optional[str]
    
    # Stage outputs
    intake: Optional[IntakeOutput]
    understand: Optional[UnderstandOutput]
    prepare: Optional[PrepareOutput]
    retrieve: Optional[RetrieveOutput]
    match_two_way: Optional[MatchTwoWayOutput]
    checkpoint: Optional[CheckpointHitlOutput]
    hitl: Optional[HitlDecisionOutput]
    reconcile: Optional[ReconciliationOutput]
    approve: Optional[ApproveOutput]
    posting: Optional[PostingOutput]
    notify: Optional[NotifyOutput]
    complete: Optional[CompleteOutput]
    
    # Metadata
    workflow_status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    
    # Errors
    error: Optional[Dict[str, Any]]

