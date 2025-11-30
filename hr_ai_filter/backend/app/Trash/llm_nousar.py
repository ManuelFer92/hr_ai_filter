# # hr_ai_filter/backend/app/services/llm.py

# import requests
# import json


# class LLMService:
#     def __init__(
#         self,
#         base_url: str = "http://127.0.0.1:11434/api/generate",
#         model_name: str = "gemma3:270m",
#     ):
#         """
#         Servicio para interactuar con Ollama.
#         """
#         self.base_url = base_url
#         self.model_name = model_name

#     def analyze_text(self, text: str) -> dict:
#         """
#         Envía el texto ya extraído del CV a Ollama y devuelve el análisis.
#         """
#         try:
#             payload = {
#                 "model": self.model_name,
#                 "prompt": f"Analiza este CV y genera un resumen útil:\n\n{text}\n\nResumen:",
#                 "stream": False,
#             }

#             response = requests.post(self.base_url, json=payload)

#             if response.status_code != 200:
#                 return {
#                     "error": f"Error {response.status_code} al consultar Ollama",
#                     "details": response.text,
#                 }

#             data = response.json()

#             return {
#                 "response": data.get("response", ""),
#                 "model": self.model_name,
#             }

#         except Exception as e:
#             return {"error": "Excepción al comunicarse con Ollama", "details": str(e)}
