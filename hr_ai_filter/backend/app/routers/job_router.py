from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ============================================================
# MODELO DE REQUEST
# ============================================================

class AnalyzeRequest(BaseModel):
    cv_text: str
    job_text: str
    job_name: str
    cv_filename: str  # 👈 NUEVO (trazabilidad MLflow)

# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/list")
async def list_jobs(request: Request):
    job_service = request.app.state.job_service
    return job_service.list_jobs()


@router.post("/analyze")
async def analyze_cv(request: Request, body: AnalyzeRequest):

    job_service = request.app.state.job_service
    llm_service = request.app.state.llm_service

    # ---------------------------
    # Validar Job
    # ---------------------------
    job = job_service.get_job_by_name(body.job_name)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    # ---------------------------
    # Ejecutar análisis con el LLM
    # ---------------------------
    llm_response = llm_service.compare(
        cv_text=body.cv_text,
        job_text=body.job_text,
        job_name=body.job_name,
        cv_filename=body.cv_filename
    )

    return llm_response
