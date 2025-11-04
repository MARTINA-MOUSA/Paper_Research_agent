from fastapi import APIRouter, Body, HTTPException
from services.gemini_service import classify_field_with_gemini
from loguru import logger

router = APIRouter()

@router.post("/field")
def classify_field(text: str = Body("")):
    """
    Classify text into AI field categories using Gemini
    """
    try:
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters")
        
        field = classify_field_with_gemini(text)
        return {"predicted_field": field}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying field: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error classifying field: {str(e)}")

