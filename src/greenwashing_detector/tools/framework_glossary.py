# src/greenwashing_detector/tools/framework_glossary.py

from typing import Any, Annotated
from crewai.tools import BaseTool

class FrameworkGlossaryTool(BaseTool):
    """Tool for providing ESG framework descriptions and key identifiers."""
    
    name: Annotated[str, "FrameworkGlossaryTool"] = "FrameworkGlossaryTool"
    description: Annotated[str, "Tool description"] = """
    Provides ESG framework descriptions and key identifiers based on name or acronym.
    Use this tool to understand what different ESG reporting frameworks are and what
    keywords to look for when detecting them in reports.
    """

    def _run(self, query: str) -> str:
        """Look up ESG framework information by name or acronym."""
        
        FRAMEWORKS = {
            "GRI": {
                "name": "Global Reporting Initiative",
                "purpose": "International standards for sustainability reporting",
                "keywords": ["GRI", "Global Reporting Initiative", "sustainability standards", "material topics"],
                "indicators": [
                    "GRI 102: General Disclosures",
                    "GRI 305: Emissions",
                    "GRI 403: Occupational Health and Safety",
                    "GRI 401: Employment"
                ],
                "greenwashing_signals": [
                    "Generic sustainability statements without reference to specific GRI indicators",
                    "Claims of alignment without reporting material topics",
                    "Lack of data granularity for reported metrics"
                ],
                "claim_patterns": [
                    "We report in accordance with GRI standards",
                    "Our emissions disclosures align with GRI 305",
                    "We prioritize employee safety in line with GRI 403"
                ],
                "prompt_snippets": {
                    "claims_extraction": "Extract ESG claims that reference or imply alignment with GRI standards (e.g. GRI 102, 305, 403). Focus on mentions of disclosures, indicators, and materiality. Provide section headers or page context for each.",
                    "greenwashing_analysis": "For each GRI-aligned claim, evaluate the specificity of disclosed indicators, presence of quantitative data, and whether the material topics are identified. Flag claims that use GRI language without proper supporting disclosures."
                },
                "analysis_prompt": """You are a Senior ESG Compliance Analyst evaluating the quality of a sustainability report's disclosure against GRI standards.

<BASIC_INFO>:
====
Company Name: {company_name}
Sector: {company_sector}
Location: {company_location}
====

Your task is to evaluate whether the following GRI disclosure is sufficiently addressed:

<GRI_DISCLOSURE_ID>: {disclosure_id}

<DISCLOSURE_REQUIREMENTS>:
====
{requirements}
====

<DISCLOSURE_TEXT>:
====
{disclosure_text}
====

Evaluate how well this disclosure fulfills the GRI requirements. Be strict and analytical. Consider the following:

1. Does the disclosure provide quantitative data? If so, is it detailed and transparent?
2. Are methodologies, baselines, or scopes clearly stated?
3. Is the language vague, promotional, or lacking substance?
4. Are any critical components missing or misrepresented?
5. Is the content measurable and verifiable?

If the disclosure does **not address** the requirements at all, say so explicitly and assign a score of 0.

SCORE rubric:
- 100 = Fully meets all requirements with detail, evidence, and clarity.
- 50 = Partially meets requirements, but with vague or missing data.
- 0 = No alignment with GRI disclosure requirements.

Return your answer in this **JSON format**:
{
  "DISCLOSURE_ID": "...",
  "SUMMARY": "...",
  "EVIDENCE_QUALITY": "High | Medium | Low",
  "GREENWASHING_RISK": "Low | Medium | High",
  "SCORE": 0-100,
  "COMMENTS": "..."
}"""
            },

            "TCFD": {
                "name": "Task Force on Climate-related Financial Disclosures",
                "purpose": "Framework for climate-related financial risk disclosures",
                "keywords": ["TCFD", "climate-related financial disclosures", "climate risk", "climate scenarios"],
                "pillars": ["Governance", "Strategy", "Risk Management", "Metrics and Targets"],
                "queries": {
                    "tcfd_1": "How does the company's board oversee climate-related risks and opportunities?",
                    "tcfd_2": "What is the role of management in assessing and managing climate-related risks and opportunities?",
                    "tcfd_3": "What are the most relevant climate-related risks and opportunities that the organisation has identified over the short, medium, and long term? Are risks clearly associated with a horizon?",
                    "tcfd_4": "How do climate-related risks and opportunities impact the organisation's businesses strategy, economic and financial performance, and financial planning?",
                    "tcfd_5": "How resilient is the organisation's strategy when considering different climate-related scenarios, including a 2°C target or lower scenario? How resilient is the organisation's strategy when considering climate physical risks?",
                    "tcfd_6": "What processes does the organisation use to identify and assess climate-related risks?",
                    "tcfd_7": "How does the organisation manage climate-related risks?",
                    "tcfd_8": "How are the processes for identifying, assessing, and managing climate-related risks integrated into the organisation's overall risk management?",
                    "tcfd_9": "What metrics does the organisation use to assess climate-related risks and opportunities? How do the metrics help ensure that the performance is in line with its strategy and risk management process?",
                    "tcfd_10": "Does the organisation disclose its Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions? What are the related risks and do they differ depending on the scope?",
                    "tcfd_11": "What targets does the organisation use to understand/quantify/benchmark climate-related risks and opportunities? How is the organization performing against these targets?"
                },
                "assessments": {
                    "tcfd_1": """In describing the board's oversight of climate-related issues, organizations should consider including a discussion of the following:
1. processes and frequency by which the board and/or board committees (e.g., audit, risk, or other committees) are informed about climate-related issues;
2. whether the board and/or board committees consider climate-related issues when reviewing and guiding strategy, major plans of action, risk management policies, annual budgets, and business plans as well as setting the organization's performance objectives, monitoring implementation and performance, and overseeing major capital expenditures, acquisitions, and divestitures; and 
3. how the board monitors and oversees progress against goals and targets for addressing climate-related issues.""",
                    "tcfd_2": """In describing management's role related to the assessment and management of climate-related issues, organizations should consider including the following information:
1. whether the organization has assigned climate-related responsibilities to management-level positions or committees; and, if so, whether such management positions or committees report to the board or a committee of the board and whether those responsibilities include assessing and/or managing climate-related issues;
2. a description of the associated organizational structure(s);
3. processes by which management is informed about climate-related issues; and
4. how management (through specific positions and/or management committees) monitors climate-related issues.""",
                    "tcfd_3": """In describing the climate-related risks and opportunities the organization has identified over the short, medium, and long term, organizations should provide the following information:
1. a description of what they consider to be the relevant short-, medium-, and long-term time horizons, taking into consideration the useful life of the organization's assets or infrastructure and the fact that climate-related issues often manifest themselves over the medium and longer terms;
2. a description of the specific climate-related issues potentially arising in each time horizon (short, medium, and long term) that could have a material financial impact on the organization; and
3. a description of the process(es) used to determine which risks and opportunities could have a material financial impact on the organization. 
Organizations should consider providing a description of their risks and opportunities by sector and/or geography, as appropriate.""",
                    "tcfd_4": """In describing impact of climate-related risks and opportunities on the organization's businesses, strategy, and financial planning, organizations should discuss how identified climate-related issues have affected their businesses, strategy, and financial planning. 
Organizations should consider including the impact on their businesses, strategy, and financial planning in the following areas:
1. Products and services
2. Supply chain and/or value chain
3. Adaptation and mitigation activities
4. Investment in research and development
5. Operations (including types of operations and location of facilities)
6. Acquisitions or divestments
7. Access to capital
Organizations should describe how climate-related issues serve as an input to their financial planning process, the time period(s) used, and how these risks and opportunities are prioritized. Organizations' disclosures should reflect a holistic picture of the interdependencies among the factors that affect their ability to create value over time. 
Organizations should describe the impact of climate-related issues on their financial performance (e.g., revenues, costs) and financial position (e.g., assets, liabilities). If climate-related scenarios were used to inform the organization's strategy and financial planning, such scenarios should be described.
Organizations that have made GHG emissions reduction commitments, operate in jurisdictions that have made such commitments, or have agreed to meet investor expectations regarding GHG emissions reductions should describe their plans for transitioning to a low-carbon economy, which could include GHG emissions targets and specific activities intended to reduce GHG emissions in their operations and value chain or to otherwise support the transition.""",
                    "tcfd_5": """In describing the resilience of the organization's strategy, organizations should describe how resilient their strategies are to climate-related risks and opportunities, taking into consideration a transition to a low-carbon economy consistent with a 2°C or lower scenario and, where relevant to the organization, scenarios consistent with increased physical climate-related risks.
Organizations should consider discussing:
1. where they believe their strategies may be affected by climate-related risks and opportunities; 
2. how their strategies might change to address such potential risks and opportunities;
3. the potential impact of climate-related issues on financial performance (e.g., revenues, costs) and financial position (e.g., assets, liabilities); and
4. the climate-related scenarios and associated time horizon(s) considered.""",
                    "tcfd_6": """In describing the organization's processes for identifying and assessing climate-related risks, organizations should describe their risk management processes for identifying and assessing climate-related risks. An important aspect of this description is how organizations determine the relative significance of climate-related risks in relation to other risks. 
Organizations should describe whether they consider existing and emerging regulatory requirements related to climate change (e.g., limits on emissions) as well as other relevant factors considered.
Organizations should also consider disclosing the following:
1. processes for assessing the potential size and scope of identified climate-related risks and
2. definitions of risk terminology used or references to existing risk classification frameworks used.""",
                    "tcfd_7": """In describing the organization's processes for managing climate-related risks, organizations should describe their processes for managing climate-related risks, including how they make decisions to mitigate, transfer, accept, or control those risks. In addition, organizations should describe their processes for prioritizing climate-related risks, including how materiality determinations are made within their organizations.""",
                    "tcfd_8": """In describing how processes for identifying, assessing, and managing climate-related risks are integrated into the organization's overall risk management, organizations should describe how their processes for identifying, assessing, and managing climate-related risks are integrated into their overall risk management.""",
                    "tcfd_9": """In describing the metrics used by the organization to assess climate-related risks and opportunities in line with its strategy and risk management process, organizations should provide the key metrics used to measure and manage climate-related risks and opportunities, as well as metrics consistent with the cross-industry.
Organizations should consider including metrics on climate-related risks associated with water, energy, land use, and waste management where relevant and applicable.
Where climate-related issues are material, organizations should consider describing whether and how related performance metrics are incorporated into remuneration policies.
Where relevant, organizations should provide their internal carbon prices as well as climate-related opportunity metrics such as revenue from products and services designed for a low-carbon economy. 
Metrics should be provided for historical periods to allow for trend analysis. Where appropriate, organizations should consider providing forward-looking metrics for the cross-industry, consistent with their business or strategic planning time horizons. In addition, where not apparent, organizations should provide a description of the methodologies used to calculate or estimate climate-related metrics.""",
                    "tcfd_10": """In disclosing Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions, and the related risks, organizations should provide their Scope 1 and Scope 2 GHG emissions independent of a materiality assessment, and, if appropriate, Scope 3 GHG emissions and the related risks. All organizations should consider disclosing Scope 3 GHG emissions.
GHG emissions should be calculated in line with the GHG Protocol methodology to allow for aggregation and comparability across organizations and jurisdictions. As appropriate, organizations should consider providing related, generally accepted industry-specific GHG efficiency ratios.
GHG emissions and associated metrics should be provided for historical periods to allow for trend analysis. In addition, where not apparent, organizations should provide a description of the methodologies used to calculate or estimate the metrics.""",
                    "tcfd_11": """In describing the targets used by the organization to manage climate-related risks and opportunities and performance against targets, organizations should describe their key climate-related targets such as those related to GHG emissions, water usage, energy usage, etc., in line with the cross-industry, where relevant, and in line with anticipated regulatory requirements or market constraints or other goals. Other goals may include efficiency or financial goals, financial loss tolerances, avoided GHG emissions through the entire product life cycle, or net revenue goals for products and services designed for a low-carbon economy. 
In describing their targets, organizations should consider including the following:
1. whether the target is absolute or intensity based;
2. time frames over which the target applies;
3. base year from which progress is measured; and
4. key performance indicators used to assess progress against targets.
Organizations disclosing medium-term or long-term targets should also disclose associated interim targets in aggregate or by business line, where available.
Where not apparent, organizations should provide a description of the methodologies used to calculate targets and measures."""
                },
                "guidelines": {
                    "tcfd_1": "Please concentrate on the board's direct responsibilities and actions pertaining to climate issues, without discussing the company-wide risk management system or other topics.",
                    "tcfd_2": "Please focus on their direct duties related to climate issues, without introducing other topics such as the broader corporate risk management system.",
                    "tcfd_3": "Avoid discussing the company-wide risk management system or how these risks and opportunities are identified and managed.",
                    "tcfd_4": "Please do not include the process of risk identification, assessment or management in your answer.",
                    "tcfd_5": "In your response, focus solely on the resilience of strategy in these scenarios, and refrain from discussing processes of risk identification, assessment, or management strategies.",
                    "tcfd_6": "Restrict your answer to the identification and assessment processes, without discussing the management or integration of these risks.",
                    "tcfd_7": "Please focus on the concrete actions and strategies implemented to manage these risks, excluding the process of risk identification or assessment.",
                    "tcfd_8": "Please focus on the integration aspect and avoid discussing the process of risk identification, assessment, or the specific management actions taken.",
                    "tcfd_9": "Do not include information regarding the organization's general risk identification and assessment methods or their broader corporate strategy and initiatives.",
                    "tcfd_10": "Confirm whether the organisation discloses its Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions. If so, provide any available data or specific figures on these emissions. Additionally, identify the related risks. The risks should be specific to the GHG emissions rather than general climate-related risks.",
                    "tcfd_11": "Please detail the precise targets and avoid discussing the company's general risk identification and assessment methods or their commitment to disclosure through the TCFD."
                },
                "greenwashing_signals": [
                    "Mention of TCFD without coverage of all four pillars",
                    "Use of TCFD branding with no climate risk analysis",
                    "No scenario analysis or stress testing",
                    "Vague climate commitments without specific targets",
                    "Lack of quantitative climate risk metrics"
                ],
                "claim_patterns": [
                    "We follow the TCFD framework",
                    "Our strategy addresses climate risks as per TCFD",
                    "We disclose under TCFD guidance",
                    "TCFD-aligned climate risk management"
                ],
                "prompt_snippets": {
                    "claims_extraction": "Extract statements that reference TCFD or relate to its four pillars: Governance, Strategy, Risk Management, and Metrics & Targets. Include context or section references.",
                    "greenwashing_analysis": "Check whether each TCFD claim aligns with the 11 recommended disclosures. Look for time-bound targets, quantitative risk data, and scenario analysis. Flag incomplete or superficial TCFD references."
                }
            },

            "SASB": {
                "name": "Sustainability Accounting Standards Board",
                "purpose": "Industry-specific sustainability accounting standards",
                "keywords": ["SASB", "Sustainability Accounting Standards Board", "industry standards", "materiality"],
                "indicators": [
                    "Sector-specific materiality maps",
                    "Standardized ESG metrics",
                    "Financial impact disclosures"
                ],
                "greenwashing_signals": [
                    "Cites SASB but does not identify industry-specific standards",
                    "No financial materiality discussion",
                    "Vague reference to SASB without standard naming"
                ],
                "claim_patterns": [
                    "We report according to SASB standards",
                    "Our disclosures are SASB-aligned",
                    "We use SASB materiality guidance"
                ],
                "prompt_snippets": {
                    "claims_extraction": "Identify claims that mention SASB standards, especially where industry-specific standards or materiality maps are referenced.",
                    "greenwashing_analysis": "Assess if SASB claims identify the relevant sector-specific standards and disclose financially material ESG risks. Flag general SASB mentions lacking specificity."
                }
            }
        }

        query = query.upper().strip()
        
        # Check for exact matches first
        for key, data in FRAMEWORKS.items():
            if key == query or data["name"].upper() == query:
                return (
                    f"**{data['name']}**\n"
                    f"- **Purpose**: {data['purpose']}\n"
                    f"- **Keywords to look for**: {', '.join(data['keywords'])}"
                )
        
        # Check for partial matches
        for key, data in FRAMEWORKS.items():
            if key in query or any(keyword.lower() in query.lower() for keyword in data["keywords"]):
                return (
                    f"**{data['name']}**\n"
                    f"- **Purpose**: {data['purpose']}\n"
                    f"- **Keywords to look for**: {', '.join(data['keywords'])}"
                )
        
        # If no match found, return available frameworks
        available_frameworks = ", ".join(FRAMEWORKS.keys())
        return (
            f"Framework '{query}' not found. Available frameworks include:\n"
            f"{available_frameworks}\n\n"
            f"Try searching for a specific acronym like GRI, TCFD, ISO 14064, etc."
        )

