from fastapi import APIRouter
from pydantic import BaseModel
from hr_ai_filter.hr_ai_filter.backend.app.services.llm_nousar import LLMService

router = APIRouter(prefix="/llm", tags=["LLM"])

llm = LLMService()

class LLMRequest(BaseModel):
    text: str

@router.post("/ask")
def ask_llm(request: LLMRequest):
    return llm.analyze_text(request.text)
