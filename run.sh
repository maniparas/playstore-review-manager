#!/usr/bin/env bash
# Quick start script for Google Play Reviews Explorer

set -e

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials!"
fi

echo "Starting FastAPI server..."
echo "Visit http://127.0.0.1:8000 in your browser"
echo ""
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

