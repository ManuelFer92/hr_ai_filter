
# import re


# class TextService:

#     @staticmethod
#     def clean_text(text: str) -> str:
#         """
#         Limpia el texto extraído del PDF:
#         - elimina saltos de línea repetidos
#         - elimina espacios múltiples
#         - elimina caracteres raros
#         - normaliza a ASCII básico cuando es posible
#         - trim final

#         Parámetros
#         ----------
#         text : str
#             Texto crudo proveniente del PDF.

#         Retorna
#         -------
#         str : Texto limpio y normalizado.
#         """

#         if not text or not isinstance(text, str):
#             return ""

#         # Quitar caracteres muy raros o no imprimibles
#         text = re.sub(r"[^\x00-\x7F]+", " ", text)

#         # Reemplazar saltos de línea múltiples por uno solo
#         text = re.sub(r"\n\s*\n+", "\n\n", text)

#         # Quitar espacios múltiples
#         text = re.sub(r" +", " ", text)

#         # Quitar tabs
#         text = text.replace("\t", " ")

#         # Strip final
#         text = text.strip()

#         return text
