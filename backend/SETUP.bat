@echo off
title Paper2Video - Complete Setup
color 0A
echo ========================================
echo   Paper2Video - Complete Setup
echo ========================================
echo.

echo Step 1: Checking Python version...
python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>nul
if errorlevel 1 (
    echo [WARNING] Python 3.9+ is recommended
    echo Current version may have compatibility issues
    echo.
    pause
)

echo.
echo Step 2: Creating .env file...
if not exist .env (
    call CREATE_ENV.bat
    echo.
    echo ⚠️ Please edit .env and add your GEMINI_API_KEY before continuing!
    echo.
    pause
) else (
    echo ✅ .env file exists
)

echo.
echo Step 3: Installing dependencies...
echo This may take 5-10 minutes...
echo.
call INSTALL_DEPENDENCIES.bat

if errorlevel 1 (
    echo.
    echo [ERROR] Setup incomplete!
    echo Please fix the errors above and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Make sure .env has your GEMINI_API_KEY
echo   2. Run: START_BACKEND.bat
echo.
pause

