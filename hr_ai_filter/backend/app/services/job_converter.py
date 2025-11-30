import pdfplumber
import os

class JobConverter:
    def __init__(self, jobs_pdf_folder="backend/jobs/pdf", jobs_txt_folder="backend/jobs/txt"):
        self.jobs_pdf_folder = jobs_pdf_folder
        self.jobs_txt_folder = jobs_txt_folder

        os.makedirs(self.jobs_pdf_folder, exist_ok=True)
        os.makedirs(self.jobs_txt_folder, exist_ok=True)

    def pdf_to_text(self, pdf_bytes: bytes, output_name: str):
        """
        Convierte un PDF a texto y lo guarda como .txt para usarlo con el LLM.
        """
        text = ""

        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        clean_text = text.strip()

        # Ruta del archivo .txt generado
        output_path = os.path.join(self.jobs_txt_folder, f"{output_name}.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        return {
            "text": clean_text,
            "path": output_path
        }

    def convert_existing_pdfs(self):
        """
        Convierte todos los PDF dentro de backend/jobs/pdf/ en .txt.
        """
        converted = []

        for filename in os.listdir(self.jobs_pdf_folder):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(self.jobs_pdf_folder, filename)
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                output_name = filename.replace(".pdf", "")
                res = self.pdf_to_text(pdf_bytes, output_name)
                converted.append(res)

        return converted
