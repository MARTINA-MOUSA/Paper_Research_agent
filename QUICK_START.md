# 🚀 Quick Start - Installation & Setup

## 🔧 First Time Setup

### If you see "ModuleNotFoundError" or missing dependencies:

**Run the setup script:**
```bash
cd backend
SETUP.bat
```

This will:
1. Create `.env` file
2. Install all dependencies
3. Verify everything is ready

**Or install manually:**
```bash
cd backend
pip install -r requirements.txt
```

### If you see "GEMINI_API_KEY not set":

1. Create `.env` file in `backend` folder:
   ```bash
   cd backend
   CREATE_ENV.bat
   ```
2. Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Get API key from: https://makersuite.google.com/app/apikey

## 🚀 Starting the Application

### Step 1: Install Dependencies (First time only)

**If dependencies are missing:**
```bash
cd backend
INSTALL_DEPENDENCIES.bat
```

**Or manually:**
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

**Create .env file:**
```bash
cd backend
CREATE_ENV.bat
```

Then edit `.env` and add your Gemini API key.

### Step 3: Start Backend

**Easiest way:**
```bash
cd backend
START_BACKEND.bat
```

**Or manually:**
```bash
cd backend
uvicorn main:app --reload
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 4: Start Frontend (NEW terminal)

```bash
cd frontend
streamlit run streamlit_app.py
```

## ❌ Common Errors & Fixes

### Error: "ModuleNotFoundError: No module named 'moviepy'"
**Fix:** Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Error: "GEMINI_API_KEY not set"
**Fix:** Create `.env` file with your API key
```bash
cd backend
CREATE_ENV.bat
# Then edit .env and add your key
```

### Error: "Connection refused"
**Fix:** Backend is not running - start it first!
```bash
cd backend
START_BACKEND.bat
```

### Error: "Python version past end of life"
**Warning (not critical):** Python 3.9.6 works but 3.10+ is recommended.
The app will still work, but consider upgrading Python later.

## ✅ The Solution

### Step 1: Start the Backend

**Easiest way (Windows):**
1. Double-click: `backend/START_BACKEND.bat`
2. Wait until you see: `Uvicorn running on http://0.0.0.0:8000`
3. **Keep that window open!**

**Or manually:**
1. Open a terminal/command prompt
2. Type:
   ```bash
   cd C:\Users\DELL\Desktop\paper2video\backend
   uvicorn main:app --reload
   ```
3. Wait for: `Application startup complete`
4. **Keep that terminal open!**

### Step 2: Verify Backend is Running

Open in your browser: **http://localhost:8000/health**

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_configured": true
}
```

### Step 3: Start Frontend (in a NEW terminal)

1. Open a **NEW** terminal window
2. Type:
   ```bash
   cd C:\Users\DELL\Desktop\paper2video\frontend
   streamlit run streamlit_app.py
   ```
3. The app will open at: http://localhost:8501

## ⚠️ Important Notes

- **You need TWO terminals running:**
  - Terminal 1: Backend server (port 8000)
  - Terminal 2: Frontend Streamlit (port 8501)

- **Don't close the backend terminal!** The server must keep running.

- If you close the backend terminal, the frontend will show connection errors.

## 🎯 One-Command Start (Windows)

From project root, run:
```bash
start_all.bat
```

This starts both backend and frontend automatically!

## 🔍 Troubleshooting

### "Port 8000 already in use"
- Another program is using port 8000
- Close other programs or restart your computer

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`

### Backend starts but frontend still can't connect
- Check backend is actually running: http://localhost:8000/health
- Make sure you didn't close the backend terminal
- Restart backend: Stop (Ctrl+C) and start again

## 📝 Checklist

Before using the app:
- [ ] Backend server is running (check terminal)
- [ ] http://localhost:8000/health shows "healthy"
- [ ] Frontend Streamlit app is running
- [ ] Both terminals are still open

