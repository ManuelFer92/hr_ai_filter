# ============================================
# cv_router.py — Upload y procesamiento de CVs
# ============================================

from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter()

@router.post("/upload")
async def upload_cv(request: Request, file: UploadFile = File(...)):
    cv_service = request.app.state.cv_service

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    file_bytes = await file.read()
    filename = file.filename.replace(".pdf", "")

    result = cv_service.process_cv(filename, file_bytes)

    return {
        "text": result["text"],
        "embedding": result["embedding"],
        "txt_path": result["paths"]["txt"],
        "embeddings_path": result["paths"]["json"]
    }
