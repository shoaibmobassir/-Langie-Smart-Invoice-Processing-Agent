# 🧾 Langie - Invoice Processing LangGraph Agent

**Langie** is a production-ready, LangGraph-based invoice processing agent that automates the entire invoice lifecycle from intake to payment, with intelligent Human-In-The-Loop (HITL) checkpoints for quality assurance.

## Overview

Langie demonstrates advanced workflow orchestration capabilities using LangGraph, featuring:
- ✅ **12-stage workflow orchestration** with state machine patterns
- ✅ **Persistent checkpoint & resume** using SQLite via LangGraph SqliteSaver
- ✅ **Human-In-The-Loop (HITL) routing** for quality control
- ✅ **Bigtool-based dynamic tool selection** for flexible integrations
- ✅ **MCP client orchestration** (COMMON & ATLAS servers)
- ✅ **File upload support** with OCR processing for PDF/image invoices (Tesseract OCR)
- ✅ **Full-stack application** with React frontend and FastAPI backend
- ✅ **Structured logging** for observability
- ✅ **Auto-generated reviewer IDs** and automatic workflow resume
- ✅ **Complete workflow visibility** - see all invoices including auto-completed ones
- ✅ **Sorting and filtering** capabilities in database preview
- ✅ **Delete functionality** for workflow management
- ✅ **Comprehensive test suite** with 15+ auto-complete scenarios

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   React UI      │────────▶│   FastAPI API    │────────▶│  LangGraph   │
│   (Frontend)    │         │   (Backend)      │         │  Workflow    │
└─────────────────┘         └──────────────────┘         └──────────────┘
                                     │                            │
                                     │                            │
                            ┌────────┴────────┐         ┌─────────┴─────────┐
                            │                 │         │                   │
                            ▼                 ▼         ▼                   ▼
                    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                    │   SQLite DB  │  │ MCP Clients  │  │   Bigtool    │
                    │ (Checkpoints)│  │ (COMMON/     │  │   Picker     │
                    │              │  │  ATLAS)      │  │              │
                    └──────────────┘  └──────────────┘  └──────────────┘
