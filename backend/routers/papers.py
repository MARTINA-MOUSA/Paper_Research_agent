from fastapi import APIRouter, UploadFile, File
from services.pdf_parser import extract_text_from_pdf
from services.gemini_service import summarize_with_gemini, segment_paper, generate_video_script, classify_field_with_gemini, extract_keywords
from services.video_maker import make_video_from_scenes
import os
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    try:
        file_name = f"{uuid.uuid4()}.pdf"
        save_path = os.path.join("uploads", file_name)
        os.makedirs("uploads", exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(await file.read())

        text = extract_text_from_pdf(save_path)

        os.remove(save_path)

        # Generate structured outputs
        sections = segment_paper(text[:8000])
        script = generate_video_script(sections)
        field = classify_field_with_gemini(text[:3000])
        keywords = extract_keywords(text[:3000])

        # Render video
        os.makedirs("outputs", exist_ok=True)
        video_path = os.path.join("outputs", f"video_{uuid.uuid4().hex}.mp4")
        make_video_from_scenes(script, output_path=video_path)

        summary = summarize_with_gemini(text[:3000])  

        return {
            "summary": summary,
            "field": field,
            "keywords": keywords,
            "sections": sections,
            "script": script,
            "video_path": video_path,
        }

    except Exception as e:
        return {"error": str(e)}

