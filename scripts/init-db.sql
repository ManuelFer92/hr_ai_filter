-- HR AI Filter - Database Initialization
-- Creates MLflow tables and application tables

-- MLflow requires these tables (will be auto-created by MLflow, but we ensure DB exists)
-- Application tables for core data

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL,
    description TEXT,
    requirements TEXT,
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    text TEXT,
    embedding_dim INTEGER DEFAULT 0,
    embedding JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    cv_id INTEGER REFERENCES cvs(id),
    job_id INTEGER REFERENCES jobs(id),
    score_final INTEGER,
    resumen TEXT,
    fortalezas JSONB,
    debilidades JSONB,
    provider VARCHAR(50),
    model_name VARCHAR(100),
    response_time_ms INTEGER,
    mlflow_run_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_evaluations_cv_id ON evaluations(cv_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_job_id ON evaluations(job_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_score ON evaluations(score_final DESC);
