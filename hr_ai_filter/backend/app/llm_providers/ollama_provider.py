# ============================================================
# ollama_provider.py — Ollama Local LLM Provider
# ============================================================

import os
import json
import re
import time
import requests
from typing import Optional

import mlflow

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    LLM Provider implementation for local Ollama server.
    Connects to Ollama API for inference.
    """

    def __init__(self):
        # Support both env var names for backwards compatibility
        ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self._base_url = f"{ollama_host}/api/generate"

        self._model_name = os.getenv("LLM_MODEL", "llama3.1:8b")

        print(f"🔥 OllamaProvider initialized")
        print(f"   → Ollama URL: {self._base_url}")
        print(f"   → Model: {self._model_name}")

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    def compare(
        self,
        cv_text: str,
        job_text: str,
        job_name: str,
        cv_filename: str
    ) -> dict:
        """Compare CV against job using Ollama."""

        prompt = self._build_comparison_prompt(cv_text, job_text, job_name)
        start_time = time.time()

        with mlflow.start_run(run_name=f"eval_{job_name}"):
            # Log params and tags
            mlflow.log_param("job_name", job_name)
            mlflow.log_param("model_name", self._model_name)
            mlflow.set_tag("cv_filename", cv_filename)
            mlflow.set_tag("llm_model", self._model_name)
            mlflow.set_tag("llm_provider", "ollama")
            mlflow.set_tag("task", "cv_job_matching")

            # Pre-call metrics
            mlflow.log_metric("prompt_length", len(prompt))
            mlflow.log_metric("cv_text_length", len(cv_text))
            mlflow.log_metric("job_text_length", len(job_text))

            payload = {
                "model": self._model_name,
                "prompt": prompt,
                "stream": False,
            }

            # Call Ollama API (longer timeout for CPU inference)
            response = requests.post(
                self._base_url,
                json=payload,
                timeout=300  # 5 minutes for slow CPU inference
            )

            elapsed = time.time() - start_time
            raw_output = response.json().get("response", "")

            # Post-call metrics
            mlflow.log_metric("response_time_ms", elapsed * 1000)
            mlflow.log_metric("response_length", len(raw_output))

            # Parse response
            parsed_ok = 0
            result = None

            try:
                result = json.loads(raw_output)
                parsed_ok = 1
            except Exception:
                # Try to extract JSON from response
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
                raise RuntimeError("❌ Could not parse LLM response")

            # Business metrics
            score = result.get("score_final")
            if isinstance(score, (int, float)):
                mlflow.log_metric("score_final", score)

            fortalezas = result.get("fortalezas", [])
            debilidades = result.get("debilidades", [])
            resumen = result.get("resumen", "")

            mlflow.log_metric("fortalezas_count", len(fortalezas))
            mlflow.log_metric("debilidades_count", len(debilidades))
            mlflow.log_metric("summary_length", len(resumen))

            # LLM-as-a-judge evaluation
            eval_score = self.evaluate_recommendation(cv_text, job_text, result)
            if eval_score is not None:
                mlflow.log_metric("llm_evaluation_score", eval_score)
                result["llm_evaluation_score"] = eval_score

            # Log artifacts
            mlflow.log_text(prompt.strip(), "prompt.txt")
            mlflow.log_text(raw_output.strip(), "raw_response.txt")

            return result

    def evaluate_recommendation(
        self,
        cv_text: str,
        job_text: str,
        llm_result: dict
    ) -> Optional[int]:
        """Evaluate recommendation quality using Ollama."""

        prompt = self._build_evaluation_prompt(cv_text, job_text, llm_result)

        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                self._base_url,
                json=payload,
                timeout=60
            )
            raw = response.json().get("response", "").strip()
            value = int(re.findall(r"\d+", raw)[0])
            return max(1, min(value, 5))
        except Exception:
            return None
