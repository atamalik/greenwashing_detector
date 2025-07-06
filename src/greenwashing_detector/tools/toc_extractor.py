# src/your_project/tools/toc_extractor.py

from typing import Any, Annotated
from crewai.tools import BaseTool
from pydantic import Field
import os
import logging
import requests

class TOCExtractor(BaseTool):
    """Tool for extracting the Table of Contents or logical section headers from a report using a local LLM."""

    name: Annotated[str, "TOCExtractor"] = "TOCExtractor"
    description: Annotated[str, "Extracts TOC or section headers from a report using a local LLM like Ollama."] = (
        "Use this tool to extract or infer the Table of Contents from a sustainability report. "
        "Returns a structured list of section titles (and page hints if possible)."
    )

    endpoint: Annotated[str, "The local LLM endpoint to query"] = Field(default="http://localhost:11434/api/generate")
    model: Annotated[str, "The local model to use"] = Field(default="llama3")
    temperature: Annotated[float, "Sampling temperature for LLM"] = Field(default=0.3)

    def _run(self, chunk: str) -> str:
        prompt = self._build_prompt(chunk)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature,
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()
            output = response.json()["response"]
            return output.strip()

        except Exception as e:
            logging.error(f"❌ TOCExtractor error: {e}")
            return f"Error extracting TOC: {e}"

    def _build_prompt(self, chunk: str) -> str:
        return f"""
You are an expert document analyst.

Analyze the following chunk of a sustainability report. Your goal is to extract a Table of Contents if it's explicitly present. If no TOC is found, infer section headers based on formatting patterns like numbered headers (e.g., 1.1, 2.2.1), bold titles, or all-caps sections.

Only extract high-level sections that reflect ESG-related structure (e.g., “Environmental Goals”, “Stakeholder Engagement”, “GRI Index”, “Sustainability Frameworks”, etc.)

Output a bullet-point list with section titles and page numbers or location hints if available.

Here is the chunk:
===========
{chunk}
===========
""".strip()
