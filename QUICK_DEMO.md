# Quick Demo Guide - Langie

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start everything
./demo.sh

# 2. In another terminal, run automated demo
python3 demo_workflow.py

# 3. Open browser
open http://localhost:5173
```

## 📋 Demo Flow (5 minutes)

### Step 1: Submit Auto-Complete Invoice
- **URL:** http://localhost:5173
- **Action:** Submit Invoice tab → Use this JSON:
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
- **Result:** ✅ Workflow completes automatically (no HITL)

### Step 2: Submit HITL Invoice
- **Action:** Submit Invoice tab → Use this JSON:
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
- **Result:** ⏸️ Workflow pauses at HITL checkpoint

### Step 3: Human Review
- **Action:** Human Review tab → Click "Review" → Select "ACCEPT" → Submit
- **Result:** ✅ Workflow resumes and completes

### Step 4: View Results
- **Action:** Database Preview tab → Filter by "Completed" or "Accepted"
- **Result:** 📊 See all processed invoices with full details

## 🎯 Key Features to Highlight

1. **12-Stage Workflow** - See all stages in Database Preview
2. **HITL Checkpoint** - Workflow pauses automatically when match fails
3. **Auto-Resume** - Workflow continues after human decision
4. **File Upload** - Upload PDF/image, OCR extracts text automatically
5. **State Persistence** - Workflow state saved in SQLite checkpoints
6. **Audit Trail** - Complete history in Database Preview

## 📊 What to Show

### Frontend UI
- ✅ Submit Invoice form (with file upload)
- ✅ Human Review queue (pending reviews)
- ✅ Database Preview (all workflows, filters, details)

### Backend Logs
```bash
tail -f /tmp/langie_backend.log
```
- Node entry/exit
- Bigtool selections
- MCP client calls
- Checkpoint creation
- Human decisions

### API Endpoints
- `/workflow/run` - Submit invoice
- `/human-review/pending` - Get pending reviews
- `/human-review/decision` - Submit decision
- `/workflow/all` - Get all workflows

## 🔍 Verification Points

1. ✅ Invoice submitted → Thread ID returned
2. ✅ HITL triggered → Status = "PAUSED"
3. ✅ Human decision → Decision saved to state
4. ✅ Workflow resumed → Status = "COMPLETED"
5. ✅ Database preview → Shows all workflows correctly

## 📝 Demo Script

```
Welcome to Langie Demo!

1. Show Frontend UI (http://localhost:5173)
   - Three tabs: Submit Invoice, Human Review, Database Preview

2. Submit Auto-Complete Invoice
   - Fill form with matching PO invoice
   - Submit → See automatic completion
   - Check Database Preview → Status: COMPLETED

3. Submit HITL Invoice
   - Fill form with non-matching invoice
   - Submit → Check Human Review tab
   - See invoice in pending queue

4. Process Human Review
   - Click Review → See invoice details
   - Select ACCEPT → Submit
   - Watch workflow resume automatically
   - Check Database Preview → Status: COMPLETED, Decision: ACCEPT

5. Show Database Preview
   - Filter by status (Pending, Accepted, Completed)
   - Click View Details on any invoice
   - Show complete workflow stages
   - Show audit trail

6. Show Backend Logs
   - Node execution
   - Checkpoint creation
   - State updates

7. Show API Documentation
   - http://localhost:8000/docs
   - Interactive API explorer
```

## 🛑 Stop Demo

```bash
./stop_demo.sh
```

Or manually:
```bash
pkill -f "uvicorn"
pkill -f "vite"
```

