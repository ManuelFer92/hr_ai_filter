import os
import pdfplumber
from sentence_transformers import SentenceTransformer

BASE_DIR = "data/results"
TXT_DIR = f"{BASE_DIR}/cv_txt"
JSON_DIR = f"{BASE_DIR}/cv_json"

os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


class CVPipeline:

    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    async def process_cv(self, file):
        # Nombre de salida
        filename = file.filename.replace(".pdf", "")
        txt_path = f"{TXT_DIR}/{filename}.txt"
        json_path = f"{JSON_DIR}/{filename}.json"

        # 1) Guardar temporalmente el PDF
        pdf_bytes = await file.read()
        temp_pdf = f"{TXT_DIR}/{filename}_temp.pdf"
        with open(temp_pdf, "wb") as f:
            f.write(pdf_bytes)

        # 2) Extraer texto
        text = ""
        with pdfplumber.open(temp_pdf) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        # Guardar .txt
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        # 3) Generar embedding
        emb = self.embedder.encode(text).tolist()

        # 4) Guardar JSON con embedding
        import json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"filename": filename, "embedding": emb}, f)

        # Eliminar PDF temporal
        os.remove(temp_pdf)

        return {
            "txt_path": txt_path,
            "json_path": json_path,
            "embedding_dim": len(emb)
        }
