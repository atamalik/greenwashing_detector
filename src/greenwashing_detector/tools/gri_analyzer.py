#!/usr/bin/env python3
"""
GRI Analyzer Tool for comprehensive GRI compliance assessment.
"""

import json
import logging
from typing import Any, Annotated, Dict, List, Optional
from crewai.tools import BaseTool
from .framework_glossary import FrameworkGlossaryTool

logger = logging.getLogger(__name__)

class GRIAnalyzerTool(BaseTool):
    """Tool for analyzing GRI compliance in sustainability reports."""
    
    name: Annotated[str, "GRIAnalyzerTool"] = "GRIAnalyzerTool"
    description: Annotated[str, "Tool description"] = """
    Analyzes sustainability reports for GRI (Global Reporting Initiative) compliance.
    Provides detailed assessment of GRI disclosures, compliance scores, and greenwashing detection.
    Use this tool when GRI standards are detected in a sustainability report.
    """

    def __init__(self):
        super().__init__()
        self._framework_glossary = None
        self._gri_data = None

    @property
    def framework_glossary(self):
        """Get the framework glossary tool."""
        if self._framework_glossary is None:
            self._framework_glossary = FrameworkGlossaryTool()
        return self._framework_glossary

    @property
    def gri_data(self):
        """Get GRI framework data from the framework glossary."""
        if self._gri_data is None:
            self._gri_data = self._get_gri_framework_data()
        return self._gri_data

    def _get_gri_framework_data(self) -> Dict[str, Any]:
        """Get GRI framework data from the framework glossary."""
        try:
            # Access the GRI data from the framework glossary
            gri_info = self.framework_glossary._run("GRI")
            
            # Common GRI indicators and their requirements
            gri_indicators = {
                "GRI 102": {
                    "name": "General Disclosures",
                    "requirements": """
                    - Organizational profile and scale
                    - Strategy and analysis
                    - Ethics and integrity
                    - Governance
                    - Stakeholder engagement
                    - Reporting practice
                    - Material topics and their boundaries
                    """,
                    "keywords": ["organizational profile", "strategy", "governance", "stakeholders", "material topics"]
                },
                "GRI 305": {
                    "name": "Emissions",
                    "requirements": """
                    - Direct greenhouse gas (GHG) emissions (Scope 1)
                    - Energy indirect GHG emissions (Scope 2)
                    - Other indirect GHG emissions (Scope 3)
                    - GHG emissions intensity
                    - Reduction of GHG emissions
                    - Emissions of ozone-depleting substances (ODS)
                    - Nitrogen oxides (NOX), sulfur oxides (SOX), and other significant air emissions
                    """,
                    "keywords": ["emissions", "greenhouse gas", "GHG", "Scope 1", "Scope 2", "Scope 3", "carbon footprint"]
                },
                "GRI 403": {
                    "name": "Occupational Health and Safety",
                    "requirements": """
                    - Occupational health and safety management system
                    - Hazard identification, risk assessment, and incident investigation
                    - Occupational health services
                    - Worker participation, consultation, and communication on occupational health and safety
                    - Worker training on occupational health and safety
                    - Promotion of worker health
                    - Prevention and mitigation of occupational health and safety impacts directly linked by business relationships
                    - Workers covered by an occupational health and safety management system
                    - Work-related injuries
                    - Work-related ill health
                    """,
                    "keywords": ["health and safety", "occupational health", "workplace safety", "injuries", "ill health"]
                },
                "GRI 401": {
                    "name": "Employment",
                    "requirements": """
                    - New employee hires and employee turnover
                    - Benefits provided to full-time employees that are not provided to temporary or part-time employees
                    - Parental leave
                    """,
                    "keywords": ["employment", "hires", "turnover", "benefits", "parental leave"]
                },
                "GRI 413": {
                    "name": "Local Communities",
                    "requirements": """
                    - Operations with local community engagement, impact assessments, and development programs
                    - Operations with significant actual and potential negative impacts on local communities
                    """,
                    "keywords": ["local communities", "community engagement", "impact assessment", "development programs"]
                },
                "GRI 414": {
                    "name": "Supplier Social Assessment",
                    "requirements": """
                    - New suppliers that were screened using social criteria
                    - Negative social impacts in the supply chain and actions taken
                    """,
                    "keywords": ["suppliers", "supply chain", "social criteria", "negative impacts"]
                },
                "GRI 302": {
                    "name": "Energy",
                    "requirements": """
                    - Energy consumption within the organization
                    - Energy consumption outside of the organization
                    - Energy intensity
                    - Reduction of energy consumption
                    - Reductions in energy requirements of products and services
                    """,
                    "keywords": ["energy consumption", "energy efficiency", "renewable energy", "energy intensity", "energy reduction"],
                    "risk_factors": [
                        "Vague claims about using renewable energy without specifying percentage or source",
                        "Energy efficiency claims without baseline comparisons"
                    ],
                    "red_flags": [
                        "Terms like 'green energy' or 'clean energy' with no quantitative backing",
                        "Statements like 'we are energy efficient' without data"
                    ]
                },
                "GRI 306": {
                    "name": "Waste",
                    "requirements": """
                    - Waste generation and significant waste-related impacts
                    - Management of significant waste-related impacts
                    - Waste diverted from disposal
                    - Waste directed to disposal
                    """,
                    "keywords": ["waste", "zero waste", "recycling", "landfill", "disposal"],
                    "risk_factors": [
                        "Zero-waste claims without lifecycle evidence",
                        "Generic references to 'recycling' without scope or data"
                    ],
                    "red_flags": [
                        "Use of aspirational language without current performance data (e.g., 'working towards zero waste')",
                        "No mention of hazardous waste or e-waste handling"
                    ]
                },
                "GRI 307": {
                    "name": "Environmental Compliance",
                    "requirements": """
                    - Non-compliance with environmental laws and regulations
                    - Significant fines or sanctions for non-compliance
                    """,
                    "keywords": ["compliance", "regulation", "environmental law", "fines", "sanctions"],
                    "risk_factors": [
                        "Statements like 'we comply with all laws' without specifics",
                        "Lack of historical context on violations or penalties"
                    ],
                    "red_flags": [
                        "No mention of whether compliance was independently verified",
                        "Omission of past environmental violations in sectors with known exposure"
                    ]
                },
                "GRI 308": {
                    "name": "Supplier Environmental Assessment",
                    "requirements": """
                    - New suppliers screened using environmental criteria
                    - Negative environmental impacts in supply chain and actions taken
                    """,
                    "keywords": ["supplier screening", "environmental criteria", "supply chain", "impacts"],
                    "risk_factors": [
                        "Blanket claims of supplier compliance with no audit or verification details",
                        "Generic commitment to 'sustainable sourcing' without tangible mechanisms"
                    ],
                    "red_flags": [
                        "No data on how many suppliers were actually assessed",
                        "Phrases like 'we ensure our suppliers are green' without evidence"
                    ]
                }
            }
            
            return {
                "info": gri_info,
                "indicators": gri_indicators
            }
        except Exception as e:
            logger.error(f"Error getting GRI framework data: {e}")
            return {"info": "GRI framework information", "indicators": {}}

    def _run(self, report_content: str, analysis_type: str = "comprehensive", 
             disclosure_id: str = None, company_info: Dict[str, str] = None) -> str:
        """
        Analyze GRI compliance in the provided report content.
        
        Args:
            report_content: The sustainability report content to analyze
            analysis_type: Type of analysis ("comprehensive", "indicator", "summary")
            disclosure_id: Specific GRI indicator to analyze (e.g., "GRI 305")
            company_info: Dictionary with company_name, sector, location
            
        Returns:
            Analysis results in structured format
        """
        try:
            logger.info(f"Starting GRI analysis: {analysis_type}")
            
            if not company_info:
                company_info = {
                    "company_name": "Unknown Company",
                    "company_sector": "Unknown Sector", 
                    "company_location": "Unknown Location"
                }
            
            if analysis_type == "indicator" and disclosure_id:
                return self._analyze_specific_indicator(report_content, disclosure_id, company_info)
            elif analysis_type == "comprehensive":
                return self._analyze_comprehensive_gri(report_content, company_info)
            elif analysis_type == "summary":
                return self._analyze_gri_summary(report_content, company_info)
            else:
                return self._analyze_comprehensive_gri(report_content, company_info)
                
        except Exception as e:
            logger.error(f"Error in GRI analysis: {e}")
            return f"Error performing GRI analysis: {str(e)}"

    def _analyze_specific_indicator(self, report_content: str, disclosure_id: str, 
                                  company_info: Dict[str, str]) -> str:
        """Analyze a specific GRI indicator."""
        try:
            # Get indicator requirements
            indicator_data = self.gri_data["indicators"].get(disclosure_id, {})
            requirements = indicator_data.get("requirements", "Requirements not available")
            
            # Get the analysis prompt from framework glossary
            gri_framework = self._get_gri_framework_data()
            analysis_prompt = gri_framework.get("analysis_prompt", "")
            
            # Format the prompt with actual data
            formatted_prompt = analysis_prompt.format(
                company_name=company_info["company_name"],
                company_sector=company_info["company_sector"],
                company_location=company_info["company_location"],
                disclosure_id=disclosure_id,
                requirements=requirements,
                disclosure_text=report_content[:2000]  # Limit content for analysis
            )
            
            return f"""**GRI INDICATOR ANALYSIS: {disclosure_id}**

**ANALYSIS PROMPT GENERATED**:
{formatted_prompt}

**INDICATOR DETAILS**:
- **Name**: {indicator_data.get('name', 'Unknown')}
- **Keywords**: {', '.join(indicator_data.get('keywords', []))}

**ANALYSIS INSTRUCTIONS**:
Use the above prompt to analyze the report content for {disclosure_id} compliance.
Focus on the specific requirements and evaluate evidence quality and greenwashing risk.
Return results in the specified JSON format with compliance score (0-100)."""

        except Exception as e:
            logger.error(f"Error analyzing specific indicator {disclosure_id}: {e}")
            return f"Error analyzing {disclosure_id}: {str(e)}"

    def _analyze_comprehensive_gri(self, report_content: str, company_info: Dict[str, str]) -> str:
        """Perform comprehensive GRI analysis across all detected indicators."""
        try:
            detected_indicators = self._detect_gri_indicators(report_content)
            
            analysis_results = []
            for indicator_id in detected_indicators:
                indicator_analysis = self._analyze_specific_indicator(
                    report_content, indicator_id, company_info
                )
                analysis_results.append(f"\n--- {indicator_id} ---\n{indicator_analysis}")
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_compliance_score(detected_indicators)
            
            return f"""**COMPREHENSIVE GRI ANALYSIS**

**COMPANY INFORMATION**:
- **Name**: {company_info['company_name']}
- **Sector**: {company_info['company_sector']}
- **Location**: {company_info['company_location']}

**DETECTED GRI INDICATORS**:
{', '.join(detected_indicators) if detected_indicators else 'No GRI indicators detected'}

**OVERALL COMPLIANCE SCORE**: {overall_score}/100

**INDICATOR-SPECIFIC ANALYSES**:
{''.join(analysis_results)}

**ANALYSIS SUMMARY**:
This comprehensive analysis evaluates GRI compliance across all detected indicators.
Each indicator analysis should be performed using the structured prompt format.
Focus on evidence quality, greenwashing risk, and specific compliance requirements."""

        except Exception as e:
            logger.error(f"Error in comprehensive GRI analysis: {e}")
            return f"Error in comprehensive GRI analysis: {str(e)}"

    def _analyze_gri_summary(self, report_content: str, company_info: Dict[str, str]) -> str:
        """Provide a summary of GRI compliance."""
        try:
            detected_indicators = self._detect_gri_indicators(report_content)
            
            return f"""**GRI COMPLIANCE SUMMARY**

**COMPANY**: {company_info['company_name']}
**SECTOR**: {company_info['company_sector']}
**LOCATION**: {company_info['company_location']}

**DETECTED GRI INDICATORS**: {len(detected_indicators)}
**INDICATORS**: {', '.join(detected_indicators) if detected_indicators else 'None detected'}

**COMPLIANCE ASSESSMENT**:
- **Coverage**: {'Good' if len(detected_indicators) >= 3 else 'Limited' if len(detected_indicators) >= 1 else 'Poor'}
- **Key Areas**: {self._identify_key_areas(detected_indicators)}
- **Recommendations**: {self._generate_recommendations(detected_indicators)}

**NEXT STEPS**:
For detailed analysis of specific indicators, use the indicator-specific analysis function."""

        except Exception as e:
            logger.error(f"Error in GRI summary analysis: {e}")
            return f"Error in GRI summary analysis: {str(e)}"

    def _detect_gri_indicators(self, report_content: str) -> List[str]:
        """Detect GRI indicators mentioned in the report content."""
        detected = []
        content_lower = report_content.lower()
        
        for indicator_id, data in self.gri_data["indicators"].items():
            # Check for indicator ID mentions
            if indicator_id.lower() in content_lower:
                detected.append(indicator_id)
            # Check for keyword mentions
            elif any(keyword.lower() in content_lower for keyword in data.get("keywords", [])):
                detected.append(indicator_id)
        
        return list(set(detected))  # Remove duplicates

    def _calculate_overall_compliance_score(self, detected_indicators: List[str]) -> int:
        """Calculate overall GRI compliance score based on detected indicators."""
        if not detected_indicators:
            return 0
        
        # Basic scoring: more indicators = higher score
        base_score = min(len(detected_indicators) * 15, 100)
        
        # Bonus for having key indicators
        key_indicators = ["GRI 102", "GRI 305", "GRI 403"]
        key_indicator_bonus = sum(10 for indicator in key_indicators if indicator in detected_indicators)
        
        return min(base_score + key_indicator_bonus, 100)

    def _identify_key_areas(self, detected_indicators: List[str]) -> str:
        """Identify key areas covered by detected indicators."""
        areas = []
        
        area_mapping = {
            "GRI 102": "General Disclosures",
            "GRI 305": "Emissions & Environmental",
            "GRI 403": "Occupational Health & Safety", 
            "GRI 401": "Employment",
            "GRI 413": "Local Communities",
            "GRI 414": "Supplier Assessment"
        }
        
        for indicator in detected_indicators:
            if indicator in area_mapping:
                areas.append(area_mapping[indicator])
        
        return ", ".join(areas) if areas else "No specific areas identified"

    def _generate_recommendations(self, detected_indicators: List[str]) -> str:
        """Generate recommendations based on detected indicators."""
        recommendations = []
        
        if not detected_indicators:
            recommendations.append("Implement basic GRI reporting framework")
            recommendations.append("Start with GRI 102 (General Disclosures)")
        
        if "GRI 102" not in detected_indicators:
            recommendations.append("Add GRI 102 General Disclosures")
        
        if "GRI 305" not in detected_indicators:
            recommendations.append("Include GRI 305 Emissions reporting")
        
        if "GRI 403" not in detected_indicators:
            recommendations.append("Implement GRI 403 Occupational Health & Safety")
        
        if len(detected_indicators) < 3:
            recommendations.append("Expand GRI coverage to include more material topics")
        
        return "; ".join(recommendations) if recommendations else "Good GRI coverage achieved"

    def get_gri_indicators(self) -> List[str]:
        """Get list of available GRI indicators."""
        return list(self.gri_data["indicators"].keys())

    def get_indicator_requirements(self, indicator_id: str) -> str:
        """Get requirements for a specific GRI indicator."""
        indicator_data = self.gri_data["indicators"].get(indicator_id, {})
        return indicator_data.get("requirements", "Requirements not available") 