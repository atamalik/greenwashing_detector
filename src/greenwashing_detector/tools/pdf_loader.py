# src/greenwashing_detector/tools/pdf_loader.py

from crewai.tools import BaseTool
from PyPDF2 import PdfReader
import os
from typing import Annotated

class PDFReportReader(BaseTool):
    name: Annotated[str, "PDFReportReader"] = "PDFReportReader"
    description: Annotated[str, "Tool description"] = "Extracts raw text from a given sustainability PDF report."

    def _run(self, file_path: str) -> str:
        """Implementation of the tool's functionality"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text[:15000]  # Return first 15k chars to stay within token limit
        except Exception as e:
            return f"Failed to read PDF: {str(e)}"
