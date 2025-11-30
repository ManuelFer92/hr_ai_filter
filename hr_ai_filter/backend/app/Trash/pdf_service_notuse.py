# import pdfplumber
# import os


# class PDFService:

#     @staticmethod
#     def extract_text(pdf_path: str) -> str:
#         """
#         Extrae texto completo desde un archivo PDF usando pdfplumber.

#         Parámetros
#         ----------
#         pdf_path : str
#             Ruta del archivo PDF.

#         Retorna
#         -------
#         str : Texto extraído del PDF.

#         Lanza
#         -----
#         FileNotFoundError : si el archivo PDF no existe.
#         Exception : si ocurre un error durante la lectura.
#         """

#         if not os.path.exists(pdf_path):
#             raise FileNotFoundError(f"El archivo no existe: {pdf_path}")

#         full_text = []

#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     text = page.extract_text()
#                     if text:
#                         full_text.append(text)
#         except Exception as e:
#             raise Exception(f"Error al leer PDF: {e}")

#         # Unimos todo el texto
#         return "\n".join(full_text)
