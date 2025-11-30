import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
TXT_DIR = os.path.join(DATA_DIR, "processed")
EMB_DIR = os.path.join(DATA_DIR, "embeddings")

# crear carpetas si no existen
for folder in [RAW_DIR, TXT_DIR, EMB_DIR]:
    os.makedirs(folder, exist_ok=True)
