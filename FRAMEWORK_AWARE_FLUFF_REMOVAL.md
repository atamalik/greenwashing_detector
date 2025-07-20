# Framework-Aware Fluff Removal: Preserving Critical Content for Analysis

## Overview

The fluff remover has been enhanced to be framework-aware, ensuring that when TCFD or GRI frameworks are detected, all relevant content is preserved for downstream analysis by the specialized framework analyzers.

## Problem Solved

Previously, the fluff remover could potentially remove critical framework-specific content that would be needed by the TCFD and GRI analyzers, leading to incomplete analysis and inaccurate results.

## Solution Implemented

### 1. **Framework Detection Integration**
- Framework detection runs first in the workflow
- Detected frameworks are extracted with confidence scores
- Framework information is passed to the fluff remover

### 2. **Framework-Aware Content Preservation**
- **TCFD Content Preservation**: All climate-related discussions, board oversight, emissions data, scenario analysis, and TCFD-specific indicators (tcfd_1 through tcfd_11)
- **GRI Content Preservation**: All GRI indicator mentions (GRI 102, 305, 403, 401, 413, 414, 302, 306, 307, 308), material topics, stakeholder engagement, and reporting methodology

### 3. **Intelligent Pattern Recognition**
- Keyword-based detection for framework content
- Indicator-specific pattern matching
- Confidence-based framework extraction

## Implementation Details

### Enhanced FluffRemover Tool

```python
class FluffRemover(BaseTool):
    def __init__(self):
        super().__init__()
        self._framework_content_patterns = self._initialize_framework_patterns()
    
    def _run(self, report_text: str, detected_frameworks: List[str] = None) -> str:
        # Framework-aware processing
        pass
```

### Framework Content Patterns

**TCFD Patterns:**
- **Keywords**: climate-related, climate risk, TCFD, Scope 1/2/3, GHG, emissions, etc.
- **Indicators**: tcfd_1 through tcfd_11
- **Sections**: climate, emissions, governance, risk management, strategy, metrics, targets

**GRI Patterns:**
- **Keywords**: GRI, Global Reporting Initiative, material topics, stakeholder engagement, etc.
- **Indicators**: GRI 102, 305, 403, 401, 413, 414, 302, 306, 307, 308
- **Sections**: gri, sustainability, environmental, social, governance, materiality

### Framework Extraction Method

```python
def _extract_detected_frameworks(self, framework_result) -> List[str]:
    """
    Extract detected frameworks from the framework detection result.
    Only includes frameworks with confidence >= 40%.
    """
    # Pattern matching with confidence scoring
    # Returns list of detected frameworks
```

## Workflow Integration

### 1. **Framework Detection Phase**
```
Ollama Model → Framework Detection → Confidence Scores → Framework Extraction
```

### 2. **Framework-Aware Fluff Removal Phase**
```
Detected Frameworks + Full Text → Framework-Aware Prompt → Preserved Content
```

### 3. **ESG Analysis Phase**
```
Preserved Content → TCFDAnalyzerTool → GRI AnalyzerTool → Complete Analysis
```

## Framework-Specific Preservation Rules

### TCFD Content - MUST PRESERVE:
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

### GRI Content - MUST PRESERVE:
- All GRI indicator mentions (GRI 102, 305, 403, 401, 413, 414, 302, 306, 307, 308)
- Material topics and stakeholder engagement processes
- Specific GRI disclosures and reporting methodology
- Environmental performance data (emissions, energy, waste, water)
- Social performance data (employment, health & safety, community)
- Governance disclosures and compliance information
- Any mention of "GRI", "Global Reporting Initiative", "materiality", "stakeholder"
- Specific quantitative data related to GRI indicators
- Reporting boundaries and methodology explanations

## Enhanced Task Configuration

The `remove_report_fluff` task now includes:

```yaml
remove_report_fluff:
  description: >
    **CRITICAL FRAMEWORK PRESERVATION**: If TCFD or GRI frameworks are detected, 
    you MUST preserve ALL content related to these frameworks as it will be 
    analyzed by specialized tools.
    
    [Detailed preservation rules for TCFD and GRI content]
    
    Report content to clean: {report_content}
    Detected frameworks to preserve: {detected_frameworks}
```

## Benefits

### 1. **Complete Analysis**
- No framework content is lost during fluff removal
- Framework analyzers receive complete information
- Accurate compliance assessment and greenwashing detection

### 2. **Intelligent Processing**
- Content preservation based on detected frameworks
- Automatic framework detection and extraction
- Confidence-based framework inclusion

### 3. **Scalable Architecture**
- Easy to add new frameworks
- Framework-specific preservation rules
- Consistent processing across all frameworks

### 4. **Quality Assurance**
- Framework content is preserved verbatim
- No paraphrasing or summarization of critical content
- Maintains original structure and context

## Testing Results

The framework-aware fluff removal has been tested and verified:

- ✅ TCFD content detection: Working
- ✅ GRI content detection: Working
- ✅ Framework extraction: Working (GRI, TCFD, CDP detected)
- ✅ Framework-aware prompt generation: Working
- ✅ Workflow integration: Working

**Test Results:**
- TCFD keywords: 28 keywords
- TCFD indicators: 11 indicators
- GRI keywords: 25 keywords
- GRI indicators: 10 indicators
- Framework extraction accuracy: High (confidence-based filtering)

## Future Enhancements

### 1. **Additional Frameworks**
- SASB-specific preservation rules
- CSRD/ESRS content preservation
- ISO 14064 preservation patterns

### 2. **Advanced Pattern Recognition**
- Machine learning-based content classification
- Semantic analysis for framework content
- Context-aware preservation rules

### 3. **Performance Optimization**
- Caching of framework patterns
- Parallel processing for large documents
- Incremental content analysis

## Conclusion

The framework-aware fluff removal ensures that critical ESG framework content is never lost during the cleaning process, enabling accurate and comprehensive analysis by the specialized TCFD and GRI analyzers. This enhancement significantly improves the quality and reliability of the greenwashing detection system. 