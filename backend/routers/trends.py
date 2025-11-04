from fastapi import APIRouter, Query, Depends
from typing import List
from services.arxiv_service import fetch_trending
from services.gemini_service import classify_field_with_gemini
from database.db import get_db
from database.models import Trend

router = APIRouter()

@router.get("/trending")
def trending(category: str = Query("cs.LG"), limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    items = fetch_trending(category=category, max_results=limit)
    # classify into AI fields and optionally upsert into DB
    results = []
    for it in items:
        field = classify_field_with_gemini(f"{it['title']}\n{it['summary']}")
        results.append({**it, "field": field})
        # naive upsert by arxiv_id if available
        try:
            if it.get("arxiv_id"):
                existing = db.query(Trend).filter(Trend.arxiv_id == it["arxiv_id"]).first()
                if not existing:
                    db.add(Trend(arxiv_id=it["arxiv_id"], title=it["title"], summary=it["summary"], field=field, published_at=it.get("published", "")))
                    db.commit()
        except Exception:
            db.rollback()
    return {"items": results}


