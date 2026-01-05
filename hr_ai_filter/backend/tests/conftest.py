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
    # Ensure test assets exist (create minimal PDFs for CVs and Jobs)
    from pathlib import Path
    import os

    tests_dir = Path(__file__).parent.parent

    # Create test_cvs folder and a minimal CV PDF
    test_cvs_dir = tests_dir / "test_cvs"
    test_cvs_dir.mkdir(exist_ok=True)
    cv_pdf = test_cvs_dir / "CV_DevOps.pdf"

    def _write_minimal_pdf(path, text="Hello from test PDF"):
        content = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\nendobj\n"
            b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 72 712 Td ("
            + text.encode("utf-8")
            + b") Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000110 00000 n \n0000000210 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\nstartxref\n300\n%%EOF"
        )
        with open(path, "wb") as f:
            f.write(content)

    if not cv_pdf.exists():
        _write_minimal_pdf(cv_pdf, "DevOps CV")

    # Create a test jobs folder and a job PDF that JobService will load
    test_jobs_dir = tests_dir / "test_jobs"
    test_jobs_dir.mkdir(exist_ok=True)
    job_pdf = test_jobs_dir / "Ingeniero_DevOps.pdf"
    if not job_pdf.exists():
        _write_minimal_pdf(job_pdf, "Ingeniero DevOps\nRequisitos: Python, AWS")

    # Point JobService to use our test jobs dir
    os.environ["JOBS_DIR"] = str(test_jobs_dir)

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