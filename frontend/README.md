# Paper2Video Streamlit Frontend

A user-friendly web interface for the Paper2Video API built with Streamlit.

## Features

- 📤 **Upload Papers**: Upload PDF research papers and generate video explanations
- 🔍 **Classify Text**: Classify text into AI research fields
- 📈 **Trending Papers**: Browse and explore trending papers from arXiv
- 🎬 **Video Preview**: View and download generated videos
- 📑 **Section Breakdown**: View segmented paper sections with summaries

## Installation

1. **Install dependencies:**
```bash
cd frontend
pip install -r requirements.txt
```

2. **Configure API URL (optional):**
   - Create a `.env` file or set environment variable:
   ```
   API_BASE_URL=http://localhost:8000
   ```
   - Default is `http://localhost:8000`

## Running the App

### Development Mode
```bash
streamlit run streamlit_app.py
```

### Production Mode
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## Pages

### 1. Upload Paper
- Upload a PDF research paper
- View generated summary, classification, sections, keywords
- Watch and download the generated video
- View the video script with narration

### 2. Classify Text
- Enter text (abstract, excerpt, etc.)
- Get AI field classification instantly
- Useful for quick categorization

### 3. Trending Papers
- Browse trending papers from arXiv
- Filter by category (cs.LG, cs.CV, cs.CL, etc.)
- View papers with automatic field classification
- Access direct arXiv links

## Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server settings
- Port configuration

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Running Paper2Video API backend (default: http://localhost:8000)

## Docker Deployment (Optional)

You can also run Streamlit in Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Notes

- Ensure the backend API is running before using the frontend
- Large PDF files may take several minutes to process
- Generated videos are stored on the backend and can be downloaded
- API timeout is set to 300 seconds for video generation

