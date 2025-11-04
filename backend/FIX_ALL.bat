@echo off
chcp 65001 >nul
title Paper2Video - إصلاح جميع المشاكل
color 0A
echo ========================================
echo   إصلاح جميع مشاكل Paper2Video
echo ========================================
echo.

REM Check if we're in backend directory
if not exist requirements.txt (
    echo [خطأ] يجب تشغيل هذا السكريبت من مجلد backend!
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo الخطوة 1: التحقق من البيئة الافتراضية...
if exist venv\Scripts\activate.bat (
    echo تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
    echo ✅ تم تفعيل البيئة الافتراضية
) else (
    echo ⚠️ لم يتم العثور على بيئة افتراضية
    echo.
    choice /C YN /M "هل تريد إنشاء بيئة افتراضية جديدة"
    if errorlevel 2 (
        echo تثبيت في النظام العام...
    ) else (
        python -m venv venv
        call venv\Scripts\activate.bat
        echo ✅ تم إنشاء وتفعيل البيئة الافتراضية
    )
)
echo.

echo الخطوة 2: تثبيت الحزم المطلوبة...
echo هذا قد يستغرق 5-10 دقائق...
echo.
python -m pip install --upgrade pip setuptools wheel
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [خطأ] فشل تثبيت الحزم!
    echo.
    echo جرب:
    echo   python -m pip install --upgrade pip
    echo   python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ تم تثبيت الحزم بنجاح!
echo.

echo الخطوة 3: التحقق من ملف .env...
if not exist .env (
    echo ملف .env غير موجود!
    echo.
    echo جارٍ إنشاء ملف .env...
    call CREATE_ENV.bat
    echo.
    echo ⚠️ مهم: عدّل ملف .env وضع مفتاح Gemini API
    echo.
) else (
    echo ✅ ملف .env موجود
    echo.
    echo التحقق من GEMINI_API_KEY...
    findstr /C:"GEMINI_API_KEY=" .env | findstr /V /C:"your_api_key_here" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ GEMINI_API_KEY غير مضبوط!
        echo.
        echo افتح .env وعدّل:
        echo   GEMINI_API_KEY=your_actual_api_key
        echo.
    ) else (
        echo ✅ GEMINI_API_KEY مضبوط
    )
)

echo.
echo ========================================
echo   تم الإصلاح!
echo ========================================
echo.
echo الخطوات التالية:
echo   1. افتح .env وضع مفتاح Gemini API
echo   2. شغّل: START_BACKEND.bat
echo.
pause

