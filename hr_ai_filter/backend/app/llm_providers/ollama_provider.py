import requests
import json
import re
import os
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, host=None, model=None):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.base_url = f"{self.host}/api/generate"
        self.model_name = model or os.environ.get("LLM_MODEL", "llama3.1:8b")
        print(f"🦙 OllamaProvider initialized: {self.base_url}, model={self.model_name}")

    def compare(self, cv_text, job_text, job_name):
        prompt = f"""
Eres un sistema experto en selección de personal.
Evalúa el CV contra el puesto: {job_name}

Devuelve SOLO este JSON (sin markdown ```json ... ```):

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
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        try:
            resp = requests.post(self.base_url, json=payload, timeout=120)
            raw = resp.json().get("response", "")
            return self._parse_json(raw)
        except Exception as e:
            print(f"❌ Ollama Error: {e}")
            return {"error": str(e), "raw_output": ""}

    def _parse_json(self, raw):
        try:
            # Clean markdown code blocks if present
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            # Fallback regex extraction
            m = re.findall(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m[0])
                except:
                    pass
            return {"raw_output": raw}
