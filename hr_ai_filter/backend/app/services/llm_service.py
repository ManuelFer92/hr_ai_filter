import os
from .job_service import JobService  # Keeping imports if needed
from ..llm_providers.ollama_provider import OllamaProvider
from ..llm_providers.gemini_provider import GeminiProvider

class LLMService:
    def __init__(self):
        self.provider_name = os.environ.get("LLM_PROVIDER", "ollama").lower()
        self.model_name = os.environ.get("LLM_MODEL", "llama3.1:8b")
        
        print(f"🔄 Initializing LLM Provider: {self.provider_name}")

        if self.provider_name == "gemini":
            self.provider = GeminiProvider(model=self.model_name)
        else:
            # Default to Ollama
            self.provider = OllamaProvider(model=self.model_name)

    def compare(self, cv_text, job_text, job_name):
        return self.provider.compare(cv_text, job_text, job_name)
