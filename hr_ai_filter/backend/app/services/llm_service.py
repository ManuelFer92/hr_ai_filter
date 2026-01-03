# ============================================================
# LLMService — CV vs Job Matching + Evaluation Layer + MLflow
# ============================================================

import requests
import json
import re
import time
import mlflow
import os

# ------------------------------------------------------------
# CONFIGURACIÓN MLFLOW (SE EJECUTA AL IMPORTAR)
# ------------------------------------------------------------
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("hr_ai_filter_llm")

print(f"✅ MLflow configurado en {MLFLOW_TRACKING_URI}")

# ============================================================
# SERVICIO LLM
# ============================================================

class LLMService:
    def __init__(self):
        # ⚠️ CRÍTICO PARA DOCKER → ACCESO AL HOST
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434/api/generate"
        )

        self.model_name = os.getenv(
            "OLLAMA_MODEL",
            "llama3.1:8b"
        )

        print(f"🔥 LLMService inicializado")
        print(f"   → Ollama URL : {self.base_url}")
        print(f"   → Modelo    : {self.model_name}")

    # ========================================================
    # MATCHING PRINCIPAL (CV vs JOB)
    # ========================================================
    def compare(
        self,
        cv_text: str,
        job_text: str,
        job_name: str,
        cv_filename: str
    ):
        """
        Compara un CV contra un Job usando un LLM.
        Registra métricas en MLflow.
        """

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

        start_time = time.time()

        with mlflow.start_run(run_name=f"eval_{job_name}"):

            # ---------------------------
            # PARAMS
            # ---------------------------
            mlflow.log_param("job_name", job_name)
            mlflow.log_param("model_name", self.model_name)

            # ---------------------------
            # TAGS (TRAZABILIDAD)
            # ---------------------------
            mlflow.set_tag("cv_filename", cv_filename)
            mlflow.set_tag("llm_model", self.model_name)
            mlflow.set_tag("llm_provider", "ollama")
            mlflow.set_tag("task", "cv_job_matching")

            # ---------------------------
            # MÉTRICAS PRE-LLAMADA
            # ---------------------------
            mlflow.log_metric("prompt_length", len(prompt))
            mlflow.log_metric("cv_text_length", len(cv_text))
            mlflow.log_metric("job_text_length", len(job_text))

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
            }

            # ---------------------------
            # LLAMADA AL LLM
            # ---------------------------
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=120
            )

            elapsed = time.time() - start_time

            raw_output = response.json().get("response", "")

            # ---------------------------
            # MÉTRICAS POST-LLAMADA
            # ---------------------------
            mlflow.log_metric("response_time_ms", elapsed * 1000)
            mlflow.log_metric("response_length", len(raw_output))

            # ---------------------------
            # PARSEO
            # ---------------------------
            parsed_ok = 0
            result = None

            try:
                result = json.loads(raw_output)
                parsed_ok = 1
            except Exception:
                matches = re.findall(r"\{.*\}", raw_output, re.DOTALL)
                if matches:
                    try:
                        result = json.loads(matches[0])
                        parsed_ok = 1
                    except Exception:
                        pass

            mlflow.log_metric("parse_success", parsed_ok)

            if not result:
                mlflow.log_text(raw_output, "raw_response.txt")
                raise RuntimeError("❌ No se pudo parsear la respuesta del LLM")

            # ---------------------------
            # MÉTRICAS DE NEGOCIO
            # ---------------------------
            score = result.get("score_final")
            if isinstance(score, (int, float)):
                mlflow.log_metric("score_final", score)

            fortalezas = result.get("fortalezas", [])
            debilidades = result.get("debilidades", [])
            resumen = result.get("resumen", "")

            mlflow.log_metric("fortalezas_count", len(fortalezas))
            mlflow.log_metric("debilidades_count", len(debilidades))
            mlflow.log_metric("summary_length", len(resumen))

            # ---------------------------
            # CAPA DE EVALUACIÓN (LLM-AS-A-JUDGE)
            # ---------------------------
            eval_score = self.evaluate_recommendation(
                cv_text=cv_text,
                job_text=job_text,
                llm_result=result
            )

            if eval_score is not None:
                mlflow.log_metric("llm_evaluation_score", eval_score)
                result["llm_evaluation_score"] = eval_score

            # ---------------------------
            # ARTIFACTS
            # ---------------------------
            mlflow.log_text(prompt.strip(), "prompt.txt")
            mlflow.log_text(raw_output.strip(), "raw_response.txt")

            return result

    # ========================================================
    # CAPA DE EVALUACIÓN — LLM-AS-A-JUDGE
    # ========================================================
    def evaluate_recommendation(
        self,
        cv_text: str,
        job_text: str,
        llm_result: dict
    ):
        """
        Evalúa la calidad de la recomendación generada.
        Devuelve un score entero de 1 a 5.
        """

        prompt = f"""
Evalúa si la recomendación generada es adecuada para el puesto.

CV:
{cv_text}

JOB:
{job_text}

RECOMENDACIÓN:
Score: {llm_result.get("score_final")}
Resumen: {llm_result.get("resumen")}
Fortalezas: {llm_result.get("fortalezas")}
Debilidades: {llm_result.get("debilidades")}

Responde SOLO un número entero del 1 al 5:
1 = Muy mala
5 = Excelente
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=60
            )
            raw = response.json().get("response", "").strip()
            value = int(re.findall(r"\d+", raw)[0])
            return max(1, min(value, 5))
        except Exception:
            return None
