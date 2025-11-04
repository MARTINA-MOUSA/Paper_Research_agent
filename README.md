Paper2Video
===========

## Overview
- Takes a research paper PDF, segments it into understandable sections, and explains it as a short video in Arabic.
- Fetches trending papers from arXiv and classifies them by AI field.
- Uses Gemini API for: segmentation, summarization, video script generation, and field classification.

## Architecture

### Backend Structure
- `services/pdf_parser.py`: Extract text from PDF files.
- `services/gemini_service.py`: Gemini API functions
  - `segment_paper(text)` - Segment paper into sections with title and simple summary.
  - `summarize_with_gemini(text)` - Generate organized summary.
  - `classify_field_with_gemini(text)` - Classify into AI fields.
  - `generate_video_script(sections)` - Convert sections to video scenes (overlay + narration).
  - `extract_keywords(text)` - Extract keywords.
- `services/video_maker.py`: Convert script to video:
  - gTTS for Arabic audio narration.
  - MoviePy for combining on-screen text + audio.
- `services/arxiv_service.py`: Fetch trending papers from arXiv RSS.
- `routers/papers.py`: Upload PDF and return: summary, field, keywords, sections, script, video_path.
- `routers/classify.py`: POST text -> AI field classification using Gemini.
- `routers/trends.py`: GET `/trends/trending?category=cs.LG&limit=10` fetches trends + field classification.
- `database/` SQLite (SQLAlchemy): Tables `papers`, `trends` (auto-created on startup).
- `main.py`: FastAPI setup + CORS + router inclusion + table creation on startup.

## Workflow Pipeline

1. User uploads PDF → `pdf_parser.extract_text_from_pdf`.
2. Gemini segments text → `segment_paper`, then generates video script → `generate_video_script`.
3. Classify field and extract keywords → `classify_field_with_gemini`, `extract_keywords`.
4. `video_maker.make_video_from_scenes` creates MP4 video with Arabic narration and on-screen text.
5. Returns JSON with all results + video path.
6. Trends: `trends/trending` fetches from arXiv and classifies each item by AI field and stores summary.

## Local Development

### Setup

1. **Create environment file with Gemini API key:**
```bash
backend/.env
GEMINI_API_KEY=YOUR_API_KEY
```

2. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the server:**
```bash
uvicorn main:app --reload
```

### Testing Endpoints

- Upload paper: `POST /papers/upload` (multipart file)
- Classify text: `POST /classify/field` body = raw text
- arXiv trends: `GET /trends/trending?category=cs.LG&limit=10`

## Notes

- Video generation relies on gTTS (Arabic audio) and MoviePy; audio engine can be replaced if needed.
- Video output is written to `backend/outputs/` directory.
- Uses arXiv RSS via `feedparser`; can later use a broader search interface or smart filtering.

## Production Deployment

The project is production-ready with:

### Added Features:
- ✅ **Docker & Docker Compose** for easy deployment
- ✅ **Gunicorn + Uvicorn** production server
- ✅ **Comprehensive Logging** with Loguru
- ✅ **Enhanced Error Handling**
- ✅ **Health Check** endpoint (`/health`)
- ✅ **Input Validation** (PDF validation, file size limits)
- ✅ **Configuration Management** via environment variables
- ✅ **Database Connection Pooling** for performance
- ✅ **Security** (CORS configurable, file type validation)

### Quick Start:
```bash
# Docker (Recommended)
cd backend
docker-compose up -d

# Or Gunicorn directly
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Production Files:
- `Dockerfile` - Docker image
- `docker-compose.yml` - Docker Compose configuration
- `gunicorn_config.py` - Gunicorn settings
- `config.py` - Configuration management
- `.env.example` - Environment file template
- `PRODUCTION.md` - Complete deployment guide

See `PRODUCTION.md` for full details on deployment, monitoring, and scaling.
