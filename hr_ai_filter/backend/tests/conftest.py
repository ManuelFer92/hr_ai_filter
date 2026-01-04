# tests/conftest.py

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.services.llm_service import LLMService
from backend.app.services.cv_service import CVService
from backend.app.services.job_service import JobService

class FakeLLMProvider:
    provider_name = "gemini"
    model_name = "gemini-2.5-flash"

    def _generate_content(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if "extrae las habilidades" in prompt_lower:
            return '{"skills": ["Python", "SQL", "Docker"]}'

        if "extrae los requisitos" in prompt_lower:
            return '{"requirements": ["Python", "AWS"]}'

        if '"score_final"' in prompt_lower:
            return """
            {
              "score_final": 75,
              "resumen": "Buen encaje general.",
              "fortalezas": ["Experiencia en Python"],
              "debilidades": ["Falta experiencia en AWS"]
            }
            """

        raise ValueError("Prompt no reconocido en FakeLLMProvider")

    def compare(self, cv_text, job_text, job_name, cv_filename):
        return {
            "score_final": 85,
            "resumen": "Buen encaje general con el puesto.",
            "fortalezas": ["Python", "Experiencia relevante"],
            "debilidades": ["Falta liderazgo"],
            "llm_evaluation_score": 4,
            "metadata": {
                "skill_match_score": 75
            }
        }

    def evaluate_recommendation(self, **kwargs) -> int:
        return 8


@pytest.fixture
def fake_llm_provider():
    return FakeLLMProvider()


@pytest.fixture(autouse=True)
def mock_mlflow():
    """Evita llamadas reales a MLflow."""
    with patch("mlflow.start_run"), \
         patch("mlflow.log_metric"), \
         patch("mlflow.log_param"), \
         patch("mlflow.set_tag"):
        yield

@pytest.fixture
def client():
    # Crear la app
    app = create_app()

    # Inicializar manualmente los servicios (para que tests no fallen)
    app.state.cv_service = CVService()
    app.state.job_service = JobService()
    app.state.llm_service = LLMService()
    # app.state.llm_service._provider = FakeLLMProvider()

    # TestClient ejecuta startup/shutdown automáticamente si usamos 'with'
    with TestClient(app) as c:
        yield c