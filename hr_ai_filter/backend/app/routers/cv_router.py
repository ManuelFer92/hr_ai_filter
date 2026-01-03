# ============================================================
# cv_router.py — Subida y procesamiento de CV (solo texto)
# ============================================================

from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter()


@router.post("/upload")
async def upload_cv(request: Request, file: UploadFile = File(...)):
    """
    Sube un CV en PDF, extrae su texto y lo devuelve.
    No genera embeddings.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Solo se admiten archivos PDF."
        )

    cv_service = request.app.state.cv_service

    file_bytes = await file.read()
    result = cv_service.process_cv(file.filename, file_bytes)

    return {
        "filename": file.filename,
        "text": result["text"],
        "paths": result["paths"],
    }
