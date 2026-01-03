# HR AI Filter - Detailed Roadmap

## Current State ✅
- **Multi-LLM Support**: Switch between Gemini/Ollama via `.env`
- **Infrastructure**: 7 services working (Postgres, Chroma, MLflow, etc)
- **Basic Flow**: Upload CV → LLM Evaluation → Score

---

## Phase 1: Infrastructure ✅ COMPLETE
- [x] Docker Compose with services
- [x] PostgreSQL + pgAdmin (UI on :5050)
- [x] ChromaDB (API on :8585)
- [x] MLflow (UI on :5000)
- [x] Ollama with auto-model download
- [x] Backend (FastAPI) + Frontend (Streamlit)

## Phase 2: LLM Provider Layer ✅ COMPLETE
- [x] **Provider Abstraction**: `LLMProvider` base class
- [x] **Gemini Provider**: Integrated `google-generativeai` (JSON mode)
- [x] **Ollama Provider**: Integrated with auto-pull
- [x] **Factory**: `LLMService` selects provider from `.env`

---

## Phase 3: MLflow Tracking & Metrics (Next Steps)
**Goal:** Compare model performance (Gemini vs Ollama)

- [ ] **MLflow Service Integration**:
  - **Component**: `hr_mlflow` container (Port 5000)
  - **Action**: In `routers/job_router.py`, after LLM responds:
    - `mlflow.log_metric("response_time_ms", time)`
    - `mlflow.log_metric("score_final", score)`
    - `mlflow.log_param("provider", "gemini/ollama")`
    - `mlflow.log_param("model", "gemini-1.5-flash")`
- [ ] **KPI Dashboard**: Verify charts in http://localhost:5000

---

## Phase 4: Structured Extraction (Scoring Engine)

### 4.1 CV Extractor Service
- [ ] **Input**: Raw PDF Text
- [ ] **Action**: LLM extracts structured JSON
- [ ] **Storage (PostgreSQL)**:
  - Table: `cvs`
  - Columns: `id`, `name`, `email`, `skills` (JSONB), `experience_years`

### 4.2 Matching Engine & Semantic Search
- [ ] **Embeddings Generation**:
  - Use `sentence-transformers` to turn CV Summary → Vector
- [ ] **Storage (ChromaDB)**:
  - **Component**: `hr_chroma` container (Port 8585)
  - **Collection**: `cv_embeddings`
  - **Action**: Store `[vector, cv_id]` for fast retrieval
- [ ] **Scoring Logic**:
  - **Skills (40%)**: Python logic (set intersection)
  - **Experience (30%)**: Python logic (numeric comparison)
  - **Cultural Fit (30%)**: **ChromaDB Query** (Cosine similarity of CV vector vs Job Description vector)
- [ ] **Persist Results (PostgreSQL)**:
  - Table: `evaluations`
  - Data: `job_id`, `cv_id`, `total_score`, `breakdown_json`

---

## Phase 5: Batch Processing & Export
- [ ] **Batch Flow**:
  1. Frontend sends list of files
  2. Backend iterates:
     - Extract -> PostgreSQL
     - Embed -> ChromaDB
     - Match -> PostgreSQL
  3. UI polls for progress
- [ ] **Export**: Query PostgreSQL `evaluations` table -> Generate Excel

### Optional Improvements (Bonus)
- [ ] **Async Task Queue**: Use FastAPI `BackgroundTasks` or Celery/Redis for processing large batches of CVs without blocking the UI.

---

## Phase 6: LangGraph & Advanced Pipelines
- [ ] **Orchestration**: Replaces linear Python function calls
- [ ] **Nodes**:
  - `ReaderNode` (PDF -> Text)
  - `ExtractorNode` (Text -> JSON -> **PostgreSQL**)
  - `EmbeddingNode` (JSON -> Vector -> **ChromaDB**)
  - `MatchingNode` (Vector + Metadata -> Score -> **PostgreSQL**)

---

## Component Usage Summary

| Component | Role | When is it used? |
|-----------|------|------------------|
| **PostgreSQL** | Primary DB | Storing Job descriptions, parsed CV data, and final Evaluation results. |
| **ChromaDB** | Vector DB | Storing embeddings of CV summaries for "Cultural Fit" semantic search. |
| **MLflow** | MLOps | Logging every LLM call's latency, token usage, and quality score for model comparison. |
| **Ollama/Gemini** | Intelligence | Parsing unstructured text and generating summaries/explanations. |
