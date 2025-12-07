#!/bin/bash
# Start frontend server

cd "$(dirname "$0")/frontend"
echo "🚀 Starting Langie Frontend..."
echo "📍 Frontend will be available at http://localhost:3000"
echo ""
npm run dev

