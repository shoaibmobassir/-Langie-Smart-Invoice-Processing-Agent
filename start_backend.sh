#!/bin/bash
# Start backend server with correct Python

cd /Users/shoaibmobassir/Desktop/MCP_assignment

# Use miniconda Python
PYTHON="/Users/shoaibmobassir/miniconda3/bin/python"

# Check if Python exists
if [ ! -f "$PYTHON" ]; then
    echo "Error: Python not found at $PYTHON"
    echo "Trying system Python..."
    PYTHON="python3"
fi

# Stop any existing backend
pkill -f "uvicorn src.api.app" 2>/dev/null

echo "Starting backend server..."
echo "Using: $PYTHON"
echo "Backend will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Logs: /tmp/langie_backend.log"
echo ""

# Start backend in background
$PYTHON -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 > /tmp/langie_backend.log 2>&1 &

echo "Backend started! PID: $!"
echo ""
echo "To view logs: tail -f /tmp/langie_backend.log"
echo "To stop: pkill -f 'uvicorn src.api.app'"
