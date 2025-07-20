from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
import logging
import re

logger = logging.getLogger(__name__)

class FluffRemoverInput(BaseModel):
    """Input for the FluffRemover tool."""
    report_text: str = Field(..., description="The full text of the sustainability report to be cleaned")
    detected_frameworks: List[str] = Field(default=[], description="List of detected frameworks (GRI, TCFD, etc.)")

class FluffRemover(BaseTool):
    """
    Tool for removing fluff and extracting relevant ESG content from sustainability reports.
    
    This tool processes full sustainability reports to remove marketing language, 
    repetitive content, and non-substantive text while preserving all ESG-relevant 
    information for downstream analysis. It is framework-aware and preserves content
    specific to detected frameworks like TCFD and GRI.
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
    
    The tool is framework-aware and preserves content specific to detected frameworks
    to ensure downstream analysis has all necessary information.
    """
    
    def __init__(self):
        super().__init__()
        self._framework_content_patterns = self._initialize_framework_patterns()
    
    def _initialize_framework_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for framework-specific content that must be preserved."""
        return {
            "TCFD": {
                "keywords": [
                    "climate-related", "climate risk", "climate scenario", "climate disclosure",
                    "TCFD", "Task Force", "climate governance", "climate strategy", "climate metrics",
                    "Scope 1", "Scope 2", "Scope 3", "greenhouse gas", "GHG", "emissions",
                    "climate resilience", "climate adaptation", "climate mitigation",
                    "board oversight", "climate committee", "climate working group",
                    "climate risk assessment", "climate opportunity", "climate target",
                    "carbon neutral", "net zero", "climate commitment", "climate action"
                ],
                "sections": [
                    "climate", "emissions", "environmental", "governance", "risk management",
                    "strategy", "metrics", "targets", "scenario", "resilience"
                ],
                "indicators": [
                    "tcfd_1", "tcfd_2", "tcfd_3", "tcfd_4", "tcfd_5", "tcfd_6", "tcfd_7",
                    "tcfd_8", "tcfd_9", "tcfd_10", "tcfd_11"
                ]
            },
            "GRI": {
                "keywords": [
                    "GRI", "Global Reporting Initiative", "sustainability standards",
                    "material topics", "materiality", "stakeholder engagement",
                    "GRI 102", "GRI 305", "GRI 403", "GRI 401", "GRI 413", "GRI 414",
                    "GRI 302", "GRI 306", "GRI 307", "GRI 308",
                    "emissions", "energy", "waste", "compliance", "supplier",
                    "occupational health", "safety", "employment", "community"
                ],
                "sections": [
                    "gri", "sustainability", "environmental", "social", "governance",
                    "materiality", "stakeholder", "disclosure", "reporting", "standards"
                ],
                "indicators": [
                    "GRI 102", "GRI 305", "GRI 403", "GRI 401", "GRI 413", "GRI 414",
                    "GRI 302", "GRI 306", "GRI 307", "GRI 308"
                ]
            }
        }
    
    def _run(self, report_text: str, detected_frameworks: List[str] = None) -> str:
        """
        Process the report text to remove fluff and extract relevant ESG content.
        
        Args:
            report_text: The full text of the sustainability report
            detected_frameworks: List of detected frameworks (GRI, TCFD, etc.)
            
        Returns:
            Cleaned text containing only relevant ESG information
        """
        try:
            logger.info("🧹 Starting framework-aware fluff removal process")
            logger.info(f"📄 Input text length: {len(report_text)} characters")
            logger.info(f"🎯 Detected frameworks: {detected_frameworks or 'None'}")
            
            # This is a placeholder implementation
            # In a real implementation, you would use the Ollama model to process this
            # For now, we'll return the text as-is and let the agent handle the processing
            # The framework-aware prompt will ensure proper preservation of framework content
            
            logger.info("✅ Framework-aware fluff removal completed (agent will handle processing)")
            logger.info(f"📄 Output text length: {len(report_text)} characters")
            
            return report_text
            
        except Exception as e:
            logger.error(f"❌ Error in fluff removal: {e}")
            return f"Error processing report text: {str(e)}"
    
    def _run_with_ollama(self, report_text: str, detected_frameworks: List[str] = None) -> str:
        """
        Process the report text using Ollama model for intelligent fluff removal.
        
        Args:
            report_text: The full text of the sustainability report
            detected_frameworks: List of detected frameworks (GRI, TCFD, etc.)
            
        Returns:
            Cleaned text containing only relevant ESG information
        """
        try:
            logger.info("🧹 Starting intelligent framework-aware fluff removal with Ollama")
            logger.info(f"📄 Input text length: {len(report_text)} characters")
            logger.info(f"🎯 Detected frameworks: {detected_frameworks or 'None'}")
            
            # This would be implemented with actual Ollama API calls
            # For now, we'll return the text as-is
            # TODO: Implement Ollama integration for intelligent fluff removal
            
            logger.info("✅ Intelligent framework-aware fluff removal completed")
            logger.info(f"📄 Output text length: {len(report_text)} characters")
            
            return report_text
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent fluff removal: {e}")
            return f"Error processing report text with Ollama: {str(e)}"

    def _contains_framework_content(self, text: str, framework: str) -> bool:
        """Check if text contains content relevant to a specific framework."""
        if framework not in self._framework_content_patterns:
            return False
        
        patterns = self._framework_content_patterns[framework]
        text_lower = text.lower()
        
        # Check for keywords
        for keyword in patterns["keywords"]:
            if keyword.lower() in text_lower:
                return True
        
        # Check for indicators
        for indicator in patterns["indicators"]:
            if indicator.lower() in text_lower:
                return True
        
        return False

    def _get_framework_aware_prompt(self, detected_frameworks: List[str] = None) -> str:
        """Generate a framework-aware fluff removal prompt."""
        base_prompt = FRAMEWORK_AWARE_FLUFF_REMOVAL_PROMPT
        
        if not detected_frameworks:
            return base_prompt
        
        # Add framework-specific preservation instructions
        framework_instructions = "\n\n## 🎯 FRAMEWORK-SPECIFIC PRESERVATION REQUIREMENTS:\n"
        
        for framework in detected_frameworks:
            if framework.upper() == "TCFD":
                framework_instructions += """
