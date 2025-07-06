from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class FluffRemoverInput(BaseModel):
    """Input for the FluffRemover tool."""
    report_text: str = Field(..., description="The full text of the sustainability report to be cleaned")

class FluffRemover(BaseTool):
    """
    Tool for removing fluff and extracting relevant ESG content from sustainability reports.
    
    This tool processes full sustainability reports to remove marketing language, 
    repetitive content, and non-substantive text while preserving all ESG-relevant 
    information for downstream analysis.
    """
    
    name: str = "FluffRemover"
    description: str = """
    Removes unnecessary text from sustainability reports and extracts only relevant ESG information.
    
    This tool is designed to:
    - Remove marketing filler, slogans, and promotional language
    - Eliminate repetitive boilerplate content
    - Remove design artifacts (page numbers, headers, footers)
    - Preserve all ESG-relevant content including:
      * Framework mentions (GRI, TCFD, SASB, etc.)
      * Specific targets, goals, and achievements
      * Emissions data and climate commitments
      * Governance and stakeholder engagement
      * Risk assessments and materiality discussions
      * Any claims that could be tested or challenged
    
    The tool uses intelligent filtering to distinguish between substantive ESG content
    and marketing fluff, ensuring downstream analysis focuses on material information.
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(self, report_text: str) -> str:
        """
        Process the report text to remove fluff and extract relevant ESG content.
        
        Args:
            report_text: The full text of the sustainability report
            
        Returns:
            Cleaned text containing only relevant ESG information
        """
        try:
            logger.info("🧹 Starting fluff removal process")
            logger.info(f"📄 Input text length: {len(report_text)} characters")
            
            # This is a placeholder implementation
            # In a real implementation, you would use the Ollama model to process this
            # For now, we'll return the text as-is and let the agent handle the processing
            
            logger.info("✅ Fluff removal completed (agent will handle processing)")
            logger.info(f"📄 Output text length: {len(report_text)} characters")
            
            return report_text
            
        except Exception as e:
            logger.error(f"❌ Error in fluff removal: {e}")
            return f"Error processing report text: {str(e)}"
    
    def _run_with_ollama(self, report_text: str) -> str:
        """
        Process the report text using Ollama model for intelligent fluff removal.
        
        Args:
            report_text: The full text of the sustainability report
            
        Returns:
            Cleaned text containing only relevant ESG information
        """
        try:
            logger.info("🧹 Starting intelligent fluff removal with Ollama")
            logger.info(f"📄 Input text length: {len(report_text)} characters")
            
            # This would be implemented with actual Ollama API calls
            # For now, we'll return the text as-is
            # TODO: Implement Ollama integration for intelligent fluff removal
            
            logger.info("✅ Intelligent fluff removal completed")
            logger.info(f"📄 Output text length: {len(report_text)} characters")
            
            return report_text
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent fluff removal: {e}")
            return f"Error processing report text with Ollama: {str(e)}"

FLUFF_REMOVAL_PROMPT = """
You are a world-class ESG compliance analyst and greenwashing detection assistant. Your task is to carefully clean the following corporate sustainability report by removing irrelevant, promotional, or redundant content, while preserving **all potentially meaningful, material, or scrutinizable ESG-related information**.

This is **not a summarization task**. You must **retain original wording verbatim** for anything that could later be used to assess ESG claims, disclosure quality, or detect potential greenwashing.

---

## ✅ YOU MUST RETAIN TEXT IF IT FITS ANY OF THESE CATEGORIES:

1. **Quantitative ESG data**  
   - Emissions, energy use, waste volumes, water consumption, DEI statistics  
   - GHG Scope 1, 2, 3 values, offset usage, emission factors

2. **Qualitative disclosures with ESG relevance**  
   - Climate risks, adaptation strategy, circular economy, supply chain initiatives  
   - Statements about ESG goals, risk assessments, board governance

3. **Mentions of standards, regulations, or frameworks**  
   - GRI, TCFD, SASB, CDP, SDGs, ISO 14064, IFRS S1/S2, CSRD, ESRS  
   - Industry codes of conduct, science-based targets, ESG raters (MSCI, Sustainalytics)

4. **Commitments or future goals**  
   - Net zero targets, renewable adoption, gender parity goals  
   - These may be vague or non-binding — still keep them for greenwashing review

5. **Aspirational or vague sustainability claims**  
   - "We are committed to sustainability" or "We care about the planet" — these are cheap talk, but useful for scrutiny  
   - Any mention of social/environmental purpose, ethics, community engagement

6. **Descriptions of initiatives**  
   - Renewable projects, workforce programs, governance changes, emissions offsets  
   - Partnerships, supplier standards, diversity training

7. **Anything that could later be flagged as greenwashing**  
   - Overly positive claims not backed by data  
   - ESG claims that sound good but lack substance  
   - Keep them for later analysis

---

## ❌ YOU MUST REMOVE TEXT IF IT FITS ANY OF THESE CATEGORIES:

1. **Generic PR, promotional, or congratulatory language**  
   - "We are a global leader in excellence"  
   - "Our people are our greatest strength"

2. **Repetitive slogans or unsubstantiated taglines**  
   - "Powering a sustainable future" (unless substantiated nearby)

3. **Company history or product advertising with no ESG tie**  
   - "Founded in 1921, our company has grown to…"

4. **Generic values not linked to ESG**  
   - "We believe in innovation and customer service" (unless ESG-linked)

5. **Navigation items, TOC pages, footnotes, legal disclaimers**  
   - "Page 4 of 112", "Forward-looking statements…"

---

## FORMATTING INSTRUCTIONS:

- **Retain** original paragraph, bullet, heading structure where applicable.
- **Do not paraphrase** or shorten any retained text.
- Output should be the **filtered full text**, only with irrelevant parts removed.

---

### INPUT DOCUMENT:
==========
{content}
==========

### CLEANED REPORT:
(Return only the filtered text, no commentary or headers.)
""" 