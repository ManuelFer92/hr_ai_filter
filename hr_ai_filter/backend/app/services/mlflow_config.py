# backend/app/services/mlflow_config.py
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("hr_ai_filter_llm")
