# ============================================================
# JobService — Procesamiento de Job Descriptions (RUTA FIJA)
# ============================================================

import os
import json
from sentence_transformers import SentenceTransformer
from ..utils.pdf_utils_old import extract_pdf_text


class JobService:
    def __init__(self):

        # Carpeta base del archivo actual
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Ruta real absoluta al directorio jobs_pdf
        self.jobs_pdf_dir = os.path.join(BASE_DIR, "data", "jobs", "jobs_pdf")

        # Rutas para guardar resultados
        self.jobs_txt_dir = os.path.join(BASE_DIR, "data", "results", "jobs_txt")
        self.jobs_json_dir = os.path.join(BASE_DIR, "data", "results", "jobs_json")

        os.makedirs(self.jobs_txt_dir, exist_ok=True)
        os.makedirs(self.jobs_json_dir, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.jobs = self.load_jobs()

    def load_jobs(self):
        jobs = []

        print(f"🔍 Buscando jobs en: {self.jobs_pdf_dir}")

        if not os.path.exists(self.jobs_pdf_dir):
            print(f"❌ No se encontró la carpeta de jobs: {self.jobs_pdf_dir}")
            return jobs

        for pdf_name in os.listdir(self.jobs_pdf_dir):
            if pdf_name.endswith(".pdf"):
                job_name = pdf_name.replace(".pdf", "")
                pdf_path = os.path.join(self.jobs_pdf_dir, pdf_name)

                print(f"📄 Procesando Job: {pdf_name}")

                text = extract_pdf_text(pdf_path)
                embedding = self.model.encode(text).tolist()

                txt_path = os.path.join(self.jobs_txt_dir, f"{job_name}.txt")
                json_path = os.path.join(self.jobs_json_dir, f"{job_name}.json")

                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(text)

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "job_name": job_name,
                        "text": text,
                        "embedding": embedding
                    }, f, indent=2, ensure_ascii=False)

                jobs.append({
                    "job_name": job_name,
                    "text": text,
                    "embedding": embedding,
                    "paths": {
                        "txt": txt_path,
                        "json": json_path
                    }
                })

        return jobs

    def list_jobs(self):
        return self.jobs
