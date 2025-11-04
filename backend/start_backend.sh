#!/bin/bash
echo "========================================"
echo "Starting Paper2Video Backend API"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file with GEMINI_API_KEY"
    echo ""
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000

