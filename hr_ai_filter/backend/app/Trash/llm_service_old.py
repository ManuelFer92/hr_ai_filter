import subprocess
import json
import re

class LLMService:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        print(f"🔥 LLMService cargado con: {self.model_name}")

    def compare(self, cv_text: str, job_text: str, job_name: str):

        prompt = f"""
        Analiza la compatibilidad entre este CV y la oferta laboral.

        Puesto: {job_name}

        CV:
        {cv_text}

        Job Description:
        {job_text}

        Devuelve el resultado en formato JSON así:

        {{
          "score_final": 0-100,
          "resumen": "...",
          "fortalezas": [...],
          "debilidades": [...]
        }}
        """

        # Ejecutar Ollama
        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=prompt.encode("utf-8"),
            capture_output=True
        )

        output = result.stdout.decode("utf-8").strip()

        # ============================================
        # 1) Intentar JSON directo
        # ============================================
        try:
            return json.loads(output)
        except:
            pass

        # ============================================
        # 2) EXTRAER JSON DENTRO DE UN BLOQUE ```
        # ============================================
        codeblock = re.search(r"```(.*?)```", output, re.DOTALL)
        if codeblock:
            inner = codeblock.group(1).strip()
            try:
                parsed = json.loads(inner)
                return parsed
            except:
                pass

        # ============================================
        # 3) Buscar score_final dentro del texto
        # ============================================
        score = 0

        # formato: score_final": 20
        m_json_score = re.search(r'"score_final"\s*:\s*(\d+)', output)
        if m_json_score:
            score = int(m_json_score.group(1))
        else:
            # formato: Score final: 20/100
            m1 = re.search(r"score\s*final\W*(\d{1,3})\s*/\s*100", output, re.IGNORECASE)
            if m1:
                score = int(m1.group(1))
            else:
                # formato: score: 20
                m2 = re.search(r"score\s*[:\-]\s*(\d{1,3})", output, re.IGNORECASE)
                if m2:
                    score = int(m2.group(1))

        # ============================================
        # 4) Respuesta fallback
        # ============================================
        return {
            "score_final": score,
            "raw_output": output,
            "error": "Respuesta no JSON, score extraído mediante regex/parse"
        }
