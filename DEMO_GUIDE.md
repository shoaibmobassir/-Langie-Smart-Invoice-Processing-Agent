# Langie - Complete Demo Guide

This guide provides step-by-step instructions for demonstrating the Langie Invoice Processing Agent.

## Quick Start

### Option 1: Automated Demo Script

```bash
# Start demo environment (backend + frontend)
./demo.sh

# In another terminal, run the demo scenarios
python3 demo_workflow.py
```

### Option 2: Manual Setup

```bash
# Terminal 1: Start backend
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run demo scenarios
python3 demo_workflow.py
```

## Demo Scenarios

### Scenario 1: Auto-Complete Workflow (No HITL)

**Purpose:** Demonstrate successful invoice processing without human intervention.

**Steps:**
1. Open frontend: http://localhost:5173
2. Navigate to "Submit Invoice"
3. Submit invoice with matching PO:
   ```json
   {
     "invoice_id": "INV-DEMO-001",
     "vendor_name": "Acme Corp",
     "amount": 1000,
     "currency": "USD",
     "line_items": [
       {"desc": "Widget A", "qty": 10, "unit_price": 50, "total": 500},
       {"desc": "Widget B", "qty": 5, "unit_price": 100, "total": 500}
     ]
   }
   ```
4. Click "Submit Invoice"
5. Observe workflow completes automatically through all stages

**Expected Result:**
- Workflow completes without pausing
- Status shows "COMPLETED" in Database Preview
- No entry in Human Review Queue

**Key Points:**
- Invoice amount ($1000) matches existing PO
- Match score passes threshold
- Workflow proceeds through all 12 stages automatically

---

### Scenario 2: HITL Triggered (Match Failed)

**Purpose:** Demonstrate workflow pausing for human review when match fails.

**Steps:**
1. Navigate to "Submit Invoice"
2. Submit invoice with non-matching amount:
   ```json
   {
     "invoice_id": "INV-DEMO-002",
     "vendor_name": "Beta Industries",
     "amount": 6000,
     "currency": "USD",
     "line_items": [
       {"desc": "Unknown Item", "qty": 100, "unit_price": 60, "total": 6000}
     ]
   }
   ```
3. Click "Submit Invoice"
4. Navigate to "Human Review" tab
5. Observe invoice appears in pending reviews

**Expected Result:**
- Workflow pauses at CHECKPOINT_HITL stage
- Status shows "PAUSED" 
- Invoice appears in Human Review Queue
- Reason shows "MATCH_FAILED_HITL"

**Key Points:**
- Invoice amount ($6000) doesn't match PO ($1000)
- Match score below threshold triggers HITL
- Workflow state persisted in SQLite checkpoint

---

### Scenario 3: Human Decision & Resume

**Purpose:** Demonstrate human review and workflow resumption.

**Steps:**
1. Navigate to "Human Review" tab
2. Click "Review" button on a pending invoice
3. Review invoice details (vendor, amount, line items, match evidence)
4. Select decision:
   - **ACCEPT**: Workflow continues to RECONCILE stage
   - **REJECT**: Workflow completes with rejection
5. Add optional notes
6. Click "Submit Decision"
7. Observe workflow automatically resumes

**Expected Result:**
- Decision saved to database
- Workflow state updated with human decision
- Workflow automatically continues to next stage
- Invoice moves from "Pending" to "Accepted" or "Rejected" in Database Preview

**Key Points:**
- Reviewer ID auto-generated if not provided
- Workflow resumes automatically after ACCEPT
- State persisted across pause/resume
- Complete audit trail maintained

---

### Scenario 4: Database Preview

**Purpose:** Demonstrate comprehensive view of all processed invoices.

**Steps:**
1. Navigate to "Database Preview" tab
2. View all invoices in the system
3. Filter by status:
   - **All**: All invoices
   - **Pending**: Workflows waiting for review
   - **Accepted**: Human-accepted workflows
   - **Rejected**: Human-rejected workflows
   - **Completed**: All completed workflows
4. Click "View Details" on any invoice
5. Review complete workflow details:
   - All stage outputs
   - HITL decisions
   - Timestamps
   - Full invoice payload

**Expected Result:**
- See all processed invoices
- Filter accurately reflects workflow status
- Complete audit trail for each invoice
- Detailed stage-by-stage information

**Key Points:**
- Source of truth: LangGraph state (not just database)
- Decision read from workflow state
- Complete visibility into workflow execution

---

### Scenario 5: File Upload & OCR

**Purpose:** Demonstrate invoice processing with PDF/image attachments.

