# Testing Summary - Langie Invoice Processing

## ✅ Completed Setup

1. **Test Data Created**
   - 4 test invoice JSON files
   - 4 PDF/text files for OCR
   - All in `test_data/` directory

2. **Backend API**
   - FastAPI server running on port 8000
   - Endpoints for workflow execution and HITL
   - Graph compilation successful (checkpoint_id renamed)

3. **Frontend**
   - React app ready in `frontend/` directory
   - Components for invoice submission and human review

## 📋 Test Data Files

- `test_data/invoice_pass.json` - Successful match scenario
- `test_data/invoice_fail.json` - HITL trigger scenario
- `test_data/invoice_large.json` - Large amount (>$10K)
- `test_data/invoice_missing.json` - Missing fields scenario
- `test_data/invoice_*.pdf` - OCR test files

## 🚀 Quick Start Commands

### Start Backend
```bash
python -m src.api.app
# Or background:
python -m src.api.app > /tmp/langie_backend.log 2>&1 &
```

### Start Frontend
```bash
cd frontend
npm install  # First time only
npm run dev
```

### Test API
```bash
# Test successful invoice
curl -X POST http://localhost:8000/workflow/run \
  -H "Content-Type: application/json" \
  -d @test_data/invoice_pass.json

# Check pending reviews
curl http://localhost:8000/human-review/pending
```

## 📊 What to Test

1. **Invoice Submission**
   - Submit invoice via frontend or API
   - Verify all 12 stages execute
   - Check logs for Bigtool selections

2. **HITL Workflow**
   - Submit invoice that fails matching
   - Verify checkpoint creation
   - Review via frontend or API
   - Accept/reject and verify resume

3. **OCR Processing**
   - Verify PDF files are read
   - Check extracted text in logs
   - Confirm parsed line items

4. **End-to-End Flow**
   - Complete workflow from INTAKE to COMPLETE
   - Verify state persistence
   - Check final payload structure

## 🔍 Monitoring

- **Backend Logs**: `/tmp/langie_backend.log` or console output
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: `demo.db` (SQLite)

## 📝 Notes

- All MCP clients are mocked for demo
- OCR reads PDFs/text files from `test_data/`
- Checkpoints stored in SQLite database
- Frontend proxy configured to backend on port 8000

## 🎯 Next Steps

1. Fix any remaining graph execution issues
2. Test full workflow end-to-end
3. Verify HITL checkpoint/resume
4. Test all 4 scenarios
5. Document any issues found

---

**Status**: Backend starts successfully ✅
**Remaining**: Graph execution needs minor fixes
**Ready for**: Manual testing via frontend UI

