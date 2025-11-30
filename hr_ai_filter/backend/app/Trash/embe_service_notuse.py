# import os
# import json
# import numpy as np
# from datetime import datetime
# from sentence_transformers import SentenceTransformer


# class EmbedService:

#     def __init__(self):
#         """
#         Carga el modelo de embeddings sólo una vez.
#         """
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")

#     def generate_embedding(self, text: str) -> np.ndarray:
#         """
#         Genera un embedding desde texto limpio usando SentenceTransformer.
#         """
#         if not text or not isinstance(text, str):
#             raise ValueError("El texto está vacío o no es válido.")

#         embedding = self.model.encode(text)
#         return embedding

#     def save_embedding_json(self, text: str, embedding: np.ndarray, output_path: str):
#         """
#         Guarda el texto y el embedding en un archivo JSON dentro de data/results/cv_json/.
#         """
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)

#         data = {
#             "text": text,
#             "embedding": embedding.tolist(),   # convertir numpy → lista
#             "dimension": len(embedding),
#             "timestamp": datetime.now().isoformat(),
#         }

#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)

#         return output_path
