# ============================================================
# pdf_utils.py — Utilidad para extraer texto de PDFs
# ============================================================

import pdfplumber

def extract_pdf_text(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages).strip()
    except Exception as e:
        print(f"❌ Error leyendo PDF {pdf_path}: {e}")
        return ""
