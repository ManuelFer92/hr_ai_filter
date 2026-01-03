# ============================================================
# main.py — Backend FastAPI with Docker/MLflow integration
# ============================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.cv_router import router as cv_router
from .routers.job_router import router as job_router

from .services.cv_service import CVService
from .services.job_service import JobService
from .services.llm_service import LLMService


def create_app() -> FastAPI:
    print("🚀 Starting HR AI Filter services...")

    app = FastAPI(
        title="HR AI Filter API",
        version="2.0",
        description="HR AI Filter Backend with MLflow, LangGraph, and multi-LLM support."
    )

    # Global services
    app.state.cv_service = CVService()
    app.state.job_service = JobService()
    app.state.llm_service = LLMService()

    # Routers
    app.include_router(cv_router, prefix="/cv", tags=["CV"])
    app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

    # CORS for Streamlit
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Health"])
    def health_check():
        """Health check endpoint for Docker and load balancers."""
        return {
            "status": "healthy",
            "service": "hr-ai-filter-backend",
            "version": "2.0",
            "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
            "mlflow_uri": os.getenv("MLFLOW_TRACKING_URI", "not configured")
        }

    @app.on_event("startup")
    def startup_event():
        job_service = app.state.job_service
        print(f"✔ Jobs loaded: {len(job_service.jobs)}")
        print(f"✔ LLM Provider: {os.getenv('LLM_PROVIDER', 'ollama')}")
        print(f"✔ MLflow URI: {os.getenv('MLFLOW_TRACKING_URI', 'not configured')}")

    print("🟢 Services initialized successfully.")
    return app


app = create_app()
