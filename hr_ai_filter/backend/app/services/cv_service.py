# ============================================================
# CVService — Procesamiento de CVs PDF (solo texto)
# ============================================================

import io
import os
import pdfplumber
from ..utils.text_utils import clean_text


class CVService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, "data", "results")

        self.cv_txt_dir = os.path.join(results_dir, "cv_txt")
        os.makedirs(self.cv_txt_dir, exist_ok=True)

        print("📄 CVService iniciado (solo texto, sin embeddings)")

    def process_cv(self, filename: str, file_bytes: bytes):
        # Extraer texto del PDF
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            text = clean_text("\n".join(pages))
        except Exception as e:
            print("❌ Error leyendo PDF:", e)
            text = ""

        # Guardar texto
        safe_name = filename.replace(".pdf", "")
        txt_path = os.path.join(self.cv_txt_dir, f"{safe_name}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        return {
            "text": text,
            "paths": {"txt": txt_path},
        }
