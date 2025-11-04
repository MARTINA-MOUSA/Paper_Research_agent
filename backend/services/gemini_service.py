import google.generativeai as genai
import os
from typing import List, Dict
from config import settings
from loguru import logger

if not settings.GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set")
else:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def _get_model(model_name: str = None):
    if model_name is None:
        model_name = settings.GEMINI_MODEL
    return genai.GenerativeModel(model_name)

def summarize_with_gemini(text: str) -> str:
    """
    يأخذ نص بحث علمي ويولد ملخص ذكي باستخدام Gemini API
    """
    try:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        model = _get_model()
        prompt = f"""
        أنت مساعد أكاديمي ذكي. لخص النص الآتي بشكل منظم وواضح:
        - المقدمة
        - المشكلة
        - المنهجية
        - النتائج
        - الاستنتاج
        النص:
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
    يقسم الورقة إلى أقسام منطقية مع شرح مبسط لكل قسم
    Returns: List of {"title": str, "summary": str}
    """
    model = _get_model()
    prompt = f"""
    اقسم النص التالي الخاص بورقة علمية إلى أقسام رئيسية. لكل قسم أعط:
    - عنوان قصير
    - ملخص مبسط بالعربية لجمهور عام
    أعد النتيجة بصيغة JSON list من عناصر تحتوي على المفاتيح: title, summary فقط.
    النص:
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
    """يتنبأ بمجال الورقة داخل AI (NLP, CV, RL, ...)."""
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
    prompt = f"""
    من النص التالي، حدد المجال الأكثر مناسبة ضمن الخيارات التالية فقط:
    {constraint}
    أعد الإجابة كاسم مجال واحد فقط بدون شرح.
    النص:
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
    ينتج سيناريو فيديو بسيط: لكل قسم -> نص صوتي (narration) ونص على الشاشة (overlay)
    Returns list of scenes: {"overlay": str, "narration": str}
    """
    model = _get_model()
    joined = "\n\n".join([f"{s['title']}: {s['summary']}" for s in sections])
    prompt = f"""
    حول الملخصات التالية إلى مخطط فيديو تعليمي قصير.
    لكل مشهد أعط:
    - overlay: نص قصير يظهر على الشاشة
    - narration: نص التعليق الصوتي (مقروء للعربية الفصحى المبسطة)
    أعد الناتج كـ JSON list لعناصر تحتوي overlay و narration فقط.
    النص:
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
        return normalized or [{"overlay": s.get("title", "مشهد"), "narration": s.get("summary", "")} for s in sections]
    except Exception:
        return [{"overlay": s.get("title", "مشهد"), "narration": s.get("summary", "")} for s in sections]

def extract_keywords(text: str, k: int = 8) -> List[str]:
    model = _get_model()
    prompt = f"""
    استخرج {k} كلمات مفتاحية فقط من النص التالي. أعدها كسطر واحد مفصول بفواصل.
    النص:
    {text}
    """
    response = model.generate_content(prompt)
    raw = response.text if response and getattr(response, "text", None) else ""
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p][:k]