```

## Project Structure

```
MCP_assignment/
├── workflow.json                    # Workflow configuration (12 stages)
├── requirements.txt                 # Python dependencies
├── demo_run.py                     # Demo script (success + HITL scenarios)
├── demo.sh                         # Automated demo launcher
├── demo_workflow.py                # Automated demo scenarios with logging
├── stop_demo.sh                    # Stop demo servers
├── start_backend.sh                # Backend startup helper script
├── test_end_to_end.py              # End-to-end test suite
├── test_auto_complete_scenarios.py # Auto-complete test scenarios
├── sample_invoice.json             # Sample invoice payload
├── DEMO_GUIDE.md                   # Complete demo documentation
├── DEMO_PRESENTATION.md            # Presentation guide
├── QUICK_DEMO.md                   # Quick reference guide
├── EXPLANATION_SCRIPT.md           # Explanation script for presentations
├── VIDEO_SCRIPT.md                 # Video recording script
├── AUTO_COMPLETE_TEST_CASES.md     # Auto-complete test cases documentation
│
├── src/
│   ├── state/
│   │   └── models.py               # TypedDict state models (WorkflowState)
│   ├── graph/
│   │   ├── builder.py              # LangGraph StateGraph construction
│   │   ├── routing.py              # Conditional routing functions
│   │   └── node_wrapper.py         # Runtime context injection
│   ├── nodes/                      # 12 workflow stage nodes
│   │   ├── intake.py               # INTAKE - Validate and persist
│   │   ├── understand.py           # UNDERSTAND - OCR extraction
│   │   ├── prepare.py              # PREPARE - Vendor normalization
│   │   ├── retrieve.py             # RETRIEVE - ERP data fetch
│   │   ├── match_two_way.py        # MATCH_TWO_WAY - Match scoring
│   │   ├── checkpoint_hitl.py      # CHECKPOINT_HITL - Pause & save
│   │   ├── hitl_decision.py        # HITL_DECISION - Process decision
│   │   ├── reconcile.py            # RECONCILE - Accounting entries
│   │   ├── approve.py              # APPROVE - Approval policies
│   │   ├── posting.py              # POSTING - ERP posting
│   │   ├── notify.py               # NOTIFY - Notifications
│   │   └── complete.py             # COMPLETE - Finalization
│   ├── tools/
│   │   └── bigtool_picker.py       # Dynamic tool selection
│   ├── mcp_clients/
│   │   ├── common_client.py        # COMMON server (normalize, match, accounting)
│   │   └── atlas_client.py         # ATLAS server (OCR, ERP, notifications)
│   ├── storage/
│   │   ├── checkpoint_store.py     # LangGraph SqliteSaver wrapper
│   │   └── human_review_repo.py    # Human review queue management
│   ├── api/
│   │   └── app.py                  # FastAPI application
│   ├── config/
│   │   └── workflow_loader.py      # workflow.json loader
│   └── logging/
│       └── logger.py               # Structured logging helpers
│
├── frontend/                       # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx                 # Main app with routing
│   │   ├── components/
│   │   │   ├── InvoiceSubmit.jsx   # Invoice submission form (with file upload)
│   │   │   ├── HumanReview.jsx     # HITL review interface
│   │   │   └── DatabasePreview.jsx # Database preview & audit trail
│   │   └── main.jsx
│   └── package.json
│
├── test_data/
│   ├── invoice_pass.json           # Successful match scenario
│   ├── invoice_fail.json           # HITL trigger scenario
│   ├── invoice_large.json          # Large amount (>$10K)
│   ├── invoice_missing.json        # Missing fields
│   ├── invoices_auto_complete.json # 15 auto-complete test cases
│   ├── test_data/
│   │   ├── invoice_001.pdf         # Sample PDF invoices
│   │   ├── invoice_002.pdf
│   │   ├── invoice_003.pdf
│   │   └── invoice_004.pdf
│   ├── uploaded/                   # Uploaded files directory
│   ├── invoice_pass_image.png      # Sample PNG invoice for OCR
│   ├── invoice_fail_image.png      # Sample PNG invoice (HITL scenario)
│   └── invoice_large_image.png     # Sample PNG invoice (large amount)
│
├── demo.db                         # SQLite database (created on first run)
├── start_backend.sh                # Backend startup script
├── start_frontend.sh               # Frontend startup script
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.11+ (3.13 recommended)
- Node.js 18+ and npm
- pip

### Installation

```bash
# 1. Clone repository (if applicable)
# git clone <repository-url>
# cd MCP_assignment

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

#### Option 1: Automated Demo (Recommended for first-time users)

```bash
# Start everything (backend + frontend)
./demo.sh

# In another terminal, run automated demo scenarios
python3 demo_workflow.py

# Access:
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Option 2: Use Helper Scripts

```bash
# Terminal 1 - Backend
./start_backend.sh
# OR manually with correct Python:
/Users/shoaibmobassir/miniconda3/bin/python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
# Backend runs on http://localhost:8000

# Terminal 2 - Frontend
cd frontend && npm run dev
# Frontend runs on http://localhost:5173
```

#### Option 3: Manual Start

**Important**: Use the correct Python environment that has all dependencies installed.

