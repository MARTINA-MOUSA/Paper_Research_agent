@echo off
chcp 65001 >nul
title Paper2Video - إصلاح المشاكل
color 0A
echo ========================================
echo   إصلاح مشاكل Paper2Video
echo ========================================
echo.

echo المشكلة: الحزم المطلوبة غير مثبتة (moviepy وغيرها)
echo.
echo جارٍ تثبيت الحزم... هذا قد يستغرق بضع دقائق
echo.

REM Activate venv if exists
if exist venv\Scripts\activate.bat (
    echo تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
    echo.
)

echo ترقية pip...
python -m pip install --upgrade pip setuptools wheel
echo.

echo تثبيت الحزم المطلوبة...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [خطأ] فشل التثبيت!
    echo.
    echo جرب:
    echo   python -m pip install --upgrade pip
    echo   python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   تم التثبيت بنجاح!
echo ========================================
echo.
echo الآن قم بإنشاء ملف .env:
echo   1. شغّل: CREATE_ENV.bat
echo   2. عدّل .env وضع مفتاح Gemini API
echo   3. شغّل: START_BACKEND.bat
echo.
pause

