# ============================================================
# cv_analysis_graph.py — LangGraph Workflow for CV Analysis
# ============================================================

from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import mlflow
import time


class CVAnalysisState(TypedDict):
    """State passed through the graph nodes."""
    # Inputs
    cv_text: str
    job_text: str
    job_name: str
    cv_filename: str
    
    # Intermediate results
    cv_skills: Optional[list[str]]
    job_requirements: Optional[list[str]]
    skill_match_score: Optional[int]
    
    # Final results
    score_final: Optional[int]
    resumen: Optional[str]
    fortalezas: Optional[list[str]]
    debilidades: Optional[list[str]]
    llm_evaluation_score: Optional[int]
    
    # Metadata
    error: Optional[str]
    retry_count: int


class CVAnalysisGraph:
    """
    LangGraph workflow for CV analysis.
    
    Graph structure:
    START → extract_cv_skills → extract_job_requirements → 
    calculate_skill_match → generate_recommendation → 
    evaluate_quality → END
    """
    
    def __init__(self, llm_provider, use_checkpointing: bool = False):
        self.llm_provider = llm_provider
        self.use_checkpointing = use_checkpointing
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the analysis workflow graph."""
        
        workflow = StateGraph(CVAnalysisState)
        
        # Add nodes
        workflow.add_node("extract_cv_skills", self._extract_cv_skills)
        workflow.add_node("extract_job_requirements", self._extract_job_requirements)
        workflow.add_node("calculate_skill_match", self._calculate_skill_match)
        workflow.add_node("generate_recommendation", self._generate_recommendation)
        workflow.add_node("evaluate_quality", self._evaluate_quality)
        workflow.add_node("handle_error", self._handle_error)
        
        # Define edges
        workflow.set_entry_point("extract_cv_skills")
        
        workflow.add_edge("extract_cv_skills", "extract_job_requirements")
        workflow.add_edge("extract_job_requirements", "calculate_skill_match")
        workflow.add_edge("calculate_skill_match", "generate_recommendation")
        workflow.add_edge("generate_recommendation", "evaluate_quality")
        workflow.add_edge("evaluate_quality", END)
        
        # Conditional edge for error handling
        workflow.add_conditional_edges(
            "extract_cv_skills",
            self._should_retry,
            {
                "retry": "extract_cv_skills",
                "error": "handle_error",
                "continue": "extract_job_requirements"
            }
        )
        
        # Compile WITHOUT checkpointer for simpler use case
        # If you need persistence, uncomment the checkpointer line
        # Compile with or without checkpointing
        if self.use_checkpointing:
            return workflow.compile(checkpointer=MemorySaver())
        else:
            return workflow.compile()
    
    def _should_retry(self, state: CVAnalysisState) -> str:
        """Decide whether to retry or continue."""
        error = state.get("error")
        
        # No error means success, continue
        if not error:
            return "continue"
        
        # Check retry count
        retry_count = state.get("retry_count", 0)
        
        if retry_count < 3:
            print(f"⚠️ Retry attempt {retry_count + 1}/3 due to: {error}")
            return "retry"
        else:
            print(f"❌ Max retries reached. Last error: {error}")
            return "error"
    
    # ============================================================
    # NODE: Extract CV Skills
    # ============================================================
    
    def _extract_cv_skills(self, state: CVAnalysisState) -> dict:
        """Extract key skills from CV."""
        print("📊 [Node] Extracting CV skills...")
        
        updates = {}
        
        try:
            prompt = f"""
Analiza el siguiente CV y extrae las habilidades técnicas y profesionales clave.
Devuelve SOLO un JSON con esta estructura:
{{
  "skills": ["skill1", "skill2", ...]
}}

