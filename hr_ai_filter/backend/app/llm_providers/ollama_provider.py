import os
import json
import re
import time
from typing import Optional

import requests
import mlflow

from .base import LLMProvider
from ..graphs.cv_analysis_graph import CVAnalysisGraph


class OllamaProvider(LLMProvider):
    """
    LLM Provider implementation for local Ollama API.
    Now uses LangGraph for structured workflow orchestration.
    """

    def __init__(self):
        self._model_name = os.getenv("LLM_MODEL", "gemma2:2b")
        self._ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        
        # Test connection
        try:
            resp = requests.get(f"{self._ollama_host}/api/tags", timeout=5)
            if not resp.ok:
                raise ConnectionError(f"Ollama not available at {self._ollama_host}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}")
        
        # Initialize LangGraph workflow
        self._graph = CVAnalysisGraph(llm_provider=self)

        print(f"🦙 OllamaProvider initialized with LangGraph")
        print(f"   → Model: {self._model_name}")
        print(f"   → Host: {self._ollama_host}")
        print(f"   → Workflow: CVAnalysisGraph")

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _call_ollama(self, prompt: str, format: str = "json") -> dict:
        """Helper method to call Ollama API."""
        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "format": format
        }
        
        resp = requests.post(
            f"{self._ollama_host}/api/generate",
            json=payload,
            timeout=120
        )
        
        if not resp.ok:
            raise RuntimeError(f"Ollama API error: {resp.text}")
        
        return resp.json()

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
        """Evaluate recommendation quality using Ollama."""

        prompt = self._build_evaluation_prompt(cv_text, job_text, llm_result)

        try:
            result = self._call_ollama(prompt, format="")
            raw = result.get("response", "").strip()
            value = int(re.findall(r"\d+", raw)[0])
            return max(1, min(value, 5))
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            return None
    
    # Override this method to use Ollama's API
    def _generate_content(self, prompt: str) -> str:
        """Generate content using Ollama (used by graph nodes)."""
        result = self._call_ollama(prompt)
        return result.get("response", "")