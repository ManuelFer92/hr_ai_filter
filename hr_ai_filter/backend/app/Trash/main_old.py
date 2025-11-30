# ============================================================
# main.py — Inicialización del Backend FastAPI
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.cv_router_old import router as cv_router
from .routers.job_router_old import router as job_router

from .services.cv_service_old import CVService
from .services.job_service_old import JobService
from .services.llm_service_old import LLMService


def create_app():
    print("🔍 Inicializando backend…")

    app = FastAPI(title="HR AI Filter API", version="1.0")

    # Servicios globales
    app.state.cv_service = CVService()
    app.state.job_service = JobService()
    app.state.llm_service = LLMService()

    # Routers
    app.include_router(cv_router, prefix="/cv", tags=["CV"])
    app.include_router(job_router, prefix="/jobs", tags=["Jobs"])

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.on_event("startup")
    def startup_event():
        job_service = app.state.job_service
        print(f"✔ Jobs procesados: {len(job_service.jobs)}")

    return app


app = create_app()
