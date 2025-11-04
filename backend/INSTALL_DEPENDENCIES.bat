@echo off
title Paper2Video - Install Dependencies
color 0B
echo ========================================
echo   Paper2Video - Installing Dependencies
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
) else (
    echo [INFO] No virtual environment found, installing globally...
    echo.
)

echo Installing required packages...
echo This may take a few minutes...
echo.

pip install --upgrade pip setuptools wheel
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Common issues:
    echo   1. Python version too old (need 3.10+ recommended)
    echo   2. Missing build tools (Visual C++ Build Tools for Windows)
    echo   3. Network connectivity issues
    echo.
    echo Try:
    echo   python -m pip install --upgrade pip
    echo   python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Create .env file with GEMINI_API_KEY
echo   2. Run: START_BACKEND.bat
echo.
pause

