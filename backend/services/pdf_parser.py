from pdfminer.high_level import extract_text
import logging
import os
from config import settings

# Reduce noisy warnings from pdfminer (e.g., FontBBox parsing)
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found.")
    try:
        # Only parse the first N pages to avoid timeouts on huge PDFs
        page_numbers = list(range(max(1, settings.MAX_PDF_PAGES)))
        return extract_text(file_path, page_numbers=page_numbers)
    except Exception:
        # Fallback to default extraction if page_numbers unsupported in env
        return extract_text(file_path)
