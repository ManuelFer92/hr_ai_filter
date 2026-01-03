# ============================================================
# LLMService — Factory for LLM Providers + MLflow Configuration
# ============================================================

import os
import mlflow

from ..llm_providers import GeminiProvider, OllamaProvider
from ..llm_providers.base import LLMProvider


# ============================================================
# LLM Service (Factory Pattern)
# ============================================================

class LLMService:
    """
    Factory service that creates the appropriate LLM provider
    based on the LLM_PROVIDER environment variable.
    
    Supported providers:
    - "gemini": Google Gemini API (requires GOOGLE_API_KEY)
    - "ollama": Local Ollama server (requires OLLAMA_HOST)
    """

    _mlflow_initialized = False

    def __init__(self):
        # Initialize MLflow lazily (only when first instance is created)
        if not LLMService._mlflow_initialized:
            self._init_mlflow()
            LLMService._mlflow_initialized = True

        provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()

        print(f"🔧 LLMService | Initializing provider: {provider_name}")

        if provider_name == "gemini":
            self._provider: LLMProvider = GeminiProvider()
        elif provider_name == "ollama":
            self._provider: LLMProvider = OllamaProvider()
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER: {provider_name}. "
                f"Supported: 'gemini', 'ollama'"
            )

        print(f"✅ LLMService | Provider '{self._provider.provider_name}' ready")
        print(f"   → Model: {self._provider.model_name}")

    def _init_mlflow(self):
        """Initialize MLflow with fault tolerance."""
        MLFLOW_TRACKING_URI = os.getenv(
            "MLFLOW_TRACKING_URI",
            "http://mlflow:5000"
        )

        try:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment("hr_ai_filter_llm")
            print(f"✅ MLflow configured at {MLFLOW_TRACKING_URI}")
        except Exception as e:
            print(f"⚠️ MLflow not available: {e}")
            print("   → LLM will run without MLflow tracking")
            # Use local file storage as fallback
            mlflow.set_tracking_uri("file:///tmp/mlruns")
            try:
                mlflow.set_experiment("hr_ai_filter_llm")
            except Exception:
                pass

    @property
    def provider(self) -> LLMProvider:
        """Get the underlying provider instance."""
        return self._provider

    def compare(
        self,
        cv_text: str,
        job_text: str,
        job_name: str,
        cv_filename: str
    ) -> dict:
        """
        Compare a CV against a job description.
        Delegates to the configured LLM provider.
        """
        return self._provider.compare(
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
    ):
        """
        Evaluate the quality of an LLM recommendation.
        Delegates to the configured LLM provider.
        """
        return self._provider.evaluate_recommendation(
            cv_text=cv_text,
            job_text=job_text,
            llm_result=llm_result
        )
