# src/greenwashing_detector/tools/tcfd_analyzer.py

from typing import Any, Annotated, Dict, List, Optional
from crewai.tools import BaseTool
from .prompt_builder import PromptBuilder
import json
import re

class TCFDAnalyzerTool(BaseTool):
    """Tool for sophisticated TCFD compliance analysis using Chatreport-style prompts."""
    
    name: Annotated[str, "TCFDAnalyzerTool"] = "TCFDAnalyzerTool"
    description: Annotated[str, "Tool description"] = """
    Performs sophisticated TCFD compliance analysis using detailed assessment criteria.
    Provides pillar-specific analysis, compliance scoring, and greenwashing detection.
    Use this tool to analyze TCFD disclosures in sustainability reports.
    """

    def __init__(self):
        super().__init__()

    @property
    def prompt_builder(self):
        """Get the prompt builder instance."""
        return PromptBuilder(["TCFD"])

    def _run(self, 
             report_content: str, 
             analysis_type: str = "comprehensive",
             pillar: Optional[str] = None) -> str:
        """
        Analyze TCFD compliance in sustainability report content.
        
        Args:
            report_content: The sustainability report text to analyze
            analysis_type: "comprehensive" for full TCFD analysis, "pillar" for specific pillar
            pillar: TCFD pillar to analyze (tcfd_1 through tcfd_11) if analysis_type is "pillar"
        """
        
        try:
            if analysis_type == "pillar" and pillar:
                return self._analyze_tcfd_pillar(report_content, pillar)
            elif analysis_type == "comprehensive":
                return self._analyze_comprehensive_tcfd(report_content)
            else:
                return "Invalid analysis type. Use 'comprehensive' or 'pillar' with a specific pillar (tcfd_1 through tcfd_11)."
                
        except Exception as e:
            return f"Error during TCFD analysis: {str(e)}"

    def _analyze_tcfd_pillar(self, report_content: str, pillar: str) -> str:
        """Analyze a specific TCFD pillar."""
        prompt = self.prompt_builder.build_tcfd_sophisticated_prompt(pillar)
        
        # For now, return the prompt structure - in actual implementation,
        # this would be sent to an LLM for analysis
        return f"""
**TCFD PILLAR ANALYSIS: {pillar.upper()}**

**ANALYSIS PROMPT GENERATED**:
{prompt}

**REPORT CONTENT LENGTH**: {len(report_content)} characters

**NEXT STEPS**:
1. Send the prompt and report content to an LLM for analysis
2. Parse the JSON response
3. Extract compliance score, greenwashing indicators, and missing elements
4. Format results for display

**EXPECTED OUTPUT STRUCTURE**:
- ANSWER: Detailed analysis of the pillar
- COMPLIANCE_SCORE: 0-100 score
- GREENWASHING_INDICATORS: List of potential issues
- MISSING_ELEMENTS: Required elements not found
- SOURCES: Page/section references
"""

    def _analyze_comprehensive_tcfd(self, report_content: str) -> str:
        """Analyze comprehensive TCFD compliance across all pillars."""
        prompt = self.prompt_builder.build_tcfd_sophisticated_prompt()
        
        return f"""
**COMPREHENSIVE TCFD ANALYSIS**

**ANALYSIS PROMPT GENERATED**:
{prompt}

**REPORT CONTENT LENGTH**: {len(report_content)} characters

**ANALYSIS COVERAGE**:
- Governance (TCFD 1-2): Board and management oversight
- Strategy (TCFD 3-5): Business impact and resilience
- Risk Management (TCFD 6-8): Risk processes and integration
- Metrics and Targets (TCFD 9-11): KPIs and emissions disclosure

**NEXT STEPS**:
1. Send the prompt and report content to an LLM for analysis
2. Parse the JSON response
3. Extract overall score and pillar-specific analysis
4. Identify critical findings and recommendations

**EXPECTED OUTPUT STRUCTURE**:
- OVERALL_TCFD_SCORE: 0-100 overall compliance
- PILLAR_ANALYSIS: Detailed scores and findings per pillar
- CRITICAL_FINDINGS: Most important gaps or issues
- RECOMMENDATIONS: Specific improvements needed
- SOURCES: Page/section references
"""

    def analyze_tcfd_pillar_with_llm(self, 
                                   report_content: str, 
                                   pillar: str,
                                   llm_response: str) -> Dict[str, Any]:
        """
        Parse LLM response for TCFD pillar analysis.
        
        Args:
            report_content: Original report content
            pillar: TCFD pillar being analyzed
            llm_response: Response from LLM analysis
            
        Returns:
            Parsed analysis results
        """
        try:
            # Try to extract JSON from LLM response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback parsing if JSON not found
                result = self._parse_text_response(llm_response)
            
            # Add metadata
            result["pillar"] = pillar
            result["analysis_timestamp"] = self._get_timestamp()
            result["content_length"] = len(report_content)
            
            return result
            
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse LLM response as JSON",
                "raw_response": llm_response,
                "pillar": pillar
            }

    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        result = {
            "ANSWER": response,
            "COMPLIANCE_SCORE": 0,
            "GREENWASHING_INDICATORS": [],
            "MISSING_ELEMENTS": [],
            "SOURCES": []
        }
        
        # Try to extract score if mentioned
        score_match = re.search(r'(\d+)/100|score[:\s]*(\d+)', response, re.IGNORECASE)
        if score_match:
            result["COMPLIANCE_SCORE"] = int(score_match.group(1) or score_match.group(2))
        
        return result

    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis tracking."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_tcfd_pillar_summary(self, pillar: str) -> str:
        """Get a summary of what a specific TCFD pillar requires."""
        from .framework_glossary import FRAMEWORKS
        
        if "TCFD" not in FRAMEWORKS:
            return "TCFD framework not available."
        
        tcfd_framework = FRAMEWORKS["TCFD"]
        
        if pillar not in tcfd_framework.get("queries", {}):
            return f"Pillar {pillar} not found in TCFD framework."
        
        query = tcfd_framework["queries"][pillar]
        assessment = tcfd_framework["assessments"][pillar]
        
        return f"""
**TCFD PILLAR: {pillar.upper()}**

**QUESTION**: {query}

**REQUIRED DISCLOSURE**:
{assessment}

**GUIDELINE**: {tcfd_framework["guidelines"][pillar]}
"""

    def get_all_tcfd_pillars(self) -> List[str]:
        """Get list of all available TCFD pillars."""
        from .framework_glossary import FRAMEWORKS
        
        if "TCFD" not in FRAMEWORKS:
            return []
        
        return list(FRAMEWORKS["TCFD"].get("queries", {}).keys())


# Example usage and testing
if __name__ == "__main__":
    analyzer = TCFDAnalyzerTool()
    
    # Test pillar summary
    print("=== TCFD Pillar Summary ===")
    print(analyzer.get_tcfd_pillar_summary("tcfd_1"))
    
    # Test available pillars
    print("\n=== Available TCFD Pillars ===")
    pillars = analyzer.get_all_tcfd_pillars()
    for pillar in pillars:
        print(f"- {pillar}")
    
    # Test analysis prompt generation
    print("\n=== TCFD Analysis Prompt ===")
    test_content = "This is a sample sustainability report content for testing TCFD analysis."
    result = analyzer._run(test_content, "pillar", "tcfd_1")
    print(result) 