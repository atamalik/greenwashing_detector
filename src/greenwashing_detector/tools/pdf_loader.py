# src/greenwashing_detector/tools/pdf_loader.py

from crewai.tools import BaseTool
from PyPDF2 import PdfReader
import os

class PDFReportReader(BaseTool):
    name = "PDFReportReader"
    description = "Extracts raw text from a given sustainability PDF report."

    def __call__(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text[:15000]  # Return first 15k chars to stay within token limit
        except Exception as e:
            return f"Failed to read PDF: {str(e)}"
