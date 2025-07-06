from crewai.tools import BaseTool
from typing import Any, Annotated
from pydantic import Field
import requests


class RelevantSectionExtractor(BaseTool):
    name: Annotated[str, "RelevantSectionExtractor"] = "RelevantSectionExtractor"
    description: Annotated[str, "Tool to extract sections likely related to ESG frameworks based on TOC"] = (
        "This tool selects and extracts the most relevant sections from a sustainability report "
        "that are likely to contain ESG framework mentions like GRI, TCFD, SASB, CDP, etc. "
        "based on the Table of Contents and full report content."
    )

    model_endpoint: Annotated[str, "Local Ollama API endpoint"] = Field(default="http://localhost:11434/api/generate")
    model: Annotated[str, "Ollama model name"] = Field(default="llama3")

    def _run(self, toc: str, full_text: str) -> str:
        prompt = self._build_prompt(toc, full_text)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3
        }

        try:
            response = requests.post(self.model_endpoint, json=payload, timeout=90)
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            return f"❌ Error extracting relevant sections: {e}"

    def _build_prompt(self, toc: str, full_text: str) -> str:
        return f"""
You are an ESG analyst reading a sustainability report.

Here is the TABLE OF CONTENTS:
-------------------------------
{toc}

Here is the FULL TEXT of the report (first part or selected extract):
-------------------------------
{full_text[:4000]}

TASK:
From the full text above and the TOC, extract only the sections that are most likely to contain ESG reporting frameworks.

Frameworks of interest: GRI, SASB, CDP, TCFD, ISO 14064, CSRD, ESRS, IFRS S2, UNGC, SDGs

Focus on TOC headers or paragraphs that mention:
- "reporting methodology"
- "reporting frameworks"
- "GRI Index"
- "ESG Standards"
- "Framework alignment"
- "Sustainability reporting approach"
- "Assurance" or "Verification" (if frameworks are involved)

Return ONLY the relevant paragraphs.

FORMAT:
========
[Section Title]
Extracted paragraph(s)...

========
If nothing relevant is found, say so clearly.
""".strip()