```bash
# Terminal 1 - Backend
# Use miniconda Python (or your virtual environment)
/Users/shoaibmobassir/miniconda3/bin/python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Note**: If you get `ModuleNotFoundError: No module named 'uvicorn'`, ensure you're using the Python environment where dependencies are installed. Check with:
```bash
which python3
python3 -m pip list | grep uvicorn
```

### Quick Demo

```bash
# Run demo script (2 scenarios: success + HITL)
python demo_run.py
```

## Workflow Stages (Detailed)

The workflow consists of **12 stages** executed sequentially with conditional branching:

### 1. **INTAKE** (Deterministic)
- **Purpose**: Validate invoice payload schema and persist raw data
- **Tools**: BigtoolPicker (storage), Database
- **Output**: `raw_id`, `ingest_ts`, `validated`
- **Implementation**: `src/nodes/intake.py`

### 2. **UNDERSTAND** (Deterministic)
- **Purpose**: Extract text from PDF/image attachments using OCR and parse invoice data
- **Tools**: BigtoolPicker (OCR: google_vision, tesseract, aws_textract), ATLAS client
- **Features**: 
  - **PDF files**: Uses PyPDF2 for direct text extraction from PDFs
  - **Image files**: Uses Tesseract OCR for text extraction from images (PNG, JPG, JPEG, BMP, TIFF)
  - Parses line items, dates, PO references from extracted text
  - Falls back gracefully if OCR libraries are not available
- **OCR Implementation**: 
  - Tesseract OCR (open-source, default)
  - Supports multiple image formats
  - Returns structured text with metadata
- **Output**: `parsed_invoice` (text, line_items, detected_pos, dates, currency)
- **Implementation**: `src/nodes/understand.py`

### 3. **PREPARE** (Deterministic)
- **Purpose**: Normalize vendor name and enrich vendor profile
- **Tools**: BigtoolPicker (enrichment: clearbit, people_data_labs, vendor_db), COMMON client
- **Output**: `vendor_profile`, `normalized_invoice`, `flags` (missing_info, risk_score)
- **Implementation**: `src/nodes/prepare.py`

### 4. **RETRIEVE** (Deterministic)
- **Purpose**: Fetch Purchase Orders (POs), Goods Receipt Notes (GRNs), and historical invoices from ERP
- **Tools**: BigtoolPicker (ERP: sap_sandbox, netsuite, mock_erp), ATLAS client
- **Output**: `matched_pos`, `matched_grns`, `history`
- **Implementation**: `src/nodes/retrieve.py`

### 5. **MATCH_TWO_WAY** (Deterministic)
- **Purpose**: Compute 2-way match score between invoice and PO
- **Logic**: 
  - Calculates match score based on amount, line items, vendor
  - Applies tolerance percentage (default: 5%)
  - Sets `match_result = "MATCHED"` if `match_score >= threshold` (default: 0.90)
  - Sets `match_result = "FAILED"` otherwise
- **Output**: `match_score`, `match_result`, `tolerance_pct`, `match_evidence`
- **Routing**: 
  - If `MATCHED` → Continue to RECONCILE
  - If `FAILED` → Route to CHECKPOINT_HITL
- **Implementation**: `src/nodes/match_two_way.py`

### 6. **CHECKPOINT_HITL** (Deterministic, Conditional)
- **Purpose**: Create persistent checkpoint and pause workflow for human review
- **Trigger**: Only executed if `match_result == "FAILED"`
- **Actions**:
  - Persists full workflow state to SQLite
  - Creates entry in `human_review_queue` table
  - Generates `checkpoint_id` and `review_url`
  - Sets `paused = true` in state
- **Tools**: BigtoolPicker (db: postgres, sqlite, dynamodb), QueueService
- **Output**: `cp_id`, `review_url`, `paused_reason`
- **Implementation**: `src/nodes/checkpoint_hitl.py`

### 7. **HITL_DECISION** (Non-Deterministic)
- **Purpose**: Process human decision and resume workflow
- **Trigger**: After human submits decision via `/human-review/decision` API
- **Input**: `human_decision` ("ACCEPT" or "REJECT"), `reviewer_id`, `notes`
- **Routing**:
  - If `ACCEPT` → Continue to RECONCILE
  - If `REJECT` → Skip to COMPLETE (status: MANUAL_HANDOFF)
- **Output**: `human_decision`, `reviewer_id`, `resume_token`, `next_stage`
- **Implementation**: `src/nodes/hitl_decision.py`

### 8. **RECONCILE** (Deterministic)
- **Purpose**: Build accounting entries (debits/credits) and reconciliation report
- **Tools**: AccountingEngine, COMMON client
- **Output**: `accounting_entries`, `reconciliation_report`
- **Implementation**: `src/nodes/reconcile.py`

### 9. **APPROVE** (Deterministic)
- **Purpose**: Apply approval policies
- **Logic**: 
  - Auto-approve if amount < threshold
  - Escalate to approver if amount >= threshold
- **Output**: `approval_status`, `approver_id`
- **Implementation**: `src/nodes/approve.py`

### 10. **POSTING** (Deterministic)
- **Purpose**: Post journal entries to ERP and schedule payment
- **Tools**: BigtoolPicker (ERP connector), Payments service
- **Output**: `posted`, `erp_txn_id`, `scheduled_payment_id`
- **Implementation**: `src/nodes/posting.py`

### 11. **NOTIFY** (Deterministic)
- **Purpose**: Send notifications to vendor and finance team
- **Tools**: BigtoolPicker (email: sendgrid, smartlead, ses), Messaging
- **Output**: `notify_status`, `notified_parties`
- **Implementation**: `src/nodes/notify.py`

### 12. **COMPLETE** (Deterministic)
- **Purpose**: Produce final payload, audit log, and mark workflow completed
- **Output**: `final_payload`, `audit_log`, `status` (COMPLETED, MANUAL_HANDOFF, FAILED)
- **Implementation**: `src/nodes/complete.py`

## Human-In-The-Loop (HITL) Flow

```
Invoice Submission
       │
       ▼