**TCFD CONTENT - MUST PRESERVE:**
- All climate-related risk and opportunity discussions
- Board oversight of climate issues (tcfd_1)
- Management's role in climate risk assessment (tcfd_2)
- Climate risk identification and time horizons (tcfd_3)
- Impact on business strategy and financial planning (tcfd_4)
- Climate scenario analysis and resilience (tcfd_5)
- Climate risk identification processes (tcfd_6)
- Climate risk management processes (tcfd_7)
- Integration with overall risk management (tcfd_8)
- Climate metrics and performance indicators (tcfd_9)
- Scope 1, 2, 3 emissions data and methodology (tcfd_10)
- Climate targets and performance against targets (tcfd_11)
- Any mention of "climate", "emissions", "GHG", "carbon", "TCFD"
"""
            elif framework.upper() == "GRI":
                framework_instructions += """
**GRI CONTENT - MUST PRESERVE:**
- All GRI indicator mentions (GRI 102, 305, 403, 401, 413, 414, 302, 306, 307, 308)
- Material topics and stakeholder engagement processes
- Specific GRI disclosures and reporting methodology
- Environmental performance data (emissions, energy, waste, water)
- Social performance data (employment, health & safety, community)
- Governance disclosures and compliance information
- Any mention of "GRI", "Global Reporting Initiative", "materiality", "stakeholder"
- Specific quantitative data related to GRI indicators
- Reporting boundaries and methodology explanations
"""
        
        return base_prompt + framework_instructions

FRAMEWORK_AWARE_FLUFF_REMOVAL_PROMPT = """
You are a world-class ESG compliance analyst and greenwashing detection assistant. Your task is to carefully clean the following corporate sustainability report by removing irrelevant, promotional, or redundant content, while preserving **all potentially meaningful, material, or scrutinizable ESG-related information**.

This is **not a summarization task**. You must **retain original wording verbatim** for anything that could later be used to assess ESG claims, disclosure quality, or detect potential greenwashing.

**CRITICAL**: If TCFD or GRI frameworks are detected, you MUST preserve ALL content related to these frameworks as it will be analyzed by specialized tools.

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