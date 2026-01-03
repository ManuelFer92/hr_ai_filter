from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def compare(self, cv_text: str, job_text: str, job_name: str) -> dict:
        """
        Compares a CV against a job description.
        Returns a dictionary with score, summary, strengths, and weaknesses.
        """
        pass
