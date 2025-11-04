# 🚀 Quick Start Guide

## Prerequisites
- Python 3.11+ installed
- Gemini API key from Google AI Studio

## Step 1: Setup Backend

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create environment file:**
   - Create a file named `.env` in the `backend` folder
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   
   **Windows:**
   ```bash
   start_backend.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start_backend.sh
   ./start_backend.sh
   ```
   
   **Or manually:**
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be running at: `http://localhost:8000`

## Step 2: Setup Frontend

1. **Open a NEW terminal/command prompt** (keep backend running)

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Streamlit app:**
   
   **Windows:**
   ```bash
   run.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   **Or manually:**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   The app will open at: `http://localhost:8501`

## Step 3: Use the Application

1. Open your browser and go to `http://localhost:8501`
2. Check the sidebar - the API status should show "✅ API is running"
3. Navigate to "Upload Paper" to upload a PDF
4. Or try "Classify Text" or "Trending Papers"

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify `.env` file exists with `GEMINI_API_KEY`
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Make sure backend is running on `http://localhost:8000`
- Check the API Base URL in the sidebar
- Verify backend is accessible: Open `http://localhost:8000/health` in browser

### Video generation fails
- Ensure ffmpeg is installed (for video processing)
- Check backend logs for errors
- Verify Gemini API key is valid

## API Endpoints

Once backend is running, you can test endpoints:

- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- Upload paper: `POST http://localhost:8000/papers/upload`
- Classify text: `POST http://localhost:8000/classify/field`
- Trending papers: `GET http://localhost:8000/trends/trending?category=cs.LG&limit=10`

## Need Help?

- Check backend logs in the terminal where backend is running
- Check frontend logs in the Streamlit app
- Verify all environment variables are set correctly
- Make sure both servers are running simultaneously

