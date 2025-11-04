@echo off
echo ========================================
echo Paper2Video - Starting Backend and Frontend
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Checking backend...
cd backend

REM Check if .env exists
if not exist .env (
    echo.
    echo WARNING: .env file not found in backend folder!
    echo Please create .env file with:
    echo   GEMINI_API_KEY=your_api_key_here
    echo.
    pause
)

REM Check if backend is already running
python ..\check_backend.py >nul 2>&1
if %errorlevel% == 0 (
    echo Backend is already running!
    echo.
) else (
    echo Starting backend server...
    echo.
    start "Paper2Video Backend" cmd /k "cd /d %cd% && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo Waiting for backend to start...
    timeout /t 3 /nobreak >nul
    
    REM Check again
    python ..\check_backend.py
    if errorlevel 1 (
        echo.
        echo Failed to start backend. Please check the error messages above.
        pause
        exit /b 1
    )
)

cd ..
echo.
echo Step 2: Starting frontend...
cd frontend

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Streamlit app...
echo.
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C in this window to stop the frontend
echo (Backend will continue running in its own window)
echo.

streamlit run streamlit_app.py

