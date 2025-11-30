# import re
# from typing import Dict, List


# class ExtractService:

#     def extract_contact_info(self, text: str) -> Dict[str, str]:
#         """
#         Extrae email, teléfono y URLs básicas como LinkedIn o GitHub.
#         """
#         email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
#         phone = re.findall(r"\+?\d[\d\s\-\(\)]{7,}\d", text)
#         urls = re.findall(r"https?://\S+", text)

#         return {
#             "email": email[0] if email else None,
#             "phone": phone[0] if phone else None,
#             "urls": urls
#         }

#     def extract_name(self, text: str) -> str:
#         """
#         Heurística simple para detectar nombres:
#         - Primera línea del CV
#         - Mayúsculas con 2 o 3 palabras
#         """
#         lines = text.split("\n")

#         # Primera línea como nombre probable
#         first_line = lines[0].strip()

#         # Nombre típico: 2–4 palabras iniciales con capitalización
#         if re.match(r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}$", first_line):
#             return first_line

#         return None

#     def extract_skills(self, text: str) -> List[str]:
#         """
#         Busca skills conocidas mediante un diccionario básico.
#         """
#         skill_bank = [
#             "python", "java", "javascript", "sql", "excel",
#             "react", "node", "docker", "kubernetes", "aws",
#             "azure", "tensorflow", "pytorch", "scikit-learn",
#             "nlp", "machine learning", "deep learning"
#         ]

#         found = []
#         lower = text.lower()

#         for s in skill_bank:
#             if s in lower:
#                 found.append(s)

#         return list(set(found))

#     def extract_education(self, text: str) -> List[str]:
#         """
#         Detecta líneas que contengan grados académicos.
#         """
#         edu_keywords = ["bachelor", "licenciado", "ingeniero", "master", "maestría",
#                         "doctor", "phd", "universidad", "college", "institute"]

#         lines = text.split("\n")

#         matches = [
#             line.strip()
#             for line in lines
#             if any(k in line.lower() for k in edu_keywords)
#         ]

#         return matches[:3]  # limita para no llenar demasiado

#     def extract_experience(self, text: str) -> List[str]:
#         """
#         Extrae 2-3 líneas relacionadas a experiencia laboral.
#         """
#         exp_keywords = ["experience", "experiencia", "work", "trabajo", "laboral"]

#         lines = text.split("\n")

#         matches = [
#             line.strip()
#             for line in lines
#             if any(k in line.lower() for k in exp_keywords)
#         ]

#         return matches[:3]

#     def extract_all(self, text: str) -> Dict:
#         """
#         Ejecuta todos los extractores y retorna un diccionario estructurado.
#         """
#         return {
#             "name": self.extract_name(text),
#             "contact": self.extract_contact_info(text),
#             "skills": self.extract_skills(text),
#             "education": self.extract_education(text),
#             "experience": self.extract_experience(text),
#             "total_chars": len(text)
#         }
