#!/bin/bash
# Demo script for Langie - Invoice Processing LangGraph Agent
# This script runs a complete end-to-end demonstration

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  Langie - Invoice Processing LangGraph Agent"
echo "  Complete End-to-End Demo"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠️  Warning: No virtual environment detected${NC}"
    echo "Consider activating a virtual environment for isolated dependencies"
    echo ""
fi

# Step 1: Check dependencies
echo -e "${BLUE}📦 Step 1: Checking dependencies...${NC}"
python3 --version
echo ""

# Step 2: Start backend server
echo -e "${BLUE}🚀 Step 2: Starting backend server...${NC}"
echo "Backend will run on: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "Starting backend in background..."
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --log-level info > /tmp/langie_backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo ""

# Wait for backend to start
echo "Waiting for backend to be ready..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting...${NC}"
    sleep 3
fi
echo ""

# Step 3: Start frontend server
echo -e "${BLUE}🎨 Step 3: Starting frontend server...${NC}"
echo "Frontend will run on: http://localhost:5173"
echo ""
echo "Starting frontend in background..."
cd frontend
npm run dev > /tmp/langie_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"
echo ""

# Wait for frontend to start
echo "Waiting for frontend to be ready..."
sleep 5
echo ""

# Step 4: Show demo information
echo -e "${BLUE}📋 Step 4: Demo Information${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ACCESS POINTS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  🌐 Frontend UI:     http://localhost:5173"
echo "  🔌 Backend API:     http://localhost:8000"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo "  🏥 Health Check:    http://localhost:8000/health"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  DEMO SCENARIOS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  1. Submit Invoice (Auto-Complete)"
echo "     - Go to: http://localhost:5173"
echo "     - Click 'Submit Invoice'"
echo "     - Use test data that matches PO (will auto-complete)"
echo ""
echo "  2. Submit Invoice (Triggers HITL)"
echo "     - Submit invoice with amount that doesn't match PO"
echo "     - Workflow will pause at CHECKPOINT_HITL"
echo "     - Go to 'Human Review' tab to see pending reviews"
echo ""
echo "  3. Human Review & Resume"
echo "     - Click 'Review' on a pending invoice"
echo "     - Select ACCEPT or REJECT"
echo "     - Workflow will automatically resume"
echo ""
echo "  4. Database Preview"
echo "     - Click 'Database Preview' tab"
echo "     - View all invoices, filter by status"
echo "     - See complete workflow details"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  LOG FILES:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Backend logs:  /tmp/langie_backend.log"
echo "  Frontend logs: /tmp/langie_frontend.log"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  TO STOP SERVERS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Run: ./stop_demo.sh"
echo "  Or manually: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${GREEN}✅ Demo environment is ready!${NC}"
echo ""
echo "Press Ctrl+C to stop and clean up..."
echo ""

# Keep script running and trap signals
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for user to stop
wait

