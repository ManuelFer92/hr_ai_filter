import os
import pdfplumber
from ..utils.text_utils import clean_text

class JobService:
    def __init__(self):
        # Use Docker volume path /app/data or fallback to local ./data
        data_dir = os.environ.get("DATA_DIR", "/app/data")
        jobs_dir = os.path.join(data_dir, "jobs", "jobs_pdf")

        print(f"🔍 Looking for job PDFs in: {jobs_dir}")

        self.jobs = []
        
        # Create directory if it doesn't exist
        os.makedirs(jobs_dir, exist_ok=True)
        
        for file in os.listdir(jobs_dir):
            if file.endswith(".pdf"):
                path = os.path.join(jobs_dir, file)
                print(f"📄 Procesando Job: {file}")

                try:
                    with pdfplumber.open(path) as pdf:
                        pages = [p.extract_text() or "" for p in pdf.pages]
                    text = clean_text("\n".join(pages))
                except:
                    text = ""

                job_name = file.replace(".pdf", "").replace("_", " ").title()
                self.jobs.append({
                    "job_name": job_name,
                    "filename": file,
                    "text": text,
                })

        print(f"✔ Jobs cargados: {len(self.jobs)}")

    def list_jobs(self):
        return {"jobs": self.jobs}

    def get_job_by_name(self, name: str):
        for job in self.jobs:
            if job["job_name"] == name:
                return job
        return None
