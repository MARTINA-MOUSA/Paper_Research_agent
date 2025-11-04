import feedparser
from typing import List, Dict
from loguru import logger

# Fetch trending AI papers from arXiv via RSS (recent submissions)
# Users can filter by category e.g., cs.CL, cs.CV, cs.LG

def fetch_trending(category: str = "cs.LG", max_results: int = 10) -> List[Dict[str, str]]:
    """
    Fetch trending papers from arXiv RSS feed
    """
    try:
        url = f"https://export.arxiv.org/rss/{category}"
        logger.debug(f"Fetching from arXiv: {url}")
        
        # Parse RSS feed
        feed = feedparser.parse(url)
        
        if feed.bozo and feed.bozo_exception:
            logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
        
        results: List[Dict[str, str]] = []
        entries = feed.entries[:max_results] if feed.entries else []
        
        for entry in entries:
            # Extract arxiv ID from link or id
            arxiv_id = ""
            if entry.get("id"):
                arxiv_id = entry["id"].split("/")[-1]
            elif entry.get("link"):
                arxiv_id = entry["link"].split("/")[-1]
            
            results.append({
                "arxiv_id": arxiv_id,
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "published": entry.get("published", ""),
                "link": entry.get("link", ""),
            })
        
        logger.info(f"Fetched {len(results)} papers from arXiv")
        return results
        
    except Exception as e:
        logger.error(f"Error fetching from arXiv: {e}", exc_info=True)
        return []
