#!/bin/bash
# Complete end-to-end test script

echo "🧾 Langie - Complete End-to-End Test"
echo "===================================="
echo ""

# Step 1: Create test data
echo "📁 Step 1: Creating test data..."
python test_data/create_all_test_data.py
echo ""

# Step 2: Start backend
echo "🚀 Step 2: Starting backend server..."
cd "$(dirname "$0")"
python -m src.api.app > /tmp/langie_backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

# Check if backend started
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start. Check /tmp/langie_backend.log"
    cat /tmp/langie_backend.log | tail -20
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Step 3: Test API
echo ""
echo "🧪 Step 3: Testing API..."
python test_api.py

# Step 4: Start frontend (optional)
echo ""
echo "🌐 Step 4: Frontend available at http://localhost:3000"
echo "   To start frontend: cd frontend && npm run dev"
echo ""

# Keep backend running
echo "✅ Backend is running. Press Ctrl+C to stop."
echo "   Backend logs: tail -f /tmp/langie_backend.log"
echo "   API docs: http://localhost:8000/docs"
echo ""

wait $BACKEND_PID

