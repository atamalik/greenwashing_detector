# Integrated TCFD Approach: ESG Analyst with Framework-Specific Tools

## Overview

Instead of creating separate agents for each ESG framework, we've integrated sophisticated TCFD analysis capabilities directly into the existing ESG Analyst agent. This approach provides a scalable, maintainable architecture that can easily accommodate additional frameworks in the future.

## Key Benefits

### 1. **Scalable Architecture**
- **Single Agent, Multiple Tools**: One ESG Analyst agent handles all frameworks
- **Easy Framework Addition**: New frameworks can be added as tools without creating new agents
- **Consistent Analysis Quality**: All framework analysis follows the same high standards

### 2. **Sophisticated TCFD Analysis**
- **Chatreport-Inspired Prompts**: Advanced TCFD prompts based on the Chatreport research project
- **Comprehensive Assessment**: Analyzes all four TCFD pillars (Governance, Strategy, Risk Management, Metrics & Targets)
- **Compliance Scoring**: Provides detailed compliance scores (0-100) for each pillar
- **Greenwashing Detection**: Identifies potential greenwashing signals within TCFD disclosures

### 3. **Dynamic Framework Detection**
- **Intelligent Tool Selection**: ESG Analyst automatically uses appropriate tools based on detected frameworks
- **Framework-Specific Analysis**: Different analysis approaches for TCFD, GRI, SASB, etc.
- **Comprehensive Coverage**: Ensures no framework is overlooked in the analysis

## Implementation Details

### ESG Analyst Agent Configuration

```python
@agent
def esg_analyst(self) -> Agent:
    config = self.agents_config['esg_analyst'].copy()
    if 'tools' in config:
        del config['tools']
    return Agent(
        **config,
        tools=[
            self.tools["FullPDFReader"](),
            self.tools["TCFDAnalyzerTool"](),
            self.tools["FrameworkGlossaryTool"]()
        ]
    )
```

### Framework-Specific Task Description

The ESG claims extraction task now includes intelligent framework-specific analysis:

```yaml
extract_esg_claims:
  description: >
    FRAMEWORK-SPECIFIC ANALYSIS:
    Based on the frameworks detected in the report, perform additional specialized analysis:
    
    - If TCFD (Task Force on Climate-related Financial Disclosures) is detected: 
      Use the TCFDAnalyzerTool to perform detailed TCFD compliance analysis across all four pillars 
      (Governance, Strategy, Risk Management, Metrics & Targets). Provide compliance scores, 
      identify missing elements, and detect potential greenwashing signals.
    
    - If GRI Standards are detected: 
      Use the FrameworkGlossaryTool to understand GRI requirements and assess alignment 
      with specific GRI indicators mentioned in the report.
    
    - If SASB is detected: 
      Use the FrameworkGlossaryTool to evaluate industry-specific materiality and 
      financial impact disclosures.
```

## TCFD Analysis Capabilities

### 1. **Pillar-Specific Analysis**
- **TCFD_1**: Board oversight of climate-related risks and opportunities
- **TCFD_2**: Management's role in assessing and managing climate-related risks
- **TCFD_3**: Climate-related risks and opportunities identified by the organization
- **TCFD_4**: Impact of climate-related risks and opportunities on business strategy
- **TCFD_5**: Resilience of strategy considering different climate-related scenarios
- **TCFD_6**: Processes for identifying and assessing climate-related risks
- **TCFD_7**: Integration of climate-related risks into overall risk management
- **TCFD_8**: Metrics used to assess climate-related risks and opportunities
- **TCFD_9**: Scope 1, Scope 2, and Scope 3 greenhouse gas emissions
- **TCFD_10**: Targets used to manage climate-related risks and opportunities
- **TCFD_11**: Performance against climate-related targets

### 2. **Comprehensive Analysis**
- **Overall Compliance Score**: 0-100 score across all pillars
- **Missing Disclosures**: Identification of required elements not addressed
- **Greenwashing Indicators**: Detection of vague or unverifiable claims
- **Recommendations**: Specific improvement suggestions

