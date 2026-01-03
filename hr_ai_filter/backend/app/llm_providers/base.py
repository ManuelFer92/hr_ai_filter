# ============================================================
# base.py — Abstract LLM Provider Interface
# ============================================================

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Implement this interface to add new LLM backends (Gemini, Ollama, OpenAI, etc.)
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'gemini', 'ollama')"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name being used"""
        pass

    @abstractmethod
    def compare(
        self,
        cv_text: str,
        job_text: str,
        job_name: str,
        cv_filename: str
    ) -> dict:
        """
        Compare a CV against a job description.
        
        Returns a dict with:
        - score_final: int (0-100)
        - resumen: str
        - fortalezas: list[str]
        - debilidades: list[str]
        """
        pass

    @abstractmethod
    def evaluate_recommendation(
        self,
        cv_text: str,
        job_text: str,
        llm_result: dict
    ) -> Optional[int]:
        """
        Evaluate the quality of an LLM recommendation (LLM-as-a-judge).
        
        Returns an int from 1-5, or None if evaluation fails.
        """
        pass

    def _build_comparison_prompt(
        self,
        cv_text: str,
        job_text: str,
        job_name: str
    ) -> str:
        """Build the standard comparison prompt."""
        return f"""
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

    def _build_evaluation_prompt(
        self,
        cv_text: str,
        job_text: str,
        llm_result: dict
    ) -> str:
        """Build the evaluation prompt for LLM-as-a-judge."""
        return f"""
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
