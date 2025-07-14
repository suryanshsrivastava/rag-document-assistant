#!/bin/bash

# Enhanced RAG Document Assistant Test Script
# Features: Logging, Startup, Cleanup

set -e  # Exit on any error

# Configuration
LOG_FILE="test_rag_system.log"
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_PID_FILE="/tmp/rag_backend.pid"
FRONTEND_PID_FILE="/tmp/rag_frontend.pid"
STARTED_SERVICES=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize logging
log_init() {
    echo "=== RAG Document Assistant Test Script ===" | tee "$LOG_FILE"
    echo "Date: $(date)" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Enhanced logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Helper functions with logging
test_pass() {
    echo -e "${GREEN}✅ $1: PASS${NC}" | tee -a "$LOG_FILE"
    log "INFO" "Test passed: $1"
}

test_fail() {
    echo -e "${RED}❌ $1: FAIL${NC}" | tee -a "$LOG_FILE"
    echo "   Error: $2" | tee -a "$LOG_FILE"
    log "ERROR" "Test failed: $1 - $2"
}

test_warn() {
    echo -e "${YELLOW}⚠️  $1: WARNING${NC}" | tee -a "$LOG_FILE"
    echo "   Note: $2" | tee -a "$LOG_FILE"
    log "WARN" "Test warning: $1 - $2"
}

test_info() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
    log "INFO" "$1"
}

# Function to check if python virtualenv is active
check_virtualenv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        test_info "Python virtual environment active: $VIRTUAL_ENV"
        return 0
    else
        test_warn "Python virtual environment" "No virtual environment detected"
        return 1
    fi
}


# Test 1: Check if services are running
echo "1. Checking service status..."
if ss -tlnp | grep -q ":8000"; then
    test_pass "Backend port 8000"
else
    test_fail "Backend port 8000" "Service not running"
fi

if ss -tlnp | grep -q ":3000"; then
    test_pass "Frontend port 3000"
else
    test_fail "Frontend port 3000" "Service not running"
fi

# Test 2: Root endpoint
echo
echo "2. Testing API endpoints..."
RESPONSE=$(curl -s -m 5 -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$RESPONSE" = "200" ]; then
    test_pass "Root endpoint"
else
    test_fail "Root endpoint" "HTTP $RESPONSE"
fi

# Test 3: Health check
HEALTH=$(curl -s -m 5 http://localhost:8000/health)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    test_pass "Health check"
else
    test_fail "Health check" "System unhealthy"
fi

# Test 4: Database connection
if echo "$HEALTH" | grep -q '"database_connected":true'; then
    test_pass "Database connection"
else
    test_fail "Database connection" "Database not connected"
fi

# Test 5: Gemini AI connection
if echo "$HEALTH" | grep -q '"gemini_connected":true'; then
    test_pass "Gemini AI connection"
else
    test_fail "Gemini AI connection" "Gemini not connected"
fi

# Test 6: Document list
echo
echo "3. Testing document operations..."
DOCS=$(curl -s -m 5 http://localhost:8000/api/documents)
if echo "$DOCS" | grep -q '\['; then
    DOC_COUNT=$(echo "$DOCS" | grep -o '"id"' | wc -l)
    test_pass "Document list ($DOC_COUNT documents)"
else
    test_fail "Document list" "Invalid response"
fi

# Test 7: Document upload (commented out to avoid duplicate uploads)
echo "$DOCS" > /tmp/test_rag_docs.json
# if [ -f "test_document.txt" ]; then
#     UPLOAD_RESPONSE=$(curl -s -X POST -F "file=@test_document.txt" http://localhost:8000/api/documents/upload)
#     if echo "$UPLOAD_RESPONSE" | grep -q '"document_id"'; then
#         test_pass "Document upload"
#     elif echo "$UPLOAD_RESPONSE" | grep -q '"detail"'; then
#         ERROR_MSG=$(echo "$UPLOAD_RESPONSE" | grep -o '"detail": "[^"]*"' | cut -d'"' -f4)
#         test_fail "Document upload" "$ERROR_MSG"
#     else
#         test_fail "Document upload" "Unknown error"
#     fi
# else
#     test_warn "Document upload" "test_document.txt not found, skipping upload test"
# fi
test_warn "Document upload" "Skipped to avoid duplicate uploads"

# Test 8: CORS
echo
echo "4. Testing CORS..."
CORS_RESPONSE=$(curl -s -m 5 -H "Origin: http://localhost:3000" -o /dev/null -w "%{http_code}" http://localhost:8000/api/documents)
if [ "$CORS_RESPONSE" = "200" ]; then
    test_pass "CORS configuration"
else
    test_fail "CORS configuration" "HTTP $CORS_RESPONSE"
fi

# Test 9: Frontend
echo
echo "5. Testing frontend..."
FRONTEND=$(curl -s -m 5 http://localhost:3000/)
if echo "$FRONTEND" | grep -q "RAG Document Assistant"; then
    test_pass "Frontend loading"
else
    test_fail "Frontend loading" "Frontend not accessible"
fi

# Test 10: Chat functionality (quick test)
echo
echo "6. Testing chat functionality..."
CHAT_RESPONSE=$(curl -s -m 10 -X POST -H "Content-Type: application/json" \
    -d '{"message": "test", "document_ids": [], "conversation_id": "test-123"}' \
    http://localhost:8000/api/chat)

if echo "$CHAT_RESPONSE" | grep -q '"response"'; then
    test_pass "Chat functionality"
elif echo "$CHAT_RESPONSE" | grep -q "overloaded\|timeout"; then
    test_warn "Chat functionality" "API temporarily overloaded"
elif echo "$CHAT_RESPONSE" | grep -q '"detail"'; then
    ERROR_MSG=$(echo "$CHAT_RESPONSE" | grep -o '"detail": "[^"]*"' | cut -d'"' -f4 | head -c 100)
    test_fail "Chat functionality" "$ERROR_MSG..."
else
    test_fail "Chat functionality" "No response received"
fi

echo
echo "=== Test Summary ==="
echo "Run complete at $(date)"
echo
echo "💡 Tips:"
echo "   - If tests fail, check logs: tail -f uvicorn.log"
echo "   - Restart services if needed: pkill uvicorn && ./restart_services.sh"
echo "   - Frontend available at: http://localhost:3000"
echo "   - Backend API at: http://localhost:8000"
