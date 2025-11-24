#!/usr/bin/env bash
# Test script to demonstrate logging functionality

set -e

cd "$(dirname "$0")"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    LOGGING FUNCTIONALITY TEST                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  1. Start the FastAPI server in the background"
echo "  2. Make test API calls"
echo "  3. Show the logged output"
echo "  4. Stop the server"
echo ""
echo "Press Ctrl+C to stop at any time"
echo ""

# Start server in background
echo "Starting server..."
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!
echo "  ✓ Server started (PID: $SERVER_PID)"
echo "  ✓ Logs being written to server.log"
echo ""

# Wait for server to start
echo "Waiting for server to be ready..."
sleep 3

# Test 1: List reviews
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Fetching list of reviews"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Request: GET /api/reviews?package_name=com.example.app&page_size=50"
echo ""

curl -s "http://127.0.0.1:8000/api/reviews?package_name=com.example.app&page_size=50" > /dev/null

sleep 1

echo "📋 Server Logs:"
echo "─────────────────────────────────────────────────────────────────────────────"
tail -30 server.log | grep -A 20 "INCOMING HTTP REQUEST" | head -25 || echo "  (See server.log for full output)"
echo ""

# Test 2: Get single review
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Fetching single review"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Request: GET /api/reviews/mock-review-1"
echo ""

curl -s "http://127.0.0.1:8000/api/reviews/mock-review-1?package_name=com.example.app" > /dev/null

sleep 1

echo "📋 Server Logs:"
echo "─────────────────────────────────────────────────────────────────────────────"
tail -25 server.log | grep -A 15 "get_review" | head -20 || echo "  (See server.log for full output)"
echo ""

# Cleanup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null || true
echo "  ✓ Server stopped"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                          TEST COMPLETED                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Full logs saved to: server.log"
echo ""
echo "To view complete logs:"
echo "  cat server.log"
echo ""
echo "To view only specific log types:"
echo "  grep '🌍' server.log    # HTTP requests from clients"
echo "  grep '📥' server.log    # Service method calls"
echo "  grep '🌐' server.log    # Outgoing Google API requests"
echo "  grep '📦' server.log    # Google API responses"
echo "  grep '📤' server.log    # HTTP responses to clients"
echo ""

