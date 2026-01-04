# ============================================================
# JobService — Carga y gestión de convocatorias (Jobs)
# ============================================================

import os
import pdfplumber
from ..utils.text_utils import clean_text


class JobService:
    def __init__(self):
        """
        Carga los PDFs de convocatorias desde:
        /app/data/jobs (Docker) or configurable via JOBS_DIR env var
        """

        # Use environment variable or default to /app/data/jobs
        self.jobs_dir = os.environ.get("JOBS_DIR", "/app/data/jobs")

        print(f"📂 JobService | Buscando jobs en: {self.jobs_dir}")

        self.jobs = []

        if not os.path.exists(self.jobs_dir):
            print("❌ JobService | Directorio NO existe")
            return

        files = os.listdir(self.jobs_dir)
        print(f"📄 JobService | Archivos encontrados: {files}")

        for filename in files:
            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(self.jobs_dir, filename)
            print(f"📑 JobService | Procesando: {filename}")

            try:
                with pdfplumber.open(pdf_path) as pdf:
                    pages = [page.extract_text() or "" for page in pdf.pages]
                text = clean_text("\n".join(pages))
            except Exception as e:
                print(f"❌ Error leyendo {filename}: {e}")
                text = ""

            job_name = (
                filename
                .replace(".pdf", "")
                .replace("_", " ")
                .title()
            )

            self.jobs.append({
                "job_name": job_name,
                "filename": filename,
                "text": text,
            })

        print(f"✅ JobService | Jobs cargados: {len(self.jobs)}")

    def list_jobs(self):
        return {"jobs": self.jobs}

    def get_job_by_name(self, name: str):
        for job in self.jobs:
            if job["job_name"] == name:
                return job
        return None
