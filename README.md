# HR AI Filter

AI-powered CV filtering system using LLMs, embeddings, and MLOps.

## 🚀 Quick Start

```bash
# 1. Setup
cp .env.example .env
# Edit .env: Set GOOGLE_API_KEY and choose provider (gemini or ollama)

# 2. Start services
docker compose up -d

# 3. Add job descriptions
# Place PDF files in: data/jobs/jobs_pdf/

# 4. Restart backend to load jobs
docker compose restart backend

# 5. Open UI
# http://localhost:8501
```

## 🐳 Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 8501 | Streamlit UI (Wizard) |
| Backend | 8000 | FastAPI + Swagger |
| MLflow | 5000 | Experiment Tracking |
| pgAdmin | 5050 | PostgreSQL UI (admin@example.com / admin) |
| PostgreSQL | 5432 | Database |
| ChromaDB | 8585 | Vector DB API |
| Ollama | 11435 | Local LLM API |

## 🔧 Configuration (.env)

Switch between **Gemini** (Cloud, Fast) and **Ollama** (Local, Private):

```bash
# Option 1: Gemini (Recommended for dev)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=your_key

# Option 2: Ollama (Local)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
# Model auto-downloads on startup
```

## 📁 Project Structure

```
hr_ai_filter/
├── docker-compose.yml       # 7 services
├── data/                    # Volume data (jobs, DBs)
├── hr_ai_filter/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── llm_providers/   # LLM Abstraction
│   │   │   ├── services/        # Logic (CV, Job, LLM)
│   │   │   └── routers/         # API Endpoints
│   └── frontend/                # Streamlit App
└── TODO.md                  # Detailed Roadmap
```

## 📋 Features & Architecture

### Key Features
- **Multi-LLM Support**: Seamlessly switch between Gemini (Cloud) and Ollama (Local).
- **Auto-Infrastructure**: 7 containerized services (DB, MLOps, Vector Store).
- **Job Parsing**: Automatically loads PDF job descriptions on startup.
- **Smart Evaluation**: LLM analysis of CV vs Job with scoring.

### 🏗 Architecture Highlights
- **Hybrid Storage**: Combines **PostgreSQL** (structured data) + **ChromaDB** (vector embeddings) for optimal data handling.
- **MLOps Integrated**: **MLflow** included from day one to track model performance and KPIs.
- **Provider Abstraction**: Factory pattern allows plugging in new LLMs without changing business logic.
- **Scalable Design**: Ready for asynchronous batch processing and complex pipelines (LangGraph).

## License
MIT
