# ============================================
# job_router.py — Lista Jobs + Análisis LLM
# ============================================

from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.get("/list")
async def list_jobs(request: Request):
    job_service = request.app.state.job_service
    return {"jobs": job_service.list_jobs()}

@router.post("/analyze")
async def analyze_job(request: Request, payload: dict):
    llm_service = request.app.state.llm_service

    cv_text = payload.get("cv_text")
    job_text = payload.get("job_text")
    job_name = payload.get("job_name")

    if not cv_text or not job_text:
        raise HTTPException(status_code=400, detail="Faltan datos para análisis")

    return llm_service.compare(cv_text, job_text, job_name)
