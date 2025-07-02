#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from greenwashing_detector.crew import GreenwashingDetector

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
# src/greenwashing_detector/main.py

def run_greenwashing_crew(pdf_path: str) -> str:
    detector = GreenwashingDetector()
    crew = detector.crew()  # Get the crew instance
    return crew.kickoff(inputs={"file_path": pdf_path})

if __name__ == "__main__":
    result = run_greenwashing_crew("path/to/local/file.pdf")
    print(result)

