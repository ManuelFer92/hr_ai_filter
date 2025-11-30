# ============================================================
# main.py — Backend FastAPI original (sin evaluaciones JSON)
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.cv_router import router as cv_router
from .routers.job_router import router as job_router

from .services.cv_service import CVService
from .services.job_service import JobService
from .services.llm_service import LLMService


def create_app() -> FastAPI:
    print("🚀 Iniciando servicios...")

    app = FastAPI(
        title="HR AI Filter API",
        version="1.0",
        description="Backend del sistema HR AI Filter (FastAPI + OCR + LLM)."
    )

    # Servicios globales
    app.state.cv_service = CVService()
    app.state.job_service = JobService()
    app.state.llm_service = LLMService()

    # Routers
    app.include_router(cv_router, prefix="/cv", tags=["CV"])
    app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

    # Permitir acceso desde Streamlit
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup_event():
        job_service = app.state.job_service
        print(f"✔ Jobs cargados: {len(job_service.jobs)}")

    print("🟢 Servicios inicializados correctamente.")
    return app


app = create_app()
