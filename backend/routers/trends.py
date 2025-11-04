from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from services.arxiv_service import fetch_trending
from services.gemini_service import classify_field_with_gemini
from database.db import get_db
from database.models import Trend
from loguru import logger

router = APIRouter()

@router.get("/trending")
def trending(category: str = Query("cs.LG"), limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    """
    Fetch trending papers from arXiv and classify them by AI field
    """
    try:
        logger.info(f"Fetching trending papers: category={category}, limit={limit}")
        items = fetch_trending(category=category, max_results=limit)
        
        if not items:
            return {"items": [], "message": "No trending papers found"}
        
        # Classify into AI fields and optionally upsert into DB
        results = []
        for it in items:
            try:
                field = classify_field_with_gemini(f"{it['title']}\n{it['summary']}")
                results.append({**it, "field": field})
                
                # Upsert by arxiv_id if available
                if it.get("arxiv_id"):
                    try:
                        existing = db.query(Trend).filter(Trend.arxiv_id == it["arxiv_id"]).first()
                        if not existing:
                            db.add(Trend(
                                arxiv_id=it["arxiv_id"],
                                title=it["title"],
                                summary=it["summary"],
                                field=field,
                                published_at=it.get("published", "")
                            ))
                            db.commit()
                    except Exception as e:
                        logger.warning(f"Could not save trend to DB: {e}")
                        db.rollback()
            except Exception as e:
                logger.warning(f"Error classifying paper {it.get('title', 'unknown')}: {e}")
                # Include without classification
                results.append({**it, "field": "Unknown"})
        
        return {"items": results, "count": len(results)}
        
    except Exception as e:
        logger.error(f"Error fetching trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


