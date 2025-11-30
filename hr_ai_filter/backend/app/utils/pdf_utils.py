# ============================================================
# pdf_utils.py — Utilidad para extraer texto de PDFs
# ============================================================

import os
import pdfplumber


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extrae texto completo desde un archivo PDF usando pdfplumber.
    Devuelve un string con el texto concatenado de todas las páginas.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"El archivo no existe: {pdf_path}")

    pages_text = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as e:
        print(f"❌ Error leyendo PDF {pdf_path}: {e}")
        return ""

    return "\n".join(pages_text).strip()
