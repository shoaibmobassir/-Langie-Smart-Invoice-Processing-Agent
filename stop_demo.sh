#!/bin/bash
# Stop demo servers

echo "Stopping Langie demo servers..."

# Kill backend
pkill -f "uvicorn src.api.app:app" 2>/dev/null && echo "✅ Backend stopped" || echo "⚠️  Backend was not running"

# Kill frontend
pkill -f "vite" 2>/dev/null && echo "✅ Frontend stopped" || echo "⚠️  Frontend was not running"

echo "Done!"

