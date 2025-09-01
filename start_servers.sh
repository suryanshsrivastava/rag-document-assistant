#!/bin/bash

# Weekend RAG System - Server Startup Script

echo "🚀 Starting Weekend RAG System..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping servers..."
    pkill -f "uvicorn"
    pkill -f "next dev"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📡 Starting FastAPI backend..."
source venv/bin/activate
cd backend
python mvp_main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting Next.js frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started successfully!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
