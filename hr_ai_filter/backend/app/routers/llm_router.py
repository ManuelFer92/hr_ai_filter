# ============================================================
# llm_router.py — LLM Provider & Model Configuration Endpoints
# ============================================================

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import os
import requests

from ..llm_providers import GeminiProvider, OllamaProvider

router = APIRouter()

# Available models per provider
AVAILABLE_MODELS = {
    "gemini": ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash"],
    "ollama": ["gemma2:2b", "llama3.1:8b", "mistral:7b"]
}

# Ollama API URL
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


class ProviderConfig(BaseModel):
    provider: Literal["gemini", "ollama"]
    model: Optional[str] = None  # If not provided, uses first available


def get_ollama_models() -> list[str]:
    """Get list of models currently installed in Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if resp.ok:
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def pull_ollama_model(model_name: str) -> dict:
    """Pull an Ollama model. Returns status."""
    try:
        print(f"📥 Pulling Ollama model: {model_name}...")
        resp = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json={"name": model_name, "stream": False},
            timeout=600  # 10 minutes for large models
        )
        if resp.ok:
            print(f"✅ Model {model_name} pulled successfully")
            return {"status": "success", "message": f"Model {model_name} pulled"}
        else:
            return {"status": "error", "message": resp.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/config")
async def get_llm_config(request: Request):
    """Get current LLM provider and model configuration."""
    llm_service = request.app.state.llm_service
    
    # Check which providers are available
    gemini_available = bool(os.getenv("GOOGLE_API_KEY"))
    ollama_available = True  # Always available if Ollama is running
    
    # Get installed Ollama models
    installed_ollama = get_ollama_models()
    
    return {
        "current_provider": llm_service.provider.provider_name,
        "current_model": llm_service.provider.model_name,
        "available_providers": {
            "gemini": {
                "available": gemini_available,
                "reason": None if gemini_available else "GOOGLE_API_KEY not set",
                "models": AVAILABLE_MODELS["gemini"]
            },
            "ollama": {
                "available": ollama_available,
                "reason": None,
                "models": AVAILABLE_MODELS["ollama"],
                "installed_models": installed_ollama
            }
        }
    }


@router.post("/switch")
async def switch_provider(request: Request, config: ProviderConfig):
    """Switch LLM provider and/or model dynamically.
    
    For Ollama models: if the model is not installed, it will be pulled automatically.
    """
    
    provider_name = config.provider.lower()
    model_name = config.model
    
    # Default model if not specified
    if not model_name:
        model_name = AVAILABLE_MODELS[provider_name][0]
    
    try:
        if provider_name == "gemini":
            if not os.getenv("GOOGLE_API_KEY"):
                raise HTTPException(
                    status_code=400,
                    detail="GOOGLE_API_KEY not configured in .env"
                )
            os.environ["LLM_MODEL"] = model_name
            new_provider = GeminiProvider()
            
        elif provider_name == "ollama":
            # Check if model is installed, if not, pull it
            installed = get_ollama_models()
            if model_name not in installed:
                print(f"⚠️ Model {model_name} not installed, pulling...")
                pull_result = pull_ollama_model(model_name)
                if pull_result["status"] != "success":
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to pull model: {pull_result['message']}"
                    )
            
            os.environ["LLM_MODEL"] = model_name
            new_provider = OllamaProvider()
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {provider_name}"
            )
        
        # Replace the provider in the LLM service
        request.app.state.llm_service._provider = new_provider
        
        return {
            "status": "success",
            "message": f"Switched to {provider_name}/{model_name}",
            "provider": new_provider.provider_name,
            "model": new_provider.model_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to switch: {str(e)}"
        )


@router.get("/models/{provider}")
async def list_models(provider: str):
    """List available models for a provider."""
    provider = provider.lower()
    if provider not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    
    result = {"provider": provider, "models": AVAILABLE_MODELS[provider]}
    
    if provider == "ollama":
        result["installed"] = get_ollama_models()
    
    return result