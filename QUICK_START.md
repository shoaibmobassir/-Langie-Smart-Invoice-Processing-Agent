# 🚀 Quick Start Guide - Langie Invoice Processing

## ✅ Status

- ✅ **Backend**: Running on http://localhost:8000
- ✅ **Frontend**: Running on http://localhost:3000  
- ✅ **Test Data**: Created in `test_data/` directory
- ✅ **PDFs**: OCR test files ready

## 🎯 Test Now!

### Option 1: Frontend UI (Recommended)

1. **Open Browser**: http://localhost:3000
2. **Submit Invoice**:
   - Click "Submit Invoice" tab
   - Fill in the form or use test data
   - Click "Submit Invoice"
3. **Review** (if HITL triggered):
   - Click "Human Review" tab
   - Review pending invoices
   - Accept or Reject
   - Workflow continues automatically

### Option 2: API Direct

```bash
# Submit invoice
curl -X POST http://localhost:8000/workflow/run \
  -H "Content-Type: application/json" \
  -d @test_data/invoice_pass.json

# Check pending reviews
curl http://localhost:8000/human-review/pending
```

### Option 3: Test Script

```bash
python test_end_to_end.py
```

## 📁 Test Data Files

All in `test_data/` directory:

1. **invoice_pass.json** - Successful match (no HITL)
2. **invoice_fail.json** - Failed match (triggers HITL)
3. **invoice_large.json** - Large amount (>$10K)
4. **invoice_missing.json** - Missing fields
5. **invoice_*.pdf** - OCR test files

## 🔍 Monitor Execution

### Backend Logs
```bash
tail -f /tmp/langie_backend.log
```

### API Documentation
Open: http://localhost:8000/docs

### Database
```bash
sqlite3 demo.db
> SELECT * FROM human_review_queue;
```

## 📊 Expected Workflow

1. **INTAKE** - Validates and persists invoice
2. **UNDERSTAND** - OCR extraction from PDFs
3. **PREPARE** - Vendor normalization and enrichment
4. **RETRIEVE** - Fetch POs from ERP
5. **MATCH_TWO_WAY** - Compute match score
6. **CHECKPOINT_HITL** - Pause if match fails
7. **HITL_DECISION** - Human review
8. **RECONCILE** - Build accounting entries
9. **APPROVE** - Approval policy
10. **POSTING** - Post to ERP
11. **NOTIFY** - Send notifications
12. **COMPLETE** - Final payload

## 🎬 Demo Scenarios

### Scenario 1: Happy Path
- Use `invoice_pass.json`
- Workflow completes without pause
- All stages execute successfully

### Scenario 2: HITL Flow
- Use `invoice_fail.json`
- Workflow pauses at CHECKPOINT_HITL
- Review via frontend or API
- Accept → continues to RECONCILE
- Reject → finalizes with MANUAL_HANDOFF

## 🛠️ Troubleshooting

**Backend not running?**
```bash
python -m src.api.app
```

**Frontend not running?**
```bash
cd frontend && npm run dev
```

**Check services:**
```bash
curl http://localhost:8000/docs  # Backend
curl http://localhost:3000        # Frontend
```

## 📝 Notes

- OCR reads PDFs from `test_data/` directory
- All MCP clients are mocked for demo
- Checkpoints stored in `demo.db`
- Logs show Bigtool selections and stage execution

---

**Ready to test!** 🎉

Visit http://localhost:3000 to start!

