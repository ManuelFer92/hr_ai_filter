"""
Script de verificación del entorno para hr_ai_filter (LLM-only).

Comprueba:
- Ollama client
- FastAPI / Uvicorn
- MLflow
- Lectura de PDFs
- Requests / HTTP
- Pydantic

NO comprueba embeddings ni modelos locales.
"""

print("\n==============================")
print("🔍 TEST 1 — Ollama Client")
print("==============================")
try:
    from ollama import Client
    client = Client()
    print("✅ Ollama client importado correctamente")
    print("ℹ️ Nota: requiere daemon Ollama activo para pruebas reales")
except Exception as e:
    print("❌ ERROR en Ollama:", e)


print("\n==============================")
print("🔍 TEST 2 — FastAPI / Uvicorn")
print("==============================")
try:
    from fastapi import FastAPI
    import uvicorn
    print("✅ FastAPI y Uvicorn importados correctamente")
except Exception as e:
    print("❌ ERROR en FastAPI o Uvicorn:", e)


print("\n==============================")
print("🔍 TEST 3 — MLflow")
print("==============================")
try:
    import mlflow
    print("✅ MLflow version:", mlflow.__version__)
except Exception as e:
    print("❌ ERROR en MLflow:", e)


print("\n==============================")
print("🔍 TEST 4 — PDF lectura (pdfplumber)")
print("==============================")
try:
    import pdfplumber
    print("✅ pdfplumber importado correctamente")
except Exception as e:
    print("❌ ERROR en pdfplumber:", e)


print("\n==============================")
print("🔍 TEST 5 — Requests (HTTP)")
print("==============================")
try:
    import requests
    print("✅ requests importado correctamente")
except Exception as e:
    print("❌ ERROR en requests:", e)


print("\n==============================")
print("🔍 TEST 6 — Pydantic")
print("==============================")
try:
    import pydantic
    print("✅ Pydantic version:", pydantic.__version__)
except Exception as e:
    print("❌ ERROR en Pydantic:", e)


print("\n==============================")
print("🎉 RESULTADO FINAL")
print("==============================")
print("Si no viste errores, el entorno LLM-only está listo 🚀")
