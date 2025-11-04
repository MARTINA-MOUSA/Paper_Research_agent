@echo off
title Paper2Video - Create .env File
color 0E
echo ========================================
echo   Paper2Video - Environment Setup
echo ========================================
echo.

if exist .env (
    echo [WARNING] .env file already exists!
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto :end
    echo.
)

echo Creating .env file...
echo.

(
echo # Gemini API Key - REQUIRED
echo # Get your API key from: https://makersuite.google.com/app/apikey
echo GEMINI_API_KEY=your_api_key_here
echo.
echo # Database
echo DATABASE_URL=sqlite:///./app.db
echo.
echo # Server Configuration
echo HOST=0.0.0.0
echo PORT=8000
echo WORKERS=4
echo.
echo # CORS Origins (comma-separated)
echo CORS_ORIGINS=*
echo.
echo # File Handling
echo MAX_FILE_SIZE=10485760
echo UPLOAD_DIR=uploads
echo OUTPUT_DIR=outputs
echo.
echo # Processing Limits
echo MAX_TEXT_LENGTH=50000
echo MAX_SECTIONS=20
echo.
echo # Gemini Model
echo GEMINI_MODEL=gemini-1.5-flash
echo.
echo # Logging
echo LOG_LEVEL=INFO
) > .env

echo ✅ .env file created!
echo.
echo ⚠️ IMPORTANT: Edit .env and add your GEMINI_API_KEY
echo.
echo You can:
echo   1. Open .env in notepad: notepad .env
echo   2. Or edit it manually
echo.
echo Get your API key from:
echo   https://makersuite.google.com/app/apikey
echo.
pause

:end