CV:
{state['cv_text'][:3000]}  # Limit to avoid token overflow
"""
            
            # Support both Gemini and Ollama
            if hasattr(self.llm_provider, '_model'):
                # Gemini provider
                import google.generativeai as genai
                response = self.llm_provider._model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                raw_text = response.text
            else:
                # Ollama provider
                raw_text = self.llm_provider._generate_content(prompt)
            
            # Parse JSON with better error handling
            import json
            import re
            
            try:
                result = json.loads(raw_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks or text
                json_match = re.search(r'\{[\s\S]*\}', raw_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {raw_text[:200]}")
            
            updates["cv_skills"] = result.get("skills", [])
            
            # Only clear error if we successfully processed
            if "error" in state and state["error"]:
                updates["error"] = None
            
            mlflow.log_metric("cv_skills_count", len(updates["cv_skills"]))
            
        except Exception as e:
            error_msg = f"Error extracting CV skills: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Only update error if it's a new error
            if state.get("error") != error_msg:
                updates["error"] = error_msg
                updates["retry_count"] = state.get("retry_count", 0) + 1
        
        return updates
    
    # ============================================================
    # NODE: Extract Job Requirements
    # ============================================================
    
    def _extract_job_requirements(self, state: CVAnalysisState) -> dict:
        """Extract required skills from job description."""
        print("📋 [Node] Extracting job requirements...")
        
        updates = {}
        
        try:
            prompt = f"""
Analiza la siguiente descripción de trabajo y extrae los requisitos clave.
Devuelve SOLO un JSON con esta estructura:
{{
  "requirements": ["req1", "req2", ...]
}}

JOB:
{state['job_text'][:3000]}
"""
            
            # Support both Gemini and Ollama
            if hasattr(self.llm_provider, '_model'):
                import google.generativeai as genai
                response = self.llm_provider._model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                raw_text = response.text
            else:
                raw_text = self.llm_provider._generate_content(prompt)
            
            # Parse JSON with better error handling
            import json
            import re
            
            try:
                result = json.loads(raw_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{[\s\S]*\}', raw_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {raw_text[:200]}")
            
            updates["job_requirements"] = result.get("requirements", [])
            
            mlflow.log_metric("job_requirements_count", len(updates["job_requirements"]))
            
        except Exception as e:
            error_msg = f"Error extracting job requirements: {str(e)}"
            print(f"❌ {error_msg}")
            
            if state.get("error") != error_msg:
                updates["error"] = error_msg
        
        return updates
    
    # ============================================================
    # NODE: Calculate Skill Match
    # ============================================================
    
    def _calculate_skill_match(self, state: CVAnalysisState) -> dict:
        """Calculate skill match percentage."""
        print("🎯 [Node] Calculating skill match...")
        
        updates = {}
        
        cv_skills = set([s.lower() for s in state.get("cv_skills", [])])
        job_reqs = set([r.lower() for r in state.get("job_requirements", [])])
        
        if not job_reqs:
            updates["skill_match_score"] = 0
            return updates
        
        # Calculate overlap
        matched = cv_skills.intersection(job_reqs)
        match_score = int((len(matched) / len(job_reqs)) * 100)
        
        updates["skill_match_score"] = match_score
        
        mlflow.log_metric("skill_match_score", match_score)
        mlflow.log_metric("matched_skills_count", len(matched))
        
        return updates
    
    # ============================================================
    # NODE: Generate Recommendation
    # ============================================================
    
    def _generate_recommendation(self, state: CVAnalysisState) -> dict:
        """Generate final recommendation using LLM."""
        print("🤖 [Node] Generating recommendation...")
        
        updates = {}
        
        try:
            # Use the original compare logic but with enhanced context
            prompt = f"""
Eres un experto en selección de personal. Evalúa este CV contra el puesto: {state['job_name']}

CONTEXTO ADICIONAL:
- Skills del CV: {', '.join(state.get('cv_skills', [])[:10])}
- Requisitos del puesto: {', '.join(state.get('job_requirements', [])[:10])}
- Match de skills calculado: {state.get('skill_match_score', 0)}%

Devuelve SOLO este JSON:
{{
  "score_final": 0-100,
  "resumen": "texto descriptivo",
  "fortalezas": ["fortaleza 1", "fortaleza 2"],
  "debilidades": ["debilidad 1", "debilidad 2"]
}}

CV:
{state['cv_text'][:4000]}