# Export the frameworks for use in other modules
FRAMEWORKS = {
    "GRI": {
        "name": "Global Reporting Initiative",
        "purpose": "International standards for sustainability reporting",
        "keywords": ["GRI", "Global Reporting Initiative", "sustainability standards", "material topics"],
        "indicators": [
            "GRI 102: General Disclosures",
            "GRI 305: Emissions",
            "GRI 403: Occupational Health and Safety",
            "GRI 401: Employment"
        ],
        "greenwashing_signals": [
            "Generic sustainability statements without reference to specific GRI indicators",
            "Claims of alignment without reporting material topics",
            "Lack of data granularity for reported metrics"
        ],
        "claim_patterns": [
            "We report in accordance with GRI standards",
            "Our emissions disclosures align with GRI 305",
            "We prioritize employee safety in line with GRI 403"
        ],
        "prompt_snippets": {
            "claims_extraction": "Extract ESG claims that reference or imply alignment with GRI standards (e.g. GRI 102, 305, 403). Focus on mentions of disclosures, indicators, and materiality. Provide section headers or page context for each.",
            "greenwashing_analysis": "For each GRI-aligned claim, evaluate the specificity of disclosed indicators, presence of quantitative data, and whether the material topics are identified. Flag claims that use GRI language without proper supporting disclosures."
        },
        "analysis_prompt": """You are a Senior ESG Compliance Analyst evaluating the quality of a sustainability report's disclosure against GRI standards.

<BASIC_INFO>:
====
Company Name: {company_name}
Sector: {company_sector}
Location: {company_location}
====

Your task is to evaluate whether the following GRI disclosure is sufficiently addressed:

<GRI_DISCLOSURE_ID>: {disclosure_id}

<DISCLOSURE_REQUIREMENTS>:
====
{requirements}
====

<DISCLOSURE_TEXT>:
====
{disclosure_text}
====

Evaluate how well this disclosure fulfills the GRI requirements. Be strict and analytical. Consider the following:

1. Does the disclosure provide quantitative data? If so, is it detailed and transparent?
2. Are methodologies, baselines, or scopes clearly stated?
3. Is the language vague, promotional, or lacking substance?
4. Are any critical components missing or misrepresented?
5. Is the content measurable and verifiable?

If the disclosure does **not address** the requirements at all, say so explicitly and assign a score of 0.

SCORE rubric:
- 100 = Fully meets all requirements with detail, evidence, and clarity.
- 50 = Partially meets requirements, but with vague or missing data.
- 0 = No alignment with GRI disclosure requirements.

Return your answer in this **JSON format**:
{
  "DISCLOSURE_ID": "...",
  "SUMMARY": "...",
  "EVIDENCE_QUALITY": "High | Medium | Low",
  "GREENWASHING_RISK": "Low | Medium | High",
  "SCORE": 0-100,
  "COMMENTS": "..."
}"""
    },

    "TCFD": {
        "name": "Task Force on Climate-related Financial Disclosures",
        "purpose": "Framework for climate-related financial risk disclosures",
        "keywords": ["TCFD", "climate-related financial disclosures", "climate risk", "climate scenarios"],
        "pillars": ["Governance", "Strategy", "Risk Management", "Metrics and Targets"],
        "queries": {
            "tcfd_1": "How does the company's board oversee climate-related risks and opportunities?",
            "tcfd_2": "What is the role of management in assessing and managing climate-related risks and opportunities?",
            "tcfd_3": "What are the most relevant climate-related risks and opportunities that the organisation has identified over the short, medium, and long term? Are risks clearly associated with a horizon?",
            "tcfd_4": "How do climate-related risks and opportunities impact the organisation's businesses strategy, economic and financial performance, and financial planning?",
            "tcfd_5": "How resilient is the organisation's strategy when considering different climate-related scenarios, including a 2°C target or lower scenario? How resilient is the organisation's strategy when considering climate physical risks?",
            "tcfd_6": "What processes does the organisation use to identify and assess climate-related risks?",
            "tcfd_7": "How does the organisation manage climate-related risks?",
            "tcfd_8": "How are the processes for identifying, assessing, and managing climate-related risks integrated into the organisation's overall risk management?",
            "tcfd_9": "What metrics does the organisation use to assess climate-related risks and opportunities? How do the metrics help ensure that the performance is in line with its strategy and risk management process?",
            "tcfd_10": "Does the organisation disclose its Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions? What are the related risks and do they differ depending on the scope?",
            "tcfd_11": "What targets does the organisation use to understand/quantify/benchmark climate-related risks and opportunities? How is the organization performing against these targets?"
        },
        "assessments": {
            "tcfd_1": """In describing the board's oversight of climate-related issues, organizations should consider including a discussion of the following:
1. processes and frequency by which the board and/or board committees (e.g., audit, risk, or other committees) are informed about climate-related issues;
2. whether the board and/or board committees consider climate-related issues when reviewing and guiding strategy, major plans of action, risk management policies, annual budgets, and business plans as well as setting the organization's performance objectives, monitoring implementation and performance, and overseeing major capital expenditures, acquisitions, and divestitures; and 
3. how the board monitors and oversees progress against goals and targets for addressing climate-related issues.""",
            "tcfd_2": """In describing management's role related to the assessment and management of climate-related issues, organizations should consider including the following information:
1. whether the organization has assigned climate-related responsibilities to management-level positions or committees; and, if so, whether such management positions or committees report to the board or a committee of the board and whether those responsibilities include assessing and/or managing climate-related issues;
2. a description of the associated organizational structure(s);
3. processes by which management is informed about climate-related issues; and
4. how management (through specific positions and/or management committees) monitors climate-related issues.""",
            "tcfd_3": """In describing the climate-related risks and opportunities the organization has identified over the short, medium, and long term, organizations should provide the following information:
1. a description of what they consider to be the relevant short-, medium-, and long-term time horizons, taking into consideration the useful life of the organization's assets or infrastructure and the fact that climate-related issues often manifest themselves over the medium and longer terms;
2. a description of the specific climate-related issues potentially arising in each time horizon (short, medium, and long term) that could have a material financial impact on the organization; and
3. a description of the process(es) used to determine which risks and opportunities could have a material financial impact on the organization. 
Organizations should consider providing a description of their risks and opportunities by sector and/or geography, as appropriate.""",
            "tcfd_4": """In describing impact of climate-related risks and opportunities on the organization's businesses, strategy, and financial planning, organizations should discuss how identified climate-related issues have affected their businesses, strategy, and financial planning. 
Organizations should consider including the impact on their businesses, strategy, and financial planning in the following areas:
1. Products and services
2. Supply chain and/or value chain
3. Adaptation and mitigation activities
4. Investment in research and development
5. Operations (including types of operations and location of facilities)
6. Acquisitions or divestments
7. Access to capital
Organizations should describe how climate-related issues serve as an input to their financial planning process, the time period(s) used, and how these risks and opportunities are prioritized. Organizations' disclosures should reflect a holistic picture of the interdependencies among the factors that affect their ability to create value over time. 
Organizations should describe the impact of climate-related issues on their financial performance (e.g., revenues, costs) and financial position (e.g., assets, liabilities). If climate-related scenarios were used to inform the organization's strategy and financial planning, such scenarios should be described.
Organizations that have made GHG emissions reduction commitments, operate in jurisdictions that have made such commitments, or have agreed to meet investor expectations regarding GHG emissions reductions should describe their plans for transitioning to a low-carbon economy, which could include GHG emissions targets and specific activities intended to reduce GHG emissions in their operations and value chain or to otherwise support the transition.""",
            "tcfd_5": """In describing the resilience of the organization's strategy, organizations should describe how resilient their strategies are to climate-related risks and opportunities, taking into consideration a transition to a low-carbon economy consistent with a 2°C or lower scenario and, where relevant to the organization, scenarios consistent with increased physical climate-related risks.
Organizations should consider discussing:
1. where they believe their strategies may be affected by climate-related risks and opportunities; 
2. how their strategies might change to address such potential risks and opportunities;
3. the potential impact of climate-related issues on financial performance (e.g., revenues, costs) and financial position (e.g., assets, liabilities); and
4. the climate-related scenarios and associated time horizon(s) considered.""",
            "tcfd_6": """In describing the organization's processes for identifying and assessing climate-related risks, organizations should describe their risk management processes for identifying and assessing climate-related risks. An important aspect of this description is how organizations determine the relative significance of climate-related risks in relation to other risks. 
Organizations should describe whether they consider existing and emerging regulatory requirements related to climate change (e.g., limits on emissions) as well as other relevant factors considered.
Organizations should also consider disclosing the following:
1. processes for assessing the potential size and scope of identified climate-related risks and
2. definitions of risk terminology used or references to existing risk classification frameworks used.""",
            "tcfd_7": """In describing the organization's processes for managing climate-related risks, organizations should describe their processes for managing climate-related risks, including how they make decisions to mitigate, transfer, accept, or control those risks. In addition, organizations should describe their processes for prioritizing climate-related risks, including how materiality determinations are made within their organizations.""",
            "tcfd_8": """In describing how processes for identifying, assessing, and managing climate-related risks are integrated into the organization's overall risk management, organizations should describe how their processes for identifying, assessing, and managing climate-related risks are integrated into their overall risk management.""",
            "tcfd_9": """In describing the metrics used by the organization to assess climate-related risks and opportunities in line with its strategy and risk management process, organizations should provide the key metrics used to measure and manage climate-related risks and opportunities, as well as metrics consistent with the cross-industry.
Organizations should consider including metrics on climate-related risks associated with water, energy, land use, and waste management where relevant and applicable.
Where climate-related issues are material, organizations should consider describing whether and how related performance metrics are incorporated into remuneration policies.
Where relevant, organizations should provide their internal carbon prices as well as climate-related opportunity metrics such as revenue from products and services designed for a low-carbon economy. 
Metrics should be provided for historical periods to allow for trend analysis. Where appropriate, organizations should consider providing forward-looking metrics for the cross-industry, consistent with their business or strategic planning time horizons. In addition, where not apparent, organizations should provide a description of the methodologies used to calculate or estimate climate-related metrics.""",
            "tcfd_10": """In disclosing Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions, and the related risks, organizations should provide their Scope 1 and Scope 2 GHG emissions independent of a materiality assessment, and, if appropriate, Scope 3 GHG emissions and the related risks. All organizations should consider disclosing Scope 3 GHG emissions.
GHG emissions should be calculated in line with the GHG Protocol methodology to allow for aggregation and comparability across organizations and jurisdictions. As appropriate, organizations should consider providing related, generally accepted industry-specific GHG efficiency ratios.
GHG emissions and associated metrics should be provided for historical periods to allow for trend analysis. In addition, where not apparent, organizations should provide a description of the methodologies used to calculate or estimate the metrics.""",
            "tcfd_11": """In describing the targets used by the organization to manage climate-related risks and opportunities and performance against targets, organizations should describe their key climate-related targets such as those related to GHG emissions, water usage, energy usage, etc., in line with the cross-industry, where relevant, and in line with anticipated regulatory requirements or market constraints or other goals. Other goals may include efficiency or financial goals, financial loss tolerances, avoided GHG emissions through the entire product life cycle, or net revenue goals for products and services designed for a low-carbon economy. 
In describing their targets, organizations should consider including the following:
1. whether the target is absolute or intensity based;
2. time frames over which the target applies;
3. base year from which progress is measured; and
4. key performance indicators used to assess progress against targets.
Organizations disclosing medium-term or long-term targets should also disclose associated interim targets in aggregate or by business line, where available.
Where not apparent, organizations should provide a description of the methodologies used to calculate targets and measures."""
        },
        "guidelines": {
            "tcfd_1": "Please concentrate on the board's direct responsibilities and actions pertaining to climate issues, without discussing the company-wide risk management system or other topics.",
            "tcfd_2": "Please focus on their direct duties related to climate issues, without introducing other topics such as the broader corporate risk management system.",
            "tcfd_3": "Avoid discussing the company-wide risk management system or how these risks and opportunities are identified and managed.",
            "tcfd_4": "Please do not include the process of risk identification, assessment or management in your answer.",
            "tcfd_5": "In your response, focus solely on the resilience of strategy in these scenarios, and refrain from discussing processes of risk identification, assessment, or management strategies.",
            "tcfd_6": "Restrict your answer to the identification and assessment processes, without discussing the management or integration of these risks.",
            "tcfd_7": "Please focus on the concrete actions and strategies implemented to manage these risks, excluding the process of risk identification or assessment.",
            "tcfd_8": "Please focus on the integration aspect and avoid discussing the process of risk identification, assessment, or the specific management actions taken.",
            "tcfd_9": "Do not include information regarding the organization's general risk identification and assessment methods or their broader corporate strategy and initiatives.",
            "tcfd_10": "Confirm whether the organisation discloses its Scope 1, Scope 2, and, if appropriate, Scope 3 greenhouse gas (GHG) emissions. If so, provide any available data or specific figures on these emissions. Additionally, identify the related risks. The risks should be specific to the GHG emissions rather than general climate-related risks.",
            "tcfd_11": "Please detail the precise targets and avoid discussing the company's general risk identification and assessment methods or their commitment to disclosure through the TCFD."
        },
        "greenwashing_signals": [
            "Mention of TCFD without coverage of all four pillars",
            "Use of TCFD branding with no climate risk analysis",
            "No scenario analysis or stress testing",
            "Vague climate commitments without specific targets",
            "Lack of quantitative climate risk metrics"
        ],
        "claim_patterns": [
            "We follow the TCFD framework",
            "Our strategy addresses climate risks as per TCFD",
            "We disclose under TCFD guidance",
            "TCFD-aligned climate risk management"
        ],
        "prompt_snippets": {
            "claims_extraction": "Extract statements that reference TCFD or relate to its four pillars: Governance, Strategy, Risk Management, and Metrics & Targets. Include context or section references.",
            "greenwashing_analysis": "Check whether each TCFD claim aligns with the 11 recommended disclosures. Look for time-bound targets, quantitative risk data, and scenario analysis. Flag incomplete or superficial TCFD references."
        }
    },

    "SASB": {
        "name": "Sustainability Accounting Standards Board",
        "purpose": "Industry-specific sustainability accounting standards",
        "keywords": ["SASB", "Sustainability Accounting Standards Board", "industry standards", "materiality"],
        "indicators": [
            "Sector-specific materiality maps",
            "Standardized ESG metrics",
            "Financial impact disclosures"
        ],
        "greenwashing_signals": [
            "Cites SASB but does not identify industry-specific standards",
            "No financial materiality discussion",
            "Vague reference to SASB without standard naming"
        ],
        "claim_patterns": [
            "We report according to SASB standards",
            "Our disclosures are SASB-aligned",
            "We use SASB materiality guidance"
        ],
        "prompt_snippets": {
            "claims_extraction": "Identify claims that mention SASB standards, especially where industry-specific standards or materiality maps are referenced.",
            "greenwashing_analysis": "Assess if SASB claims identify the relevant sector-specific standards and disclose financially material ESG risks. Flag general SASB mentions lacking specificity."
        }
    }
}
