# Complete End-to-End Test Guide

## Quick Start

### 1. Create Test Data
```bash
python test_data/create_all_test_data.py
```

This creates:
- 4 test invoice JSON files
- 4 PDF/text files for OCR testing
- All test data in `test_data/` directory

### 2. Start Backend Server
```bash
# Option 1: Direct Python
python -m src.api.app

# Option 2: Using script
./start_backend.sh

# Option 3: Background
python -m src.api.app > /tmp/langie_backend.log 2>&1 &
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 3. Start Frontend
```bash
cd frontend
npm install  # First time only
npm run dev
```

Frontend will be available at:
- UI: http://localhost:3000

### 4. Run Tests

#### Option A: Test via Script
```bash
python test_end_to_end.py
```

#### Option B: Test via Frontend UI
1. Open http://localhost:3000
2. Go to "Submit Invoice" tab
3. Fill in invoice form or use test data
4. Submit invoice
5. If HITL triggered, go to "Human Review" tab
6. Review and accept/reject invoice
7. Workflow continues automatically

#### Option C: Test via API directly
```bash
# Test successful match (no HITL)
curl -X POST http://localhost:8000/workflow/run \
  -H "Content-Type: application/json" \
  -d @test_data/invoice_pass.json

# Test failed match (triggers HITL)
curl -X POST http://localhost:8000/workflow/run \
  -H "Content-Type: application/json" \
  -d @test_data/invoice_fail.json

# Check pending reviews
curl http://localhost:8000/human-review/pending

# Submit human decision (replace CHECKPOINT_ID)
curl -X POST http://localhost:8000/human-review/decision \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint_id": "CHECKPOINT_ID",
    "decision": "ACCEPT",
    "reviewer_id": "reviewer_001",
    "notes": "Looks good"
  }'
```

## Test Scenarios

### Scenario 1: Successful Match (No HITL)
- File: `test_data/invoice_pass.json`
- Expected: Workflow completes without pausing
- Stages: INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH_TWO_WAY → RECONCILE → APPROVE → POSTING → NOTIFY → COMPLETE

### Scenario 2: Failed Match (HITL Triggered)
- File: `test_data/invoice_fail.json`
- Expected: Workflow pauses at CHECKPOINT_HITL
- Action Required: Human review and decision
- Stages: INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH_TWO_WAY → CHECKPOINT_HITL → [PAUSE] → HITL_DECISION → RECONCILE/COMPLETE

### Scenario 3: Large Amount (Requires Approval)
- File: `test_data/invoice_large.json`
- Expected: Requires approval (amount > $10,000)

### Scenario 4: Missing Data (Flags Computed)
- File: `test_data/invoice_missing.json`
- Expected: Flags computed for missing fields

## OCR Testing

The system uses PDF files for OCR extraction:
- `test_data/invoice_001.pdf` - Successful match invoice
- `test_data/invoice_002.pdf` - Failed match invoice
- `test_data/invoice_003.pdf` - Large amount invoice
- `test_data/invoice_004.pdf` - Missing data invoice

OCR extraction will:
1. Read PDF files (or text placeholders)
2. Extract text using selected OCR provider
3. Parse line items, dates, PO references
4. Pass extracted data to next stage

## Monitoring

### Backend Logs
```bash
# View logs
tail -f /tmp/langie_backend.log

# Or if running in terminal, logs appear directly
```

### Frontend Console
- Open browser DevTools (F12)
- Check Console tab for API calls and responses
- Check Network tab for API requests

### Database
```bash
# View SQLite database
sqlite3 demo.db

# Check human review queue
sqlite> SELECT * FROM human_review_queue;

# Check checkpoints
sqlite> SELECT checkpoint_id, invoice_id, decision FROM human_review_queue;
```

## Troubleshooting

### Backend won't start
1. Check if port 8000 is available: `lsof -i :8000`
2. Check logs: `cat /tmp/langie_backend.log`
3. Verify dependencies: `pip install -r requirements.txt`

### Frontend won't start
1. Install dependencies: `cd frontend && npm install`
2. Check if port 3000 is available: `lsof -i :3000`
3. Clear cache: `rm -rf frontend/node_modules frontend/.vite`

### API errors
1. Check backend is running: `curl http://localhost:8000/docs`
2. Verify request format matches API schema
3. Check API docs: http://localhost:8000/docs

### OCR not working
1. PDF files exist in `test_data/` directory
2. Files are readable (check permissions)
3. OCR uses mock implementation (real OCR needs MCP server)

## Expected Output

### Successful Workflow
```json
{
  "thread_id": "uuid-here",
  "status": "COMPLETED",
  "message": "Workflow completed successfully"
}
```

### HITL Triggered
```json
{
  "thread_id": "uuid-here",
  "status": "PAUSED",
  "checkpoint_id": "uuid-here",
  "review_url": "/human-review/uuid-here",
  "message": "Workflow paused for human review"
}
```

## Next Steps

After testing:
1. Review logs for stage-by-stage execution
2. Check Bigtool selections per stage
3. Verify checkpoint creation and resume
4. Confirm HITL decision routing
5. Validate final payload structure

Happy testing! 🚀

