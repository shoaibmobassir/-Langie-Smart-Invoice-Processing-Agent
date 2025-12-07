# Database Population Guide

This guide explains how to populate the database with sample data for demonstration.

## Quick Start

### Prerequisites

1. **Backend must be running**
   ```bash
   ./start_backend.sh
   # OR
   /Users/shoaibmobassir/miniconda3/bin/python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
   ```

2. **Wait for backend to initialize** (about 5 seconds)

### Populate Database

```bash
python3 populate_database.py
```

This script will:
- ✅ Clear existing database files
- ✅ Submit 5 test invoice scenarios
- ✅ Process workflows (auto-complete and HITL)
- ✅ Submit human decision for pending reviews
- ✅ Show summary of populated data

## What Gets Created

### Test Scenarios

1. **INV-SAMPLE-001** - Auto-complete (perfect match with PO)
   - Amount: $1000
   - Status: COMPLETED
   - Decision: None (No Review Needed)

2. **INV-SAMPLE-002** - Auto-complete (within tolerance)
   - Amount: $1005 (+$5, 0.5% difference)
   - Status: COMPLETED
   - Decision: None (No Review Needed)

3. **INV-SAMPLE-003** - HITL trigger (match fails)
   - Amount: $6000 (no matching PO)
   - Status: PAUSED → Will need human review
   - Decision: ACCEPT (if script processes it)

4. **INV-SAMPLE-004** - Auto-complete (within tolerance)
   - Amount: $995 (-$5, 0.5% difference)
   - Status: COMPLETED
   - Decision: None (No Review Needed)

5. **INV-SAMPLE-005** - HITL trigger (large amount)
   - Amount: $17,500 (no matching PO)
   - Status: PAUSED → Will need human review
   - Decision: Pending

## Expected Results

After running the script, you should see:

```
✅ Database populated with X workflows

Workflows by Status:
  - COMPLETED: 3-4
  - PAUSED: 1-2

Workflows by Decision:
  - ACCEPT: 1 (if script processed review)
  - REJECT: 0
  - None (Auto-completed): 3-4
```

## Verify in Frontend

1. **Start frontend** (if not already running):
   ```bash
   cd frontend && npm run dev
   ```

2. **Open Database Preview**:
   - Go to: http://localhost:5173
   - Click "Database Preview" tab
   - You should see all populated workflows

3. **Filter and Explore**:
   - Filter by "Completed" to see auto-completed invoices
   - Filter by "Pending" to see invoices awaiting review
   - Click "View Details" to see complete workflow stages

## Manual Population (Alternative)

If you want to add more data manually:

### Option 1: Use Frontend

1. Go to "Submit Invoice" tab
2. Fill in invoice details
3. Submit
4. Workflow will process automatically

### Option 2: Use API

```bash
# Submit invoice via API
curl -X POST http://localhost:8000/workflow/run \
  -F "invoice=$(cat test_data/invoice_pass.json)" \
  -F "file_count=0"
```

### Option 3: Use Test Scripts

```bash
# Run auto-complete test scenarios (15 test cases)
python3 test_auto_complete_scenarios.py

# Run end-to-end tests
python3 test_end_to_end.py
```

## Troubleshooting

### Backend Not Running
```
Error: Backend API is not running!
```
**Solution**: Start the backend first with `./start_backend.sh`

### No Workflows Created
```
Warning: No workflows found in database
```
**Solution**:
- Check backend logs: `tail -f /tmp/langie_backend.log`
- Verify database file exists: `ls -la demo.db`
- Try submitting one invoice manually via frontend

### Workflows Stuck in Processing
**Solution**:
- Wait longer (some workflows may take time)
- Check backend logs for errors
- Verify workflow configuration is correct

## Database Files

The script creates/modifies:
- `demo.db` - Main SQLite database
- `demo.db-shm` - Shared memory file (auto-created)
- `demo.db-wal` - Write-ahead log (auto-created)

These files contain:
- LangGraph checkpoints (workflow state)
- Human review queue entries
- All workflow state snapshots

## Re-populate Database

To start fresh:

1. **Stop backend**:
   ```bash
   pkill -f uvicorn
   ```

2. **Delete database**:
   ```bash
   rm demo.db demo.db-shm demo.db-wal
   ```

3. **Restart backend and populate**:
   ```bash
   ./start_backend.sh
   # Wait 5 seconds
   python3 populate_database.py
   ```

## Next Steps

After populating the database:

1. ✅ View workflows in Database Preview
2. ✅ Test filtering (Completed, Pending, Accepted, Rejected)
3. ✅ Test sorting (by date, amount, vendor, etc.)
4. ✅ Test delete functionality
5. ✅ Process pending human reviews
6. ✅ View detailed workflow stages