[MATCH_TWO_WAY] ──match_score < 0.90──▶ [CHECKPOINT_HITL]
       │                                       │
       │                                       ▼
   match_score >= 0.90              Save checkpoint to DB
       │                              Add to review queue
       │                              Pause workflow
       │                                       │
       │                                       ▼
       │                            [HITL_DECISION] ◀─── Human Review
       │                                       │            (ACCEPT/REJECT)
       │                                       │
       │                              ┌────────┴────────┐
       │                              │                 │
       ▼                              ▼                 ▼
[RECONCILE]                    [RECONCILE]      [COMPLETE]
       │                              │         (MANUAL_HANDOFF)
       ▼                              ▼
[APPROVE]                        [APPROVE]
       │                              │
       ▼                              ▼
[POSTING]                        [POSTING]
       │                              │
       ▼                              ▼
[NOTIFY]                         [NOTIFY]
       │                              │
       ▼                              ▼
[COMPLETE]                      [COMPLETE]
```

## 🌐 API Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

### 1. POST `/workflow/run`
Start invoice processing workflow with optional file uploads.

**Content-Type**: `multipart/form-data` (for file uploads) or `application/json` (backward compatible)

**Form Data Parameters**:
- `invoice` (string, required): JSON string of invoice payload
- `file_count` (string, optional): Number of uploaded files (default: "0")
- `file_0` to `file_4` (file, optional): Up to 5 PDF/image files

**Request Body (JSON alternative)**:
```json
{
  "invoice_id": "INV-2024-001",
  "vendor_name": "Acme Corporation",
  "vendor_tax_id": "TAX-123456",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "amount": 1000.00,
  "currency": "USD",
  "line_items": [
    {
      "desc": "Widget A",
      "qty": 10,
      "unit_price": 50.00,
      "total": 500.00
    },
    {
      "desc": "Widget B",
      "qty": 5,
      "unit_price": 100.00,
      "total": 500.00
    }
  ],
  "attachments": ["path/to/invoice.pdf"]
}
```

**Response**:
```json
{
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PAUSED" | "COMPLETED" | "IN_PROGRESS",
  "checkpoint_id": "checkpoint-uuid" (if PAUSED),
  "review_url": "http://localhost:3000/review?checkpoint=uuid" (if PAUSED),
  "message": "Workflow paused for human review" | "Workflow completed successfully"
}
```

**Example (with file upload)**:
```bash
curl -X POST http://localhost:8000/workflow/run \
  -F "invoice={\"invoice_id\":\"INV-001\",\"vendor_name\":\"Acme\",...}" \
  -F "file_0=@invoice.pdf" \
  -F "file_count=1"
