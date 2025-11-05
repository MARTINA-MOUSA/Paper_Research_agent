import google.generativeai as genai
import os
from typing import List, Dict
from config import settings
from loguru import logger

api_key = settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY/GOOGLE_API_KEY not set")
else:
    genai.configure(api_key=api_key)

_resolved_model_name = None

def _resolve_model_name(preferred: str) -> str:
    """Resolve a usable Gemini model name that supports generateContent."""
    candidates = [
        preferred,
        "gemini-2.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-8b-latest",
        "gemini-1.5-pro-latest",
    ]
    try:
        models = list(genai.list_models())
        # Prefer models that support generateContent
        supported = [
            m.name for m in models
            if getattr(m, "supported_generation_methods", None) and "generateContent" in m.supported_generation_methods
        ]
        # Map short names to fully qualified if needed
        normalized_supported = set([
            n.replace("models/", "") for n in supported
        ])
        for c in candidates:
            short = c.replace("models/", "")
            if short in normalized_supported:
                return short
    except Exception as e:
        logger.debug(f"Could not list models, falling back to candidates: {e}")
    # Fallback to the first candidate
    return candidates[0]

def _get_model(model_name: str = None):
    """Get Gemini model instance with resilient model resolution"""
    global _resolved_model_name
    base = model_name or settings.GEMINI_MODEL
    if not _resolved_model_name:
        _resolved_model_name = _resolve_model_name(base)
        if _resolved_model_name != base:
            logger.info(f"Using Gemini model: {_resolved_model_name} (from {base})")
    return genai.GenerativeModel(_resolved_model_name)

def summarize_with_gemini(text: str) -> str:
    """
    Generate a smart summary of research paper text using Gemini API
    Returns Arabic summary
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        model = _get_model()
        prompt = f"""You are an intelligent academic assistant. Summarize the following research paper text in Arabic in a clear and organized manner:
        - Introduction
        - Problem
        - Methodology
        - Results
        - Conclusion
        
        Write the summary in Arabic language only.
        
        Text:
        {text}
        """
        response = model.generate_content(prompt)
        result = response.text if response and getattr(response, "text", None) else "No summary generated."
        logger.debug("Summary generated successfully")
        return result
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise

def segment_paper(text: str) -> List[Dict[str, str]]:
    """
    Segment paper into logical sections with simple explanation for each section
    Returns: List of {"title": str, "summary": str} - all in Arabic
    """
    model = _get_model()
    prompt = f"""Divide the following research paper text into main sections. For each section provide:
    - A short title (in Arabic)
    - A simple summary in Arabic for general audience
    
    Return the result as a JSON list with elements containing only the keys: "title" and "summary".
    All text must be in Arabic.
    
    Text:
    {text}
    """
    response = model.generate_content(prompt)
    content = response.text if response and getattr(response, "text", None) else "[]"
    try:
        import json
        sections = json.loads(content)
        if isinstance(sections, list):
            normalized = []
            for sec in sections:
                title = (sec.get("title") or "Section").strip()
                summary = (sec.get("summary") or "").strip()
                normalized.append({"title": title, "summary": summary})
            return normalized
    except Exception:
        pass
    return [{"title": "Overall", "summary": summarize_with_gemini(text)}]

def classify_field_with_gemini(text: str) -> str:
    """Classify paper into AI field categories (NLP, CV, RL, etc.)"""
    model = _get_model()
    fields = [
        "Natural Language Processing (NLP)",
        "Computer Vision",
        "Reinforcement Learning",
        "Speech Processing",
        "Robotics",
        "Machine Learning Theory",
    ]
    constraint = ", ".join(fields)
    prompt = f"""From the following text, determine the most suitable field from these options only:
    {constraint}
    
    Return only the field name without any explanation.
    
    Text:
    {text}
    """
    response = model.generate_content(prompt)
    raw = response.text.strip() if response and getattr(response, "text", None) else ""
    for f in fields:
        if f.lower() in raw.lower():
            return f
    return fields[0]

def generate_video_script(sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Generate video script: for each section -> narration text (Arabic) and on-screen text (overlay)
    Returns list of scenes: {"overlay": str, "narration": str} - all in Arabic
    """
    model = _get_model()
    joined = "\n\n".join([f"{s['title']}: {s['summary']}" for s in sections])
    dialect_instruction = """
    - narration: Use Egyptian Arabic colloquial (عامية مصرية) with simple natural phrasing
    """ if getattr(settings, "ARABIC_DIALECT", "MSA").lower() in ["egyptian", "eg", "egy"] else """
    - narration: Voice-over narration text (in Modern Standard Arabic, simple and clear)
    """
    prompt = f"""Convert the following summaries into a short educational video script.
    For each scene provide:
    - overlay: Short text to display on screen (in Arabic)
    {dialect_instruction}
    
    Return the result as a JSON list with elements containing only "overlay" and "narration" keys.
    All text must be in Arabic.
    
    Text:
    {joined}
    """
    response = model.generate_content(prompt)
    content = response.text if response and getattr(response, "text", None) else "[]"
    try:
        import json
        scenes = json.loads(content)
        normalized = []
        if isinstance(scenes, list):
            for sc in scenes:
                overlay = (sc.get("overlay") or "").strip()
                narration = (sc.get("narration") or overlay).strip()
                if overlay or narration:
                    normalized.append({"overlay": overlay, "narration": narration})
        return normalized or [{"overlay": s.get("title", "Scene"), "narration": s.get("summary", "")} for s in sections]
    except Exception:
        return [{"overlay": s.get("title", "Scene"), "narration": s.get("summary", "")} for s in sections]

def extract_keywords(text: str, k: int = 8) -> List[str]:
    """Extract keywords from text"""
    model = _get_model()
    prompt = f"""Extract exactly {k} keywords from the following text. Return them as a single line separated by commas.
    
    Text:
    {text}
    """
    response = model.generate_content(prompt)
    raw = response.text if response and getattr(response, "text", None) else ""
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p][:k]

def translate_text(text: str, target_language: str) -> str:
    """Translate given text to target language using Gemini."""
    model = _get_model()
    prompt = f"""Translate the following text to {target_language}. Preserve meaning and tone.

Text:
{text}
"""
    response = model.generate_content(prompt)
    return response.text.strip() if response and getattr(response, "text", None) else text
