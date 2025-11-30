# ============================================================
# CVService — Procesamiento de CVs PDF + Embeddings
# ============================================================

import os
import json
import pdfplumber
from sentence_transformers import SentenceTransformer


class CVService:
    def __init__(self):
        self.base_dir = os.path.join("app", "data", "results")
        self.cv_txt_dir = os.path.join(self.base_dir, "cv_txt")
        self.cv_json_dir = os.path.join(self.base_dir, "cv_json")

        os.makedirs(self.cv_txt_dir, exist_ok=True)
        os.makedirs(self.cv_json_dir, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def extract_text(self, file_bytes: bytes) -> str:
        import io
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
                return "\n".join(pages).strip()
        except:
            return ""

    def save_text(self, filename, text):
        path = os.path.join(self.cv_txt_dir, f"{filename}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def save_embedding(self, filename, text, embedding):
        path = os.path.join(self.cv_json_dir, f"{filename}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "filename": filename,
                "text": text,
                "embedding": embedding
            }, f, indent=2, ensure_ascii=False)
        return path

    def process_cv(self, filename: str, file_bytes: bytes):
        text = self.extract_text(file_bytes)
        embedding = self.model.encode(text).tolist()

        txt_path = self.save_text(filename, text)
        emb_path = self.save_embedding(filename, text, embedding)

        return {
            "text": text,
            "embedding": embedding,
            "paths": {
                "txt": txt_path,
                "json": emb_path
            }
        }