### 3. **Advanced Prompt Engineering**
- **Chatreport-Style Prompts**: Sophisticated prompts that guide the LLM to provide structured analysis
- **JSON Output Formatting**: Structured outputs for easy parsing and integration
- **Evidence-Based Analysis**: Requires specific page references and supporting quotes

## Workflow Integration

### 1. **Framework Detection Phase**
```
Ollama Model (llama2:latest) → Framework Detection → Confidence Scores
```

### 2. **ESG Analysis Phase**
```
ChatGPT (gpt-3.5-turbo-0125) + Framework Tools → Comprehensive Analysis
```

**For TCFD Detection:**
- Uses TCFDAnalyzerTool for detailed compliance assessment
- Analyzes all four pillars with specific criteria
- Provides compliance scores and missing elements
- Detects greenwashing signals

**For GRI Detection:**
- Uses FrameworkGlossaryTool for GRI standards understanding
- Assesses alignment with specific GRI indicators
- Evaluates reporting quality and completeness

**For SASB Detection:**
- Uses FrameworkGlossaryTool for industry-specific standards
- Evaluates financial materiality disclosures
- Assesses sector-specific metrics

### 3. **Claims Validation Phase**
```
ChatGPT (gpt-3.5-turbo-0125) → Framework-Specific Validation → Greenwashing Assessment
```

## Future Framework Integration

### Adding New Frameworks

To add a new framework (e.g., CSRD/ESRS), simply:

1. **Create Framework Tool**:
```python
class CSRDAnalyzerTool(BaseTool):
    name = "CSRDAnalyzerTool"
    description = "Analyzes CSRD/ESRS compliance..."
    
    def _run(self, report_content: str, analysis_type: str = "comprehensive"):
        # CSRD-specific analysis logic
        pass
```

2. **Add to ESG Analyst Tools**:
```python
tools=[
    self.tools["FullPDFReader"](),
    self.tools["TCFDAnalyzerTool"](),
    self.tools["CSRDAnalyzerTool"](),  # New framework
    self.tools["FrameworkGlossaryTool"]()
]
```

3. **Update Task Description**:
```yaml
- If CSRD/ESRS is detected: Use the CSRDAnalyzerTool for EU sustainability reporting compliance...
```

### Benefits of This Approach

- **No New Agents**: Maintains clean, simple architecture
- **Consistent Interface**: All framework analysis follows the same pattern
- **Easy Testing**: Framework tools can be tested independently
- **Modular Design**: Each framework tool is self-contained

## Comparison: Integrated vs. Separate Agents

| Aspect | Integrated Approach | Separate Agents |
|--------|-------------------|-----------------|
| **Scalability** | ✅ Easy to add frameworks | ❌ New agent per framework |
| **Maintenance** | ✅ Single agent to maintain | ❌ Multiple agents to maintain |
| **Consistency** | ✅ Unified analysis approach | ❌ Potential inconsistencies |
| **Resource Usage** | ✅ Efficient tool sharing | ❌ Duplicate agent overhead |
| **Testing** | ✅ Framework tools testable independently | ❌ Each agent requires full testing |
| **Code Reuse** | ✅ Common functionality shared | ❌ Potential code duplication |

## Conclusion

The integrated TCFD approach provides a sophisticated, scalable solution that:

1. **Leverages Advanced TCFD Analysis**: Uses Chatreport-inspired prompts for comprehensive compliance assessment
2. **Maintains Clean Architecture**: Single ESG analyst with multiple specialized tools
3. **Enables Easy Expansion**: New frameworks can be added as tools without architectural changes
4. **Ensures Quality**: Consistent analysis standards across all frameworks
5. **Optimizes Resources**: Efficient use of LLM calls and processing time

This approach represents the best practice for ESG framework analysis, combining sophistication with scalability. 