JOB:
{state['job_text'][:4000]}
"""
            
            # Support both Gemini and Ollama
            if hasattr(self.llm_provider, '_model'):
                import google.generativeai as genai
                response = self.llm_provider._model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                raw_text = response.text
            else:
                raw_text = self.llm_provider._generate_content(prompt)
            
            # Parse JSON with better error handling
            import json
            import re
            
            try:
                result = json.loads(raw_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{[\s\S]*\}', raw_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {raw_text[:200]}")
            
            updates["score_final"] = result.get("score_final")
            updates["resumen"] = result.get("resumen")
            updates["fortalezas"] = result.get("fortalezas", [])
            updates["debilidades"] = result.get("debilidades", [])
            
            mlflow.log_metric("score_final", updates["score_final"])
            mlflow.log_metric("fortalezas_count", len(updates["fortalezas"]))
            mlflow.log_metric("debilidades_count", len(updates["debilidades"]))
            
        except Exception as e:
            error_msg = f"Error generating recommendation: {str(e)}"
            print(f"❌ {error_msg}")
            
            if state.get("error") != error_msg:
                updates["error"] = error_msg
        
        return updates
    
    # ============================================================
    # NODE: Evaluate Quality
    # ============================================================
    
    def _evaluate_quality(self, state: CVAnalysisState) -> dict:
        """Evaluate recommendation quality (LLM-as-a-judge)."""
        print("⚖️ [Node] Evaluating quality...")
        
        updates = {}
        
        try:
            eval_score = self.llm_provider.evaluate_recommendation(
                cv_text=state["cv_text"],
                job_text=state["job_text"],
                llm_result={
                    "score_final": state["score_final"],
                    "resumen": state["resumen"],
                    "fortalezas": state["fortalezas"],
                    "debilidades": state["debilidades"]
                }
            )
            
            updates["llm_evaluation_score"] = eval_score
            
            if eval_score:
                mlflow.log_metric("llm_evaluation_score", eval_score)
            
        except Exception as e:
            print(f"⚠️ Warning: Quality evaluation failed: {e}")
            updates["llm_evaluation_score"] = None
        
        return updates
    
    # ============================================================
    # NODE: Handle Error
    # ============================================================
    
    def _handle_error(self, state: CVAnalysisState) -> dict:
        """Handle errors gracefully."""
        print(f"⚠️ [Node] Handling error: {state.get('error')}")
        
        # Return a safe default response with only the updates
        return {
            "score_final": 0,
            "resumen": f"Error en el análisis: {state.get('error')}",
            "fortalezas": [],
            "debilidades": ["Error en el procesamiento"]
        }
    
    # ============================================================
    # PUBLIC API
    # ============================================================
    
    def analyze(
        self,
        cv_text: str,
        job_text: str,
        job_name: str,
        cv_filename: str
    ) -> dict:
        """
        Run the complete CV analysis workflow.
        
        Returns:
            dict: Analysis results with scores and recommendations
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting CV Analysis Graph")
        print(f"   CV: {cv_filename}")
        print(f"   Job: {job_name}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Initialize state
        initial_state = {
            "cv_text": cv_text,
            "job_text": job_text,
            "job_name": job_name,
            "cv_filename": cv_filename,
            "retry_count": 0,
            "cv_skills": None,
            "job_requirements": None,
            "skill_match_score": None,
            "score_final": None,
            "resumen": None,
            "fortalezas": None,
            "debilidades": None,
            "llm_evaluation_score": None,
            "error": None
        }
        
        # Run graph
        with mlflow.start_run(run_name=f"graph_eval_{job_name}"):
            # Log initial params
            mlflow.log_param("job_name", job_name)
            mlflow.log_param("cv_filename", cv_filename)
            mlflow.set_tag("workflow", "langgraph")
            mlflow.set_tag("llm_provider", self.llm_provider.provider_name)
            mlflow.set_tag("llm_model", self.llm_provider.model_name)
            
            # Execute graph
            final_state = self.graph.invoke(initial_state)
            
            # Log execution time
            elapsed = time.time() - start_time
            mlflow.log_metric("total_execution_time_ms", elapsed * 1000)
            
            print(f"\n{'='*60}")
            print(f"✅ Analysis Complete ({elapsed:.2f}s)")
            print(f"   Score: {final_state.get('score_final')}")
            print(f"   Skill Match: {final_state.get('skill_match_score')}%")
            print(f"{'='*60}\n")
        
        # Return clean results
        return {
            "score_final": final_state["score_final"],
            "resumen": final_state["resumen"],
            "fortalezas": final_state["fortalezas"],
            "debilidades": final_state["debilidades"],
            "llm_evaluation_score": final_state.get("llm_evaluation_score"),
            "metadata": {
                "cv_skills": final_state.get("cv_skills", []),
                "job_requirements": final_state.get("job_requirements", []),
                "skill_match_score": final_state.get("skill_match_score"),
                "execution_time_ms": elapsed * 1000
            }
        }