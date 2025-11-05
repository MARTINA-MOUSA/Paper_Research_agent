from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from services.pdf_parser import extract_text_from_pdf
from services.gemini_service import summarize_with_gemini, segment_paper, generate_video_script, classify_field_with_gemini, extract_keywords, translate_text
from services.video_maker import make_video_from_scenes
from services.job_manager import create_job, set_status, set_result, set_error, get_job
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
async def upload_paper(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
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

        logger.info(f"Queued PDF for processing: {file_name}")

        # Create job and enqueue background processing
        job_id = create_job()

        def process_job():
            try:
                set_status(job_id, "processing", progress=5)

                # Helper for timeouts
                from concurrent.futures import ThreadPoolExecutor
                import functools
                def run_with_timeout(func, *f_args, timeout_sec: float = 60, default=None, **f_kwargs):
                    try:
                        with ThreadPoolExecutor(max_workers=1) as ex:
                            fut = ex.submit(functools.partial(func, *f_args, **f_kwargs))
                            return fut.result(timeout=timeout_sec)
                    except Exception as e:
                        logger.warning(f"Step '{getattr(func, '__name__', 'call')}' failed or timed out: {e}")
                        return default

                # Extract text with timeout
                text = run_with_timeout(extract_text_from_pdf, save_path, timeout_sec=90, default="")
                if not text or len(text.strip()) < 100:
                    raise Exception("Could not extract sufficient text from PDF")
                text = text[:settings.MAX_TEXT_LENGTH]
                set_status(job_id, "processing", progress=20)

                # Segment + script
                sections = run_with_timeout(segment_paper, text[:8000], timeout_sec=90, default=None)
                if not sections:
                    sections = [{"title": "الملخص", "summary": "تم تلخيص الورقة لاحقاً بسبب قيود الوقت."}]
                if len(sections) > settings.MAX_SECTIONS:
                    sections = sections[:settings.MAX_SECTIONS]
                set_status(job_id, "processing", progress=40)

                script = run_with_timeout(generate_video_script, sections, timeout_sec=90, default=[])
                if not script:
                    script = [{"overlay": s.get("title", "مشهد"), "narration": s.get("summary", "")} for s in sections]
                set_status(job_id, "processing", progress=55)

                # Classify + keywords
                field = run_with_timeout(classify_field_with_gemini, text[:3000], timeout_sec=30, default="Unknown")
                keywords = run_with_timeout(extract_keywords, text[:3000], timeout_sec=20, default=[])
                set_status(job_id, "processing", progress=65)

                # Video
                os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
                video_filename = f"video_{uuid.uuid4().hex}.mp4"
                out_path = os.path.join(settings.OUTPUT_DIR, video_filename)
                run_with_timeout(make_video_from_scenes, script, timeout_sec=300, default=None, output_path=out_path)
                set_status(job_id, "processing", progress=85)

                # Summary
                summary = run_with_timeout(summarize_with_gemini, text[:3000], timeout_sec=90, default="")
                set_status(job_id, "processing", progress=95)

                result = {
                    "summary": summary,
                    "field": field,
                    "keywords": keywords,
                    "sections": sections,
                    "script": script,
                    "video_filename": video_filename,
                    "video_url": f"/papers/video/{video_filename}"
                }
                set_result(job_id, result)
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
                set_error(job_id, str(e))
            finally:
                # Cleanup uploaded file
                try:
                    if save_path and os.path.exists(save_path):
                        os.remove(save_path)
                except Exception as ce:
                    logger.warning(f"Could not remove temp file: {ce}")

        if background_tasks is not None:
            background_tasks.add_task(process_job)
        else:
            import threading
            threading.Thread(target=process_job, daemon=True).start()

        return {"job_id": job_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing paper: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing paper: {str(e)}")
    finally:
        # Do not delete here; background process cleans it after finishing
        pass

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


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Poll job status and result if available"""
    job = get_job(job_id)
    if not job or job.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/translate")
async def translate(text: str = "", target_language: str = "English"):
    """Translate arbitrary text to a target language using Gemini"""
    try:
        if not text or len(text.strip()) < 1:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        translated = translate_text(text, target_language)
        return {"translated": translated, "target_language": target_language}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

