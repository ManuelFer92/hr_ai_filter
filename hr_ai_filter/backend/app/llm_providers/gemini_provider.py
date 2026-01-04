# ============================================================
# gemini_provider.py — Google Gemini LLM Provider with LangGraph
# ============================================================

import os
import json
import re
import time
from typing import Optional

import google.generativeai as genai
import mlflow

from .base import LLMProvider
from ..graphs.cv_analysis_graph import CVAnalysisGraph


class GeminiProvider(LLMProvider):
    """
    LLM Provider implementation for Google Gemini API.
    Now uses LangGraph for structured workflow orchestration.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini provider")

        genai.configure(api_key=api_key)

        self._model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self._model = genai.GenerativeModel(self._model_name)
        
        # Initialize LangGraph workflow (without checkpointing for simplicity)
        use_checkpointing = os.getenv("LANGGRAPH_CHECKPOINTING", "false").lower() == "true"
        self._graph = CVAnalysisGraph(llm_provider=self, use_checkpointing=use_checkpointing)

        print(f"🔥 GeminiProvider initialized with LangGraph")
        print(f"   → Model: {self._model_name}")
        print(f"   → Workflow: CVAnalysisGraph")
        print(f"   → Checkpointing: {use_checkpointing}")

    @property
    def provider_name(self) -> str:
        return "gemini"

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
        """
        Compare CV against job using LangGraph workflow.
        
        This method now delegates to the LangGraph workflow which:
        1. Extracts skills from CV
        2. Extracts requirements from job
        3. Calculates skill match
        4. Generates recommendation
        5. Evaluates quality
        """
        
        return self._graph.analyze(
            cv_text=cv_text,
            job_text=job_text,
            job_name=job_name,
            cv_filename=cv_filename
        )

    def evaluate_recommendation(
        self,
        cv_text: str,
        job_text: str,
        llm_result: dict
    ) -> Optional[int]:
        """Evaluate recommendation quality using Gemini."""

        prompt = self._build_evaluation_prompt(cv_text, job_text, llm_result)

        try:
            response = self._model.generate_content(prompt)
            raw = response.text.strip()
            value = int(re.findall(r"\d+", raw)[0])
            return max(1, min(value, 5))
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            return None