# ============================================================
# CVService — Procesamiento de CVs PDF + Embeddings
# ============================================================

import io
import os
import json
import pdfplumber
from sentence_transformers import SentenceTransformer
from ..utils.text_utils import clean_text

class CVService:

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, "data", "results")

        self.cv_txt_dir = os.path.join(results_dir, "cv_txt")
        self.cv_json_dir = os.path.join(results_dir, "cv_json")

        os.makedirs(self.cv_txt_dir, exist_ok=True)
        os.makedirs(self.cv_json_dir, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("🧠 CVService: modelo de embeddings cargado.")

    def _extract_text_from_bytes(self, file_bytes: bytes) -> str:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            text = "\n".join(pages)
        except Exception as e:
            print("❌ Error leyendo PDF:", e)
            text = ""

        return clean_text(text)

    def _save_text(self, filename: str, text: str) -> str:
        safe = filename.replace(".pdf", "")
        path = os.path.join(self.cv_txt_dir, f"{safe}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def _save_embedding(self, filename: str, text: str, embedding) -> str:
        safe = filename.replace(".pdf", "")
        path = os.path.join(self.cv_json_dir, f"{safe}.json")
        data = {
            "filename": safe,
            "text": text,
            "embedding_dim": len(embedding),
            "embedding": embedding,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def process_cv(self, filename: str, file_bytes: bytes):
        text = self._extract_text_from_bytes(file_bytes)
        embedding = self.model.encode(text).tolist() if text.strip() else []

        txt_path = self._save_text(filename, text)
        json_path = self._save_embedding(filename, text, embedding)

        return {
            "text": text,
            "embedding": embedding,
            "paths": {"txt": txt_path, "json": json_path},
        }
