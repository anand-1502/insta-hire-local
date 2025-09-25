from pathlib import Path
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return "\n".join(text_parts)
    except Exception:
        return ""
