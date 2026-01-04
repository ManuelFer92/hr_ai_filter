# ============================================================
# cv_router.py — Subida y procesamiento de CV (solo texto)
# ============================================================

import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter()

# CV storage directory
CV_DIR = Path("/app/data/cvs")
CV_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/list")
def list_cvs():
    """
    Lista todos los CVs disponibles en el directorio.
    """
    try:
        cv_files = []
        if CV_DIR.exists():
            for file in CV_DIR.glob("*.pdf"):
                cv_files.append({
                    "filename": file.name,
                    "size": file.stat().st_size,
                })
        return {
            "count": len(cv_files),
            "cvs": sorted(cv_files, key=lambda x: x["filename"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")


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

    # Save file to CV directory
    cv_path = CV_DIR / file.filename
    with open(cv_path, "wb") as f:
        f.write(file_bytes)

    return {
        "filename": file.filename,
        "text": result["text"],
        "paths": result["paths"],
        "saved_to": str(cv_path),
    }
