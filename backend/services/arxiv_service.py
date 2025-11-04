import feedparser
from typing import List, Dict

# Fetch trending AI papers from arXiv via RSS (recent submissions)
# Users can filter by category e.g., cs.CL, cs.CV, cs.LG

def fetch_trending(category: str = "cs.LG", max_results: int = 10) -> List[Dict[str, str]]:
    url = f"https://export.arxiv.org/rss/{category}"
    feed = feedparser.parse(url)
    results: List[Dict[str, str]] = []
    for entry in feed.entries[:max_results]:
        results.append({
            "arxiv_id": entry.get("id", ""),
            "title": entry.get("title", "").strip(),
            "summary": entry.get("summary", "").strip(),
            "published": entry.get("published", ""),
            "link": entry.get("link", ""),
        })
    return results


