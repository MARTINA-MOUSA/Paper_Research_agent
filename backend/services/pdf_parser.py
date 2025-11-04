from pdfminer.high_level import extract_text
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    يستخرج النص من ملف PDF
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found.")
    return extract_text(file_path)