```

### 2. GET `/human-review/pending`
Get all pending human reviews.

**Response**:
```json
{
  "items": [
    {
      "checkpoint_id": "uuid",
      "invoice_id": "INV-2024-001",
      "vendor_name": "Acme Corp",
      "amount": 1000.00,
      "created_at": "2024-01-15T10:00:00Z",
      "reason_for_hold": "Match score below threshold",
      "review_url": "http://localhost:3000/review?checkpoint=uuid",
      "thread_id": "550e8400-..."
    }
  ]
}
```

### 3. POST `/human-review/decision`
Submit human decision and resume workflow.

**Request**:
```json
{
  "checkpoint_id": "uuid",
  "decision": "ACCEPT" | "REJECT",
  "reviewer_id": "reviewer_001" (optional, auto-generated if not provided),
  "notes": "Looks good, proceed with payment"
}
```

**Response**:
```json
{
  "resume_token": "thread_id:checkpoint_id",
  "next_stage": "RECONCILE" | "COMPLETE",
  "message": "Workflow resumed to RECONCILE"
}
```

**Note**: If decision is "ACCEPT", workflow automatically continues to completion.

### 4. GET `/workflow/status/{thread_id}`
Get current status of a workflow by thread ID.

**Response**:
```json
{
  "thread_id": "550e8400-...",
  "status": "PAUSED" | "COMPLETED" | "IN_PROGRESS",
  "current_stage": "CHECKPOINT_HITL",
  "paused": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 5. GET `/workflow/all`
Get all workflows/invoices from database with detailed stage outputs.

**Includes**:
- Workflows that went through HITL (from `human_review_queue`)
- Workflows that auto-completed without HITL (from LangGraph checkpointer)
- Complete visibility into all processed invoices

**Response**:
```json
{
  "workflows": [
    {
      "checkpoint_id": "uuid",
      "invoice_id": "INV-2024-001",
      "thread_id": "550e8400-...",
      "vendor_name": "Acme Corp",
      "amount": 1000.00,
      "status": "COMPLETED",
      "paused": false,
      "current_stage": "COMPLETE",
      "created_at": "2024-01-15T10:00:00Z",
      "decision": "ACCEPT" | null,
      "reviewer_id": "reviewer_001",
      "went_through_hitl": false,
      "reason_for_hold": null,
      "notes": "Approved",
      "stages": {
        "intake": {...},
        "understand": {...},
        "prepare": {...},
        ...
      },
      "invoice_payload": {...}
    }
  ],
  "total": 10
}
```

### 6. DELETE `/workflow/{thread_id}`
Delete a workflow by thread ID.

**Deletes**:
- Workflow state from LangGraph checkpointer
- Entry from `human_review_queue` (if present)

**Response**:
```json
{
  "message": "Workflow {thread_id} deleted successfully"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:8000/workflow/550e8400-e29b-41d4-a716-446655440000
```

## Frontend Features

### 1. Invoice Submission Page (`/`)
- **File Upload**: Upload PDF/image invoices (up to 5 files)
- **Form Fields**: Invoice ID, vendor details, dates, amount, currency, line items
- **Dynamic Line Items**: Add/remove line items dynamically
- **Auto-calculation**: Line item totals calculated automatically
- **File Preview**: Shows selected files with size before submission
- **Real-time Validation**: Form validation before submission

### 2. Human Review Page (`/review`)
- **Pending Reviews List**: Display all invoices awaiting review
- **Auto-refresh**: Automatically refreshes every 5 seconds
- **Auto-generated Reviewer ID**: Reviewer ID automatically generated (can be customized)
- **Review Actions**: Accept or Reject with optional notes
- **Automatic Resume**: Workflow continues automatically after "ACCEPT" decision
- **Review Details**: Shows invoice ID, vendor, amount, match score, reason for hold

### 3. Database Preview Page (`/database`)
- **All Workflows View**: Complete list of all processed invoices (including auto-completed)
- **Filtering**: Filter by status:
  - **All**: All invoices
  - **Pending**: Workflows waiting for review
  - **Accepted**: Human-accepted workflows (HITL decision: ACCEPT)
  - **Rejected**: Human-rejected workflows (HITL decision: REJECT)
  - **Completed**: All completed workflows (auto-completed + human-accepted/rejected)
- **Sorting**: Sort by:
  - Created At (newest/oldest first)
  - Amount (highest/lowest)
  - Vendor Name (A-Z / Z-A)
  - Invoice ID (A-Z / Z-A)
  - Status (alphabetical)
- **Delete Functionality**: Delete workflows with confirmation dialog
- **Detailed View**: Expandable cards showing all stage outputs
- **JSON Viewer**: Formatted JSON display of workflow state
- **Status Badges**: Visual indicators for workflow status and decisions
- **Decision Display**: Shows:
  - "Completed (No Review Needed)" for auto-completed invoices
  - "ACCEPT" or "REJECT" for human-reviewed invoices
  - "Pending Review" for invoices awaiting decision
- **Audit Trail**: Complete history of decisions, reviewers, and timestamps

## Database Schema

### SQLite Database: `demo.db`

#### Table: `checkpoints`
Managed by LangGraph SqliteSaver for workflow state persistence.

#### Table: `human_review_queue`
```sql
CREATE TABLE human_review_queue (
    checkpoint_id TEXT PRIMARY KEY,
    invoice_id TEXT,
    vendor_name TEXT,
    amount REAL,
    created_at TEXT,
    reason_for_hold TEXT,
    decision TEXT,  -- 'ACCEPT', 'REJECT', or NULL (pending)
    reviewer_id TEXT,
    notes TEXT,
    updated_at TEXT,
    thread_id TEXT
);
```

## Configuration

### `workflow.json`
Main workflow configuration file defining:
- **Workflow stages**: 12 stages with modes, agents, instructions, tools
- **Match threshold**: Default 0.90 (90% match score required)
- **Tolerance percentage**: Default 5% (allowed variance in amounts)
- **Database path**: `sqlite:///./demo.db`
- **Tool pools**: Available tools for each capability

### Environment Variables (Future)
- `DB_CONN`: Database connection string
- `COMMON_KEY`: COMMON MCP server credentials
- `ATLAS_ERP_KEY`: ATLAS ERP credentials
- `NLP_KEY`: NLP service API key
- `QUEUE_KEY`: Queue service credentials
- `AUTH_KEY`: Authentication key
- `APP_URL`: Frontend application URL

## Features

### Bigtool Dynamic Tool Selection
Selects optimal tool implementation based on capability and context:

- **OCR**: `google_vision`, `tesseract`, `aws_textract`
- **Enrichment**: `clearbit`, `people_data_labs`, `vendor_db`
- **ERP Connector**: `sap_sandbox`, `netsuite`, `mock_erp`
- **Database**: `postgres`, `sqlite`, `dynamodb`
- **Email**: `sendgrid`, `smartlead`, `ses`
- **Storage**: `s3`, `gcs`, `local_fs`

### MCP Clients

#### COMMON Client (`src/mcp_clients/common_client.py`)
- `normalize_vendor(vendor_name)`: Normalize vendor name
- `compute_flags(vendor_profile, invoice)`: Compute risk flags
- `compute_match_score(invoice, po, tolerance)`: Two-way matching
- `build_accounting_entries(invoice, po)`: Generate accounting entries

#### ATLAS Client (`src/mcp_clients/atlas_client.py`)
- `ocr_extract(attachments, provider)`: Extract text from PDF/images
- `enrich_vendor(vendor_name, provider)`: Enrich vendor profile
- `fetch_po(po_ref)`: Fetch Purchase Order from ERP
- `fetch_grn(grn_ref)`: Fetch Goods Receipt Note
- `fetch_history(vendor_name)`: Fetch historical invoices
- `post_to_erp(entries)`: Post journal entries to ERP
- `schedule_payment(invoice_id, amount, due_date)`: Schedule payment
- `notify_vendor(invoice_id, status)`: Send vendor notification
- `notify_finance_team(invoice_id, status)`: Send internal notification

### Checkpointing & State Management
- **Persistent State**: Full workflow state saved to SQLite at each checkpoint
- **Resume Capability**: Resume from any checkpoint using `thread_id` and `checkpoint_id`
- **State Typing**: Strongly typed state using `TypedDict` models
- **State Updates**: Each node returns only modified state fields

### Structured Logging
Comprehensive logging for:
- Node entry/exit with timing
- Bigtool tool selections
- MCP client calls
- Checkpoint creation
- Human decisions
- Workflow resume events
- Errors and exceptions

## Testing

### Test Scripts

#### 1. Demo Run
```bash
python demo_run.py
```
Runs two scenarios:
- **Scenario 1**: Successful match (no HITL)
- **Scenario 2**: Failed match (triggers HITL checkpoint)

#### 2. End-to-End Tests
```bash
python test_end_to_end.py
```
Tests:
- API health check
- Invoice submission (success + HITL)
- Pending reviews retrieval
- Human decision submission
- Workflow completion

#### 3. Auto-Complete Test Scenarios
```bash
# Test 15 scenarios that should auto-complete without HITL
python3 test_auto_complete_scenarios.py
```
Tests various scenarios where invoices process automatically:
- Perfect matches
- Within tolerance variations (±5%)
- Description variations
- Vendor name normalization
- Quantity/price variations
- PDF and image attachments

### Test Data
Located in `test_data/`:
- `invoice_pass.json`: Successful match scenario (auto-completes)
- `invoice_fail.json`: HITL trigger scenario (match fails)
- `invoice_large.json`: Large amount invoice (>$10K)
- `invoice_missing.json`: Missing fields scenario
- `invoices_auto_complete.json`: 15 test cases for auto-complete scenarios
- `test_data/invoice_*.pdf`: Sample PDF invoices for OCR testing
- `invoice_*_image.png`: Sample PNG invoices for image OCR testing

### Manual Testing

#### Test File Upload
```bash
curl -X POST http://localhost:8000/workflow/run \
  -F "invoice=$(cat test_data/invoice_pass.json)" \
  -F "file_0=@test_data/test_data/invoice_001.pdf" \
  -F "file_count=1"
```

#### Test HITL Flow
1. Submit `invoice_fail.json` (match score will be low)
2. Workflow pauses at CHECKPOINT_HITL
3. Check pending reviews: `curl http://localhost:8000/human-review/pending`
4. Submit decision: `curl -X POST http://localhost:8000/human-review/decision -H "Content-Type: application/json" -d '{"checkpoint_id":"...","decision":"ACCEPT"}'`
5. Workflow resumes and completes

## Dependencies

### Backend (`requirements.txt`)
- **langgraph** >= 0.2.0 - Graph orchestration framework
- **langchain** >= 0.3.0 - LLM integration
- **langgraph-checkpoint-sqlite** >= 1.0.0 - SQLite checkpoint persistence
- **langchain-mcp-adapters** >= 0.1.0 - MCP client adapters
- **fastapi** >= 0.115.0 - Web API framework
- **uvicorn[standard]** >= 0.30.0 - ASGI server
- **python-multipart** >= 0.0.9 - File upload support
- **pydantic** >= 2.9.0 - Data validation
- **sqlalchemy** >= 2.0.36 - Database ORM
- **aiosqlite** >= 0.19.0 - Async SQLite
- **PyPDF2** >= 3.0.0 - PDF text extraction
- **pillow** >= 10.4.0 - Image processing
- **pytesseract** >= 0.3.13 - OCR (optional)
- **structlog** >= 24.4.0 - Structured logging
- **pytest** >= 8.3.0 - Testing framework

### Frontend (`frontend/package.json`)
- **react** ^18.2.0 - UI framework
- **react-router-dom** ^6.8.0 - Routing
- **axios** ^1.3.4 - HTTP client
- **vite** ^4.1.0 - Build tool

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'multipart'`
```bash
pip install python-multipart
```

**Issue**: `ValueError: Channel name 'checkpoint_id' is reserved`
- **Solution**: Already fixed - using `hitl_checkpoint_id` and `cp_id` instead

**Issue**: Database locked errors
```bash
# Stop all running processes, delete database, restart
rm demo.db demo.db-shm demo.db-wal
python -m src.api.app
```

**Issue**: Import errors
```bash
# Ensure you're in project root
cd /path/to/MCP_assignment
pip install -r requirements.txt
```

### Frontend Issues

**Issue**: Frontend not connecting to backend
- **Solution**: Ensure backend is running on port 8000
- Check `frontend/vite.config.js` proxy configuration
- Check browser console for CORS errors

**Issue**: File upload not working
- **Solution**: Ensure `python-multipart` is installed in backend
- Check browser console for errors
- Verify file size limits

### Workflow Issues

**Issue**: Workflow not pausing at HITL
- **Solution**: Check `match_score` in MATCH_TWO_WAY output
- Ensure `match_threshold` in `workflow.json` is correct (default: 0.90)
- Verify CHECKPOINT_HITL node is triggered

**Issue**: Workflow not resuming after decision
- **Solution**: Check `thread_id` and `checkpoint_id` are correct
- Verify human_review_repo has updated decision
- Check backend logs for errors

## 📝 Development Notes

### Adding New Stages
1. Create node file in `src/nodes/`
2. Define output model in `src/state/models.py`
3. Add node to graph in `src/graph/builder.py`
4. Add routing logic if conditional

### Extending MCP Clients
1. Add methods to `COMMONClient` or `ATLASClient`
2. Call from relevant nodes
3. Update mock implementations for testing

### Customizing Bigtool Selection
1. Edit `src/tools/bigtool_picker.py`
2. Add new capability pools
3. Implement selection logic

## 🎬 Demo Video Requirements

### Section 1: Introduction (1 minute)
- Your name and background
- Overview of Langie project
- Key features and technologies

### Section 2: Working Solution Demo (4 minutes)
1. **Frontend UI Walkthrough**
   - Show invoice submission form
   - Demonstrate file upload feature
   - Show human review interface
   - Display database preview

2. **Workflow Execution**
   - Submit invoice with file attachment
   - Show backend logs/stage progression
   - Demonstrate successful match scenario
   - Trigger HITL checkpoint scenario

3. **Human-In-The-Loop**
   - Show pending review in UI
   - Accept invoice decision
   - Show automatic workflow resume
   - Display final completed state

4. **Database & Audit Trail**
   - Show all workflows in database preview
   - Display detailed stage outputs
   - Show audit trail with reviewer information


## Additional Documentation

### Demo & Presentation
- **DEMO_GUIDE.md**: Complete demo guide with all scenarios
- **QUICK_DEMO.md**: Quick reference for presentations
- **DEMO_PRESENTATION.md**: Presentation-ready guide with talking points
- **EXPLANATION_SCRIPT.md**: Script for live presentations (~17 minutes)
- **VIDEO_SCRIPT.md**: Script for video recordings (~14 minutes)

### Testing
- **AUTO_COMPLETE_TEST_CASES.md**: Documentation for auto-complete test scenarios
- **test_auto_complete_scenarios.py**: Automated test script for auto-complete cases

### Quick Start
- **start_backend.sh**: Helper script to start backend with correct Python
- **demo.sh**: Automated demo launcher (starts both backend and frontend)
- **demo_workflow.py**: Automated demo scenarios with colored output

## Key Achievements

- ✅ **12-stage workflow** with deterministic and non-deterministic nodes
- ✅ **Persistent checkpoints** using LangGraph SqliteSaver
- ✅ **Human-In-The-Loop** with automatic resume after decision
- ✅ **File upload & OCR** processing for PDF/image invoices (Tesseract OCR)
- ✅ **Dynamic tool selection** via Bigtool pattern
- ✅ **MCP client integration** (COMMON & ATLAS)
- ✅ **Full-stack application** with React frontend and FastAPI backend
- ✅ **Comprehensive API** with 6 endpoints (including DELETE)
- ✅ **Complete workflow visibility** - see all invoices including auto-completed ones
- ✅ **Database preview** with sorting, filtering, and delete functionality
- ✅ **Auto-generated reviewer IDs** for better UX
- ✅ **Structured logging** for observability
- ✅ **End-to-end testing** scripts with 15+ auto-complete scenarios
- ✅ **Demo scripts** and comprehensive documentation
- ✅ **Auto-complete detection** - workflows that don't need human review are properly identified

## Recent Updates

### Version 2.0 Features
- **Complete Workflow Visibility**: `/workflow/all` now includes auto-completed workflows (previously only showed HITL workflows)
- **Delete Functionality**: Added DELETE endpoint and frontend delete button for workflow management
- **Sorting Capabilities**: Sort workflows by date, amount, vendor, invoice ID, or status
- **Improved Decision Display**: Better distinction between auto-completed and human-reviewed invoices
- **Auto-Complete Test Suite**: 15 comprehensive test cases for scenarios that don't require HITL
- **Enhanced Documentation**: Added demo guides, presentation scripts, and testing documentation



