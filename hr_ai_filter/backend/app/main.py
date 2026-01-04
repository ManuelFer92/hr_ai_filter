# ============================================================
# main.py — Backend FastAPI (Docker-safe)
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.cv_router import router as cv_router
from .routers.job_router import router as job_router
from .routers.llm_router import router as llm_router

from .services.cv_service import CVService
from .services.job_service import JobService
from .services.llm_service import LLMService


def create_app() -> FastAPI:
    print("🚀 Creando aplicación FastAPI...")

    app = FastAPI(
        title="HR AI Filter API",
        version="1.0",
        description="Backend del sistema HR AI Filter (FastAPI + NLP + LLM)."
    )

    # --------------------------------------------------------
    # Routers
    # --------------------------------------------------------
    app.include_router(cv_router, prefix="/cv", tags=["CV"])
    app.include_router(job_router, prefix="/jobs", tags=["Jobs"])
    app.include_router(llm_router, prefix="/llm", tags=["LLM"])

    # --------------------------------------------------------
    # Health Check (for Docker)
    # --------------------------------------------------------
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    # --------------------------------------------------------
    # Middleware (CORS)
    # --------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------------------------------------
    # Startup (INICIALIZACIÓN REAL)
    # --------------------------------------------------------
    @app.on_event("startup")
    def startup_event():
        print("🟢 Startup | Inicializando servicios...")

        app.state.cv_service = CVService()
        app.state.job_service = JobService()
        app.state.llm_service = LLMService()

        print(f"🟢 Startup | Jobs cargados: {len(app.state.job_service.jobs)}")

    print("🟢 Aplicación FastAPI creada.")
    return app


# ------------------------------------------------------------
# ASGI entrypoint
# ------------------------------------------------------------
app = create_app()
