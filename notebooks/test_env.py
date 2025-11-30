"""
Script de verificación del entorno para tu proyecto hr_ai_filter.

Comprueba:
- Torch (CPU/GPU)
- Sentence-Transformers (embeddings)
- Transformers (modelo HF)
- Ollama (cliente)
- FastAPI / Pydantic / Uvicorn
- MLflow
- PDF reading
"""

print("\n==============================")
print("🔍 TEST 1 — Torch")
print("==============================")
try:
    import torch
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
except Exception as e:
    print("ERROR en torch:", e)


print("\n==============================")
print("🔍 TEST 2 — Sentence Transformers")
print("==============================")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode("Hello world!")
    print("Embedding generado correctamente, shape:", emb.shape)
except Exception as e:
    print("ERROR en sentence-transformers:", e)


print("\n==============================")
print("🔍 TEST 3 — Transformers (HuggingFace)")
print("==============================")
try:
    from transformers import AutoTokenizer, AutoModel
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = AutoModel.from_pretrained("distilbert-base-uncased")
    print("Transformers funcionando correctamente")
except Exception as e:
    print("ERROR en transformers:", e)


print("\n==============================")
print("🔍 TEST 4 — Ollama Client")
print("==============================")
try:
    from ollama import Client
    client = Client()
    print("Ollama client importado correctamente (requiere daemon para prueba real)")
except Exception as e:
    print("ERROR en ollama:", e)


print("\n==============================")
print("🔍 TEST 5 — FastAPI imports")
print("==============================")
try:
    from fastapi import FastAPI
    import uvicorn
    print("FastAPI + Uvicorn importados correctamente")
except Exception as e:
    print("ERROR en FastAPI o uvicorn:", e)


print("\n==============================")
print("🔍 TEST 6 — MLflow")
print("==============================")
try:
    import mlflow
    print("MLflow version:", mlflow.__version__)
except Exception as e:
    print("ERROR en MLflow:", e)


print("\n==============================")
print("🔍 TEST 7 — PDF lectura")
print("==============================")
try:
    import pdfplumber
    print("pdfplumber importado correctamente")
except Exception as e:
    print("ERROR en pdfplumber:", e)


print("\n==============================")
print("🎉 RESULTADO FINAL")
print("==============================")
print("Si no viste errores en rojo, TU ENTORNO ESTÁ LISTO 🎯")
