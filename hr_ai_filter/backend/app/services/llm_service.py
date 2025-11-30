import requests
import json
import re

class LLMService:
    def __init__(self,
                 base_url="http://127.0.0.1:11434/api/generate",
                 model_name="llama3.1:8b"):
        self.base_url = base_url
        self.model_name = model_name
        print(f"🔥 LLMService cargado con modelo: {self.model_name}")

    def compare(self, cv_text, job_text, job_name):
        prompt = f"""
Eres un sistema experto en selección de personal.
Evalúa el CV contra el puesto: {job_name}

Devuelve SOLO este JSON:

{{
  "score_final": 0-100,
  "resumen": "texto",
  "fortalezas": ["x"],
  "debilidades": ["x"]
}}

CV:
{cv_text}

JOB:
{job_text}
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        resp = requests.post(self.base_url, json=payload)
        raw = resp.json().get("response", "")

        try:
            return json.loads(raw)
        except:
            m = re.findall(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m[0])
                except:
                    pass

        return {"raw_output": raw}
