from fastapi import APIRouter, UploadFile, File, Request, HTTPException

router = APIRouter()

@router.post("/upload")
async def upload_cv(request: Request, file: UploadFile = File(...)):
    """
    Sube un CV en PDF y devuelve su texto + embedding.
    """
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF.")

    cv_service = request.app.state.cv_service

    file_bytes = await file.read()
    result = cv_service.process_cv(file.filename, file_bytes)

    return {
        "filename": file.filename,
        "text": result["text"],
        "embedding_dim": len(result["embedding"]) if result["embedding"] else 0,
        "paths": result["paths"],
    }
