# حل المشاكل - Solution in Arabic

## المشكلة الحالية

```
ModuleNotFoundError: No module named 'moviepy.editor'
```

**السبب:** الحزم المطلوبة غير مثبتة في البيئة الافتراضية (venv)

## الحل السريع

### الطريقة 1: استخدام السكريبت (موصى به)

```bash
cd backend
FIX_ARABIC.bat
```

### الطريقة 2: التثبيت اليدوي

1. **افتح Terminal في مجلد backend:**
   ```bash
   cd C:\Users\DELL\Desktop\paper2video\backend
   ```

2. **فعّل البيئة الافتراضية:**
   ```bash
   venv\Scripts\activate
   ```

3. **ثبّت الحزم:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **انتظر حتى ينتهي التثبيت** (قد يستغرق 5-10 دقائق)

## بعد التثبيت

### 1. إنشاء ملف .env

```bash
cd backend
CREATE_ENV.bat
```

ثم افتح `.env` وضع مفتاح Gemini API:
```
GEMINI_API_KEY=your_actual_api_key_here
```

احصل على المفتاح من: https://makersuite.google.com/app/apikey

### 2. تشغيل السيرفر

```bash
START_BACKEND.bat
```

## ملاحظات مهمة

- ✅ تأكد أنك في مجلد `backend`
- ✅ تأكد أن البيئة الافتراضية (venv) مفعلة
- ✅ قد يستغرق التثبيت بضع دقائق
- ✅ Python 3.9.6 يعمل لكن 3.10+ أفضل

## إذا استمرت المشكلة

### تحقق من البيئة الافتراضية:
```bash
# في مجلد backend
venv\Scripts\activate
python --version
pip list
```

### إعادة تثبيت الحزم:
```bash
pip uninstall moviepy -y
pip install moviepy
```

### أو إعادة تثبيت كل شيء:
```bash
pip install --force-reinstall -r requirements.txt
```

