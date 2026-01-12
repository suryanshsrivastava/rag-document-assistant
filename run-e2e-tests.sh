#!/bin/bash

set -e

echo "Starting RAG Document Assistant E2E Test Suite..."

cleanup() {
    echo "Cleaning up..."
    pkill -f "uvicorn app.main:app" || true
    pkill -f "next dev" || true
    echo "Servers stopped"
}

trap cleanup EXIT

echo "Starting backend server..."
cd backend
source ../.rag-document-assistant/bin/activate
uvicorn app.main:app --reload --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Starting frontend server..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Waiting for servers to start..."
sleep 10

echo "Checking backend health..."
curl -s http://localhost:8000/health | python -m json.tool

echo "Checking frontend..."
curl -s -I http://localhost:3000 | head -3

echo "Running E2E tests..."
cd frontend
npm run test:e2e

echo "All tests passed!"
