# ============================================================
# text_utils.py — Limpieza de texto
# ============================================================

import re


def clean_text(text: str) -> str:
    """
    Limpia el texto extraído del PDF:
    - elimina saltos de línea repetidos
    - elimina espacios múltiples
    - elimina caracteres raros
    - trim final
    """
    if not text or not isinstance(text, str):
        return ""

    # Quitar caracteres muy raros o no imprimibles
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Reemplazar saltos de línea múltiples por uno solo (dejando dobles como párrafos)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Quitar espacios múltiples
    text = re.sub(r" +", " ", text)

    # Quitar tabs
    text = text.replace("\t", " ")

    # Strip final
    text = text.strip()

    return text
