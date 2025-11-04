@echo off
chcp 65001 >nul
title Paper2Video - فحص الإعداد
color 0B
echo ========================================
echo   فحص إعداد Paper2Video
echo ========================================
echo.

REM Check directory
if not exist requirements.txt (
    echo [خطأ] يجب تشغيل هذا من مجلد backend!
    echo Current: %CD%
    pause
    exit /b 1
)

echo ✅ المجلد صحيح: %CD%
echo.

REM Check .env file
echo فحص ملف .env...
if not exist .env (
    echo ❌ ملف .env غير موجود!
    echo.
    echo شغّل: CREATE_ENV.bat
    echo.
) else (
    echo ✅ ملف .env موجود
    echo.
    echo فحص GEMINI_API_KEY...
    findstr /C:"GEMINI_API_KEY=" .env | findstr /V /C:"your_api_key_here" >nul 2>&1
    if errorlevel 1 (
        echo ❌ GEMINI_API_KEY غير مضبوط!
        echo   افتح .env وضع مفتاحك
    ) else (
        echo ✅ GEMINI_API_KEY مضبوط
    )
)
echo.

REM Check Python packages
echo فحص الحزم المثبتة...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ❌ fastapi غير مثبت
) else (
    echo ✅ fastapi مثبت
)

python -c "import moviepy" 2>nul
if errorlevel 1 (
    echo ❌ moviepy غير مثبت - شغّل: INSTALL_DEPENDENCIES.bat
) else (
    echo ✅ moviepy مثبت
)

python -c "import google.generativeai" 2>nul
if errorlevel 1 (
    echo ❌ google-generativeai غير مثبت
) else (
    echo ✅ google-generativeai مثبت
)

echo.
echo ========================================
echo.

REM Test .env loading
echo اختبار قراءة .env...
python test_env.py

echo.
pause

