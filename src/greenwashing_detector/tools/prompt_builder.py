import os   
from typing import List
from .framework_glossary import FRAMEWORKS

class PromptBuilder:
    def __init__(self, detected_frameworks: List[str]):
        self.detected_frameworks = detected_frameworks
        self.valid_frameworks = [fw for fw in detected_frameworks if fw in FRAMEWORKS]
        self.missing = [fw for fw in detected_frameworks if fw not in FRAMEWORKS]

    def build_claims_extraction_prompt(self) -> str:
        parts = []
        for fw_key in self.valid_frameworks:
            fw = FRAMEWORKS[fw_key]
            if 'prompt_snippets' in fw and 'claims_extraction' in fw['prompt_snippets']:
                parts.append(f"### {fw['name']}\n{fw['prompt_snippets']['claims_extraction']}")
        return self._finalize_prompt(parts, "ESG Claims Extraction")

    def build_greenwashing_analysis_prompt(self) -> str:
        parts = []
        for fw_key in self.valid_frameworks:
            fw = FRAMEWORKS[fw_key]
            if 'prompt_snippets' in fw and 'greenwashing_analysis' in fw['prompt_snippets']:
                parts.append(f"### {fw['name']}\n{fw['prompt_snippets']['greenwashing_analysis']}")
        return self._finalize_prompt(parts, "Greenwashing Analysis")

    def build_tcfd_sophisticated_prompt(self, tcfd_pillar: str = None) -> str:
        """Build sophisticated TCFD prompts based on Chatreport's approach."""
        if "TCFD" not in self.valid_frameworks:
            return "TCFD framework not detected in the report."
        
        tcfd_framework = FRAMEWORKS["TCFD"]
        
        if tcfd_pillar and tcfd_pillar in tcfd_framework.get("queries", {}):
            # Build specific pillar prompt
            return self._build_tcfd_pillar_prompt(tcfd_framework, tcfd_pillar)
        else:
            # Build comprehensive TCFD prompt
            return self._build_comprehensive_tcfd_prompt(tcfd_framework)

    def _build_tcfd_pillar_prompt(self, tcfd_framework: dict, pillar: str) -> str:
        """Build a sophisticated prompt for a specific TCFD pillar."""
        query = tcfd_framework["queries"][pillar]
        assessment = tcfd_framework["assessments"][pillar]
        guideline = tcfd_framework["guidelines"][pillar]
        
        prompt = f"""You are a Senior Equity Analyst with expertise in climate science analyzing a company's sustainability report for TCFD compliance.

**TCFD PILLAR**: {pillar.upper()}
**SPECIFIC QUESTION**: {query}

**REQUIRED DISCLOSURE CRITERIA**:
{assessment}

**ANALYSIS GUIDELINES**:
1. Your response must be precise, thorough, and grounded on specific extracts from the report to verify its authenticity.
2. If you are unsure, simply acknowledge the lack of knowledge, rather than fabricating an answer.
3. Be skeptical of the information disclosed in the report as there might be greenwashing (exaggerating the firm's environmental responsibility). Always answer in a critical tone.
4. "Cheap talks" are statements that are costless to make and may not necessarily reflect the true intentions or future actions of the company. Be critical of all cheap talks you discover in the report.
5. Always acknowledge that the information provided represents the company's view based on its report.
6. Scrutinize whether the report is grounded in quantifiable, concrete data or vague, unverifiable statements, and communicate your findings.
7. {guideline}

**OUTPUT FORMAT**: JSON with the following structure:
{{
    "ANSWER": "Your detailed analysis (max 200 words)",
    "COMPLIANCE_SCORE": "Integer 0-100 based on how well the disclosure meets TCFD requirements",
    "GREENWASHING_INDICATORS": ["List of potential greenwashing signals found"],
    "MISSING_ELEMENTS": ["List of required TCFD elements not found"],
    "SOURCES": ["List of page numbers or sections referenced"]
}}

Analyze the provided report content for this specific TCFD pillar."""
        
        return prompt

    def _build_comprehensive_tcfd_prompt(self, tcfd_framework: dict) -> str:
        """Build a comprehensive TCFD analysis prompt covering all pillars."""
        
        prompt = f"""You are a Senior Equity Analyst with expertise in climate science analyzing a company's sustainability report for comprehensive TCFD compliance.

**TCFD FRAMEWORK OVERVIEW**:
The Task Force on Climate-related Financial Disclosures (TCFD) requires disclosure across four pillars:
1. **Governance** - Board and management oversight of climate-related risks and opportunities
2. **Strategy** - Actual and potential impacts of climate-related risks and opportunities on business strategy and financial planning
3. **Risk Management** - Processes for identifying, assessing, and managing climate-related risks
4. **Metrics and Targets** - Metrics and targets used to assess and manage climate-related risks and opportunities

**ANALYSIS REQUIREMENTS**:
For each TCFD pillar, you must evaluate:

**Governance (TCFD 1-2)**:
- Board oversight of climate issues
- Management role in climate risk assessment and management
- Organizational structures and reporting lines

**Strategy (TCFD 3-5)**:
- Climate-related risks and opportunities across time horizons
- Impact on business strategy and financial planning
- Strategy resilience under different climate scenarios

**Risk Management (TCFD 6-8)**:
- Processes for identifying and assessing climate risks
- Risk management and mitigation strategies
- Integration with overall risk management

**Metrics and Targets (TCFD 9-11)**:
- Key climate-related metrics and KPIs
- GHG emissions disclosure (Scope 1, 2, 3)
- Climate-related targets and performance tracking

**ANALYSIS GUIDELINES**:
1. **Critical Assessment**: Be skeptical of greenwashing - exaggerated environmental responsibility claims
2. **Evidence-Based**: Ground all analysis in specific report extracts with page references
3. **Quantitative Focus**: Prioritize concrete data over vague statements
4. **Cheap Talk Detection**: Identify statements that are costless to make but lack substance
5. **Completeness Check**: Identify missing required TCFD elements
6. **Materiality Assessment**: Evaluate whether disclosures address financially material climate risks

**OUTPUT FORMAT**: JSON with the following structure:
{{
    "OVERALL_TCFD_SCORE": "Integer 0-100",
    "PILLAR_ANALYSIS": {{
        "GOVERNANCE": {{
            "score": "Integer 0-100",
            "strengths": ["List of strong disclosures"],
            "weaknesses": ["List of missing or weak disclosures"],
            "greenwashing_signals": ["List of potential greenwashing indicators"]
        }},
        "STRATEGY": {{...}},
        "RISK_MANAGEMENT": {{...}},
        "METRICS_TARGETS": {{...}}
    }},
    "CRITICAL_FINDINGS": ["List of most important compliance gaps or greenwashing signals"],
    "RECOMMENDATIONS": ["List of specific improvements needed"],
    "SOURCES": ["List of page numbers or sections referenced"]
}}

Analyze the provided report content for comprehensive TCFD compliance."""
        
        return prompt

    def build_tcfd_assessment_prompt(self, pillar: str, report_content: str) -> str:
        """Build a TCFD assessment prompt for scoring disclosure quality."""
        if "TCFD" not in self.valid_frameworks:
            return "TCFD framework not detected in the report."
        
        tcfd_framework = FRAMEWORKS["TCFD"]
        query = tcfd_framework["queries"][pillar]
        assessment = tcfd_framework["assessments"][pillar]
        
        prompt = f"""Your task is to rate a sustainability report's disclosure quality on the following TCFD element:

**CRITICAL ELEMENT**: {query}

**REQUIREMENTS** for high-quality disclosure:
{assessment}

**REPORT CONTENT TO ANALYZE**:
{report_content}

**ASSESSMENT CRITERIA**:
- Score 0-100 based on completeness and quality of disclosure
- 0-20: No meaningful disclosure or completely inadequate
- 21-40: Minimal disclosure with significant gaps
- 41-60: Partial disclosure with some key elements missing
- 61-80: Good disclosure with minor gaps
- 81-100: Comprehensive disclosure meeting most/all requirements

**OUTPUT FORMAT**: JSON with the following structure:
{{
    "ANALYSIS": "Detailed assessment of disclosure quality (max 150 words)",
    "SCORE": "Integer 0-100",
    "MET_REQUIREMENTS": ["List of requirements that are met"],
    "MISSING_REQUIREMENTS": ["List of requirements that are missing or inadequate"],
    "GREENWASHING_INDICATORS": ["List of potential greenwashing signals"]
}}

Analyze the extent to which the disclosure satisfies the TCFD requirements."""
        
        return prompt

    def _finalize_prompt(self, sections: List[str], task_type: str) -> str:
        if not sections:
            return f"No tailored prompts found for the detected frameworks: {', '.join(self.detected_frameworks)}"

        header = (
            f"You are an expert ESG analyst. Your task is: {task_type}\n"
            f"Detected frameworks: {', '.join(self.valid_frameworks)}\n"
            f"Use the following tailored guidance per framework:\n"
        )
        body = "\n---\n".join(sections)
        return f"{header}\n{body}"


# Example usage (for test/debug):
if __name__ == "__main__":
    builder = PromptBuilder(["GRI", "TCFD", "SASB"])
    print("--- Claims Prompt ---")
    print(builder.build_claims_extraction_prompt())
    print("\n--- Greenwashing Prompt ---")
    print(builder.build_greenwashing_analysis_prompt())
    print("\n--- TCFD Sophisticated Prompt ---")
    print(builder.build_tcfd_sophisticated_prompt("tcfd_1"))