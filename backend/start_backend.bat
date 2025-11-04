@echo off
echo ========================================
echo Starting Paper2Video Backend API
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env file with GEMINI_API_KEY
    echo.
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

