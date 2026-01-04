# tests/test_cv_analysis_graph.py

import pytest
from backend.app.graphs.cv_analysis_graph import CVAnalysisGraph


# ============================================================
# TEST: Full graph execution (happy path)
# ============================================================

def test_full_graph_success(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    result = graph.analyze(
        cv_text="Experiencia en Python, SQL y Docker",
        job_text="Buscamos perfil con Python y AWS",
        job_name="Backend Developer",
        cv_filename="cv_test.pdf"
    )

    assert result["score_final"] == 75
    assert result["llm_evaluation_score"] == 8
    assert "Python" in result["metadata"]["cv_skills"]
    assert "AWS" in result["metadata"]["job_requirements"]
    assert result["metadata"]["skill_match_score"] == 50


# ============================================================
# TEST: Extract CV skills
# ============================================================

def test_extract_cv_skills(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    state = {
        "cv_text": "Python SQL Docker",
        "retry_count": 0,
        "error": None
    }

    updates = graph._extract_cv_skills(state)

    assert updates["cv_skills"] == ["Python", "SQL", "Docker"]
    assert "error" not in updates or updates["error"] is None


# ============================================================
# TEST: Extract job requirements
# ============================================================

def test_extract_job_requirements(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    state = {
        "job_text": "Se requiere Python y AWS"
    }

    updates = graph._extract_job_requirements(state)

    assert updates["job_requirements"] == ["Python", "AWS"]


# ============================================================
# TEST: Calculate skill match
# ============================================================

def test_calculate_skill_match():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {
        "cv_skills": ["Python", "SQL"],
        "job_requirements": ["Python", "AWS"]
    }

    updates = graph._calculate_skill_match(state)

    assert updates["skill_match_score"] == 50


def test_calculate_skill_match_no_requirements():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {
        "cv_skills": ["Python"],
        "job_requirements": []
    }

    updates = graph._calculate_skill_match(state)

    assert updates["skill_match_score"] == 0


# ============================================================
# TEST: Generate recommendation
# ============================================================

def test_generate_recommendation(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    state = {
        "cv_text": "CV text",
        "job_text": "Job text",
        "job_name": "Backend Developer",
        "cv_skills": ["Python"],
        "job_requirements": ["Python"],
        "skill_match_score": 100
    }

    updates = graph._generate_recommendation(state)

    assert updates["score_final"] == 75
    assert "Buen encaje" in updates["resumen"]
    assert updates["fortalezas"]
    assert updates["debilidades"]


# ============================================================
# TEST: Evaluate quality (LLM-as-a-judge)
# ============================================================

def test_evaluate_quality(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    state = {
        "cv_text": "CV",
        "job_text": "JOB",
        "score_final": 70,
        "resumen": "Correcto",
        "fortalezas": [],
        "debilidades": []
    }

    updates = graph._evaluate_quality(state)

    assert updates["llm_evaluation_score"] == 8


def test_evaluate_quality_failure(fake_llm_provider, monkeypatch):
    graph = CVAnalysisGraph(fake_llm_provider)

    def raise_error(*args, **kwargs):
        raise RuntimeError("LLM judge failed")

    fake_llm_provider.evaluate_recommendation = raise_error

    state = {
        "cv_text": "CV",
        "job_text": "JOB",
        "score_final": 70,
        "resumen": "Correcto",
        "fortalezas": [],
        "debilidades": []
    }

    updates = graph._evaluate_quality(state)

    assert updates["llm_evaluation_score"] is None


# ============================================================
# TEST: Error handling node
# ============================================================

def test_handle_error():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {
        "error": "Fallo crítico"
    }

    updates = graph._handle_error(state)

    assert updates["score_final"] == 0
    assert "Fallo crítico" in updates["resumen"]
    assert updates["fortalezas"] == []
    assert updates["debilidades"]


# ============================================================
# TEST: Retry logic
# ============================================================

def test_should_retry_continue():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {"error": None}
    assert graph._should_retry(state) == "continue"


def test_should_retry_retry():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {"error": "Error", "retry_count": 1}
    assert graph._should_retry(state) == "retry"


def test_should_retry_error():
    graph = CVAnalysisGraph(llm_provider=None)

    state = {"error": "Error", "retry_count": 3}
    assert graph._should_retry(state) == "error"


# ============================================================
# TEST: JSON malformed from LLM (robust parsing)
# ============================================================

def test_extract_cv_skills_malformed_json(fake_llm_provider):
    graph = CVAnalysisGraph(fake_llm_provider)

    def malformed_response(prompt: str):
        return """
        ```json
        { "skills": ["Python", "SQL"] }
        ```
        """

    fake_llm_provider._generate_content = malformed_response

    state = {
        "cv_text": "Python SQL",
        "retry_count": 0,
        "error": None
    }

    updates = graph._extract_cv_skills(state)

    assert updates["cv_skills"] == ["Python", "SQL"]
