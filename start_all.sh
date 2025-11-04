#!/bin/bash
echo "========================================"
echo "Paper2Video - Starting Backend and Frontend"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi

echo "Step 1: Checking backend..."
cd backend

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "WARNING: .env file not found in backend folder!"
    echo "Please create .env file with:"
    echo "  GEMINI_API_KEY=your_api_key_here"
    echo ""
fi

# Check if backend is already running
if python3 ../check_backend.py > /dev/null 2>&1; then
    echo "Backend is already running!"
    echo ""
else
    echo "Starting backend server..."
    echo ""
    # Start backend in background
    cd ..
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    echo "Waiting for backend to start..."
    sleep 3
    
    # Check again
    cd ..
    if ! python3 check_backend.py; then
        echo ""
        echo "Failed to start backend. Please check backend.log"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
fi

cd ..
echo ""
echo "Step 2: Starting frontend..."
cd frontend

# Check if Streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "ERROR: Streamlit is not installed!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

echo "Starting Streamlit app..."
echo ""
echo "========================================"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py

