@echo off
title Paper2Video Backend Server
color 0A
echo ========================================
echo   Paper2Video Backend API Server
echo ========================================
echo.

REM Check for .env file
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Run CREATE_ENV.bat to create it, or create manually.
    echo.
    echo Minimum required:
    echo   GEMINI_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

REM Check if GEMINI_API_KEY is set
findstr /C:"GEMINI_API_KEY=your_api_key_here" .env >nul 2>&1
if %errorlevel% == 0 (
    echo [WARNING] GEMINI_API_KEY is not configured!
    echo.
    echo Please edit .env file and add your API key.
    echo Get it from: https://makersuite.google.com/app/apikey
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b 1
)

REM Check if port 8000 is in use
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% == 0 (
    echo [WARNING] Port 8000 is already in use!
    echo.
    echo Another process might be using port 8000.
    echo Please stop it or change the port.
    echo.
    pause
    exit /b 1
)

echo Starting server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Try to activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start server!
    echo.
    echo Make sure:
    echo   1. Python is installed and in PATH
    echo   2. Dependencies are installed: pip install -r requirements.txt
    echo   3. You're in the backend directory
    echo.
    pause
)
