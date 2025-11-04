from fastapi import APIRouter, Body
from services.gemini_service import classify_field_with_gemini

router = APIRouter()

@router.post("/field")
def classify_field(text: str = Body("")):
    
    field = classify_field_with_gemini(text)
    return {"predicted_field": field}