**Steps:**
1. Navigate to "Submit Invoice"
2. Fill in invoice details
3. Click "Choose Files" under Attachments
4. Select PDF or image file (PNG, JPG, etc.)
5. Submit invoice
6. Workflow processes attachment through OCR

**Expected Result:**
- File uploaded and saved to `test_data/uploaded/`
- OCR extracts text from PDF/image
- Extracted text used in UNDERSTAND stage
- Complete workflow proceeds with OCR data

**Key Points:**
- Supports PDF (PyPDF2) and images (Tesseract OCR)
- Files persisted for audit trail
- OCR text integrated into workflow

---

## Execution Logs

### Backend Logs

View backend execution logs:
```bash
tail -f /tmp/langie_backend.log
```

Or if running manually:
```bash
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --log-level info
```

**Key Log Events:**
- Node entry/exit
- Bigtool tool selection
- MCP client calls
- Checkpoint creation
- Human decisions
- Workflow resume

### Frontend Logs

View frontend logs:
```bash
tail -f /tmp/langie_frontend.log
```

Or check browser console for client-side logs.

### Structured Logging

Backend uses structured logging with `structlog`. Logs include:
- Timestamps
- Stage names
- Thread IDs
- Checkpoint IDs
- Decision details

---

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Submit Invoice
```bash
curl -X POST http://localhost:8000/workflow/run \
  -F "invoice=@test_data/invoice_fail.json" \
  -F "file_count=0"
```

### Get Pending Reviews
```bash
curl http://localhost:8000/human-review/pending
```

### Submit Decision
```bash
curl -X POST http://localhost:8000/human-review/decision \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint_id": "xxx",
    "decision": "ACCEPT",
    "reviewer_id": "reviewer_001",
    "notes": "Approved after review"
  }'
```

### Get All Workflows
```bash
curl http://localhost:8000/workflow/all
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

---

## Architecture Highlights

### 12 Workflow Stages
1. **INTAKE**: Validate and ingest invoice
2. **UNDERSTAND**: OCR extraction and NLP parsing
3. **PREPARE**: Vendor normalization and enrichment
4. **RETRIEVE**: Fetch PO, GRN, and history
5. **MATCH_TWO_WAY**: Match invoice to PO
6. **CHECKPOINT_HITL**: Pause for human review (if match fails)
7. **HITL_DECISION**: Process human decision
8. **RECONCILE**: Generate accounting entries
9. **APPROVE**: Approval workflow
10. **POSTING**: Post to ERP system
11. **NOTIFY**: Notify vendor and finance team
12. **COMPLETE**: Finalize workflow

### Key Features Demonstrated

1. **LangGraph Orchestration**
   - State machine workflow
   - Conditional routing
   - Checkpoint persistence

2. **Human-In-The-Loop (HITL)**
   - Automatic pause on match failure
   - Human review interface
   - Automatic resume after decision

3. **Dynamic Tool Selection (Bigtool)**
   - Tool selection based on capability
   - OCR provider selection
   - ERP integration selection

4. **MCP Client Integration**
   - COMMON server (vendor normalization, matching)
   - ATLAS server (OCR, enrichment, ERP)

5. **State Management**
   - Single global state object
   - Typed state models (TypedDict)
   - SQLite checkpoint persistence

6. **Frontend-Backend Integration**
   - React frontend
   - FastAPI backend
   - Real-time status updates

---

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is available
- Verify Python dependencies: `pip install -r requirements.txt`
- Check database file: `demo.db` should exist

### Frontend Not Loading
- Check if port 5173 is available
- Install frontend dependencies: `cd frontend && npm install`
- Check API proxy configuration in `vite.config.js`

### Workflows Not Pausing
- Verify match logic in `MATCH_TWO_WAY` stage
- Check checkpoint creation logs
- Verify SQLite database is writable

### Decisions Not Resuming Workflow
- Check human decision endpoint logs
- Verify workflow state is being updated
- Check resume token format

---

## Demo Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Database file exists and is writable
- [ ] Test data files available
- [ ] OCR libraries installed (for image processing)
- [ ] All API endpoints responding
- [ ] Frontend can connect to backend

---

## Additional Resources

- **README.md**: Complete project documentation
- **workflow.json**: Workflow configuration
- **test_end_to_end.py**: Automated test scenarios
- **demo_workflow.py**: Automated demo script

---

## Questions & Support

For issues or questions:
1. Check logs in `/tmp/langie_backend.log` and `/tmp/langie_frontend.log`
2. Review API docs at http://localhost:8000/docs
3. Check README.md for detailed architecture
4. Review workflow.json for stage configuration

