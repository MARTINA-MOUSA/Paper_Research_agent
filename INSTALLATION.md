# 📦 Installation Guide

## Quick Setup (Windows)

### Step 1: Run Setup Script
```bash
cd backend
SETUP.bat
```

This automated script will:
- ✅ Create `.env` file
- ✅ Install all dependencies
- ✅ Verify setup

### Step 2: Configure API Key
1. Open `backend/.env` in a text editor
2. Replace `your_api_key_here` with your actual Gemini API key
3. Get your key from: https://makersuite.google.com/app/apikey

### Step 3: Start Backend
```bash
cd backend
START_BACKEND.bat
```

### Step 4: Start Frontend (in new terminal)
```bash
cd frontend
streamlit run streamlit_app.py
```

## Manual Installation

### Prerequisites
- Python 3.9+ (3.10+ recommended)
- pip package manager
- Gemini API key

### Backend Installation

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   # Windows
   CREATE_ENV.bat
   
   # Or manually create .env with:
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Start server:**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Installation

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Streamlit:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Troubleshooting

### "ModuleNotFoundError" or Missing Packages
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### "Python version past end of life" Warning
- **Python 3.9.6:** Works but shows warning
- **Python 3.10+:** Recommended, no warnings
- The app will still function on 3.9.6

### MoviePy Installation Issues
MoviePy requires ffmpeg. On Windows:
1. Download ffmpeg: https://ffmpeg.org/download.html
2. Add to PATH or install via conda:
   ```bash
   conda install -c conda-forge ffmpeg
   ```

### Port Already in Use
If port 8000 is busy:
```bash
# Change port in .env:
PORT=8001

# Or kill process using port (Windows):
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import Errors
If you see import errors:
1. Make sure you're in the correct directory
2. Verify virtual environment is activated (if using one)
3. Reinstall dependencies:
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

## Verification

### Check Backend
```bash
# From project root
python check_backend.py

# Or visit in browser:
http://localhost:8000/health
```

Should show:
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_configured": true
}
```

### Check Dependencies
```bash
python -c "import fastapi, uvicorn, moviepy, gtts; print('All dependencies installed!')"
```

## Next Steps

After successful installation:
1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:8501
3. ✅ API key configured in `.env`
4. ✅ Dependencies installed

You're ready to use Paper2Video! 🎉

