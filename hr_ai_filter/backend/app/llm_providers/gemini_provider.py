import os
import json
import google.generativeai as genai
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("⚠️ GeminiProvider: GOOGLE_API_KEY is missing!")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(self.model_name)
        print(f"✨ GeminiProvider initialized: model={self.model_name}")

    def compare(self, cv_text, job_text, job_name):
        prompt = f"""
Eres un sistema experto en selección de personal.
Evalúa el CV contra el puesto: {job_name}

Devuelve SOLO un objeto JSON con esta estructura:

{{
  "score_final": 0-100,
  "resumen": "texto breve",
  "fortalezas": ["str"],
  "debilidades": ["str"]
}}

CV:
{cv_text}

JOB:
{job_text}
"""
        try:
            # Gemini supports JSON mode via generation_config
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return {"error": str(e)}
