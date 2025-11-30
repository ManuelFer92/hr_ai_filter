# import pdfplumber
# import os
# import json
# from sentence_transformers import SentenceTransformer
# import numpy as np

# class CVPipeline:

#     def __init__(self):
#         self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

#         self.base_text_dir = "data/results/text"
#         self.base_json_dir = "data/results/json"
#         os.makedirs(self.base_text_dir, exist_ok=True)
#         os.makedirs(self.base_json_dir, exist_ok=True)

#     def process_cv(self, filename: str, file_bytes: bytes):

#         # -----------------------------
#         # 1) Guardar bytes como PDF real
#         # -----------------------------
#         pdf_path = os.path.join(self.base_text_dir, filename)

#         with open(pdf_path, "wb") as f:
#             f.write(file_bytes)

#         # -----------------------------
#         # 2) Extraer texto del PDF
#         # -----------------------------
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 pages = [page.extract_text() or "" for page in pdf.pages]
#                 text = "\n".join(pages)
#         except Exception as e:
#             text = ""
#             print("Error leyendo PDF:", e)

#         # Guardar .txt
#         txt_path = pdf_path.replace(".pdf", ".txt")
#         with open(txt_path, "w", encoding="utf-8") as f:
#             f.write(text)

#         # -----------------------------
#         # 3) Embedding
#         # -----------------------------
#         embedding = None
#         if text.strip() != "":
#             embedding = self.embedder.encode(text).tolist()

#         json_path = os.path.join(
#             self.base_json_dir,
#             filename.replace(".pdf", ".json")
#         )

#         with open(json_path, "w", encoding="utf-8") as f:
#             json.dump({
#                 "filename": filename,
#                 "text": text,
#                 "embedding_dim": len(embedding) if embedding else 0
#             }, f, ensure_ascii=False, indent=2)

#         # -----------------------------
#         # 4) Devolver respuesta al frontend
#         # -----------------------------
#         return {
#             "text": text,
#             "embedding": embedding,
#             "paths": {
#                 "pdf": pdf_path,
#                 "txt": txt_path,
#                 "json": json_path
#             }
#         }
