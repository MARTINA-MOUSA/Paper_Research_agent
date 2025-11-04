from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.pdf_parser import extract_text_from_pdf
from services.gemini_service import summarize_with_gemini, segment_paper, generate_video_script, classify_field_with_gemini, extract_keywords
from services.video_maker import make_video_from_scenes
from config import settings
from loguru import logger
import os
import uuid
import magic

router = APIRouter()

def validate_pdf_file(file: UploadFile) -> None:
    """Validate uploaded file is a PDF"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Check content type
    content = file.file.read(1024)
    file.file.seek(0)
    mime = magic.Magic(mime=True)
    detected_type = mime.from_buffer(content)
    
    if detected_type != 'application/pdf':
        raise HTTPException(status_code=400, detail=f"Invalid file type: {detected_type}")

@router.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    """
    Upload a research paper PDF and generate:
    - Summary
    - Sections breakdown
    - Video explanation
    - Field classification
    - Keywords
    """
    save_path = None
    video_path = None
    
    try:
        # Validate file
        validate_pdf_file(file)
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        file_name = f"{uuid.uuid4()}.pdf"
        save_path = os.path.join(settings.UPLOAD_DIR, file_name)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Processing PDF: {file_name}")
        
        # Extract text
        text = extract_text_from_pdf(save_path)
        if not text or len(text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        
        # Limit text length for processing
        text = text[:settings.MAX_TEXT_LENGTH]
        
        # Generate structured outputs
        logger.info("Segmenting paper...")
        sections = segment_paper(text[:8000])
        if len(sections) > settings.MAX_SECTIONS:
            sections = sections[:settings.MAX_SECTIONS]
        
        logger.info("Generating video script...")
        script = generate_video_script(sections)
        
        logger.info("Classifying field...")
        field = classify_field_with_gemini(text[:3000])
        
        logger.info("Extracting keywords...")
        keywords = extract_keywords(text[:3000])
        
        # Render video
        logger.info("Generating video...")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        video_filename = f"video_{uuid.uuid4().hex}.mp4"
        video_path = os.path.join(settings.OUTPUT_DIR, video_filename)
        make_video_from_scenes(script, output_path=video_path)
        
        logger.info("Generating summary...")
        summary = summarize_with_gemini(text[:3000])
        
        logger.info(f"Successfully processed paper: {file_name}")
        
        return {
            "summary": summary,
            "field": field,
            "keywords": keywords,
            "sections": sections,
            "script": script,
            "video_filename": video_filename,
            "video_url": f"/papers/video/{video_filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing paper: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing paper: {str(e)}")
    finally:
        # Cleanup uploaded file
        if save_path and os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file: {e}")

@router.get("/video/{filename}")
async def get_video(filename: str):
    """Serve generated video files"""
    video_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not filename.endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )

