# TCFD Routing Logic Implementation Summary

## **Overview**

The TCFD routing logic automatically detects when TCFD (Task Force on Climate-related Financial Disclosures) is identified as a major framework and routes the workflow to follow specialized TCFD analysis paths. This ensures that TCFD reports receive the climate-specific, framework-tailored analysis they deserve.

## **How It Works**

### **1. Framework Detection Phase**
- Framework detection identifies all ESG frameworks in the report
- TCFD routing logic analyzes the detection results
- Determines if TCFD is a major framework and its role (primary/secondary)

### **2. TCFD Major Framework Detection**
```python
def is_tcfd_major_framework(self, detected_frameworks: List[str]) -> bool:
    # TCFD is major if:
    # - TCFD is in detected frameworks AND
    # - Confidence >= 70% OR multiple TCFD mentions
```

**Criteria for TCFD as Major Framework:**
- TCFD must be in the detected frameworks list
- Confidence score >= 70% (if available)
- OR multiple TCFD mentions in the framework result
- Default: True if TCFD is detected

### **3. TCFD Analysis Route Determination**
```python
def get_tcfd_analysis_route(self, detected_frameworks: List[str]) -> str:
    # Returns: 'tcfd_primary', 'tcfd_secondary', or 'standard'
```

**Route Logic:**
- **`tcfd_primary`**: TCFD marked as PRIMARY in framework detection
- **`tcfd_secondary`**: TCFD marked as SECONDARY in framework detection
- **`standard`**: TCFD not detected

## **Analysis Routes**

### **🎯 TCFD PRIMARY Analysis Route**

**When Used**: TCFD is identified as the primary framework for the report.

**Specialized Crew**:
- **TCFD Compliance Specialist**: Deep TCFD expertise across all four pillars
- **TCFD Greenwashing Detector**: Climate-specific greenwashing detection

**Analysis Focus**:
1. **Governance (TCFD 1-2)**: Board oversight, management role
2. **Strategy (TCFD 3-5)**: Climate risks, business impact, scenario analysis
3. **Risk Management (TCFD 6-8)**: Risk processes, integration
4. **Metrics & Targets (TCFD 9-11)**: Emissions, targets, performance

**Tools Used**:
- `TCFDAnalyzerTool` with `analysis_type="comprehensive"`
- `FrameworkGlossaryTool` for framework knowledge

**Output**:
- Comprehensive TCFD compliance scores (0-100) for each pillar
- Detailed analysis of each TCFD requirement
- Climate-specific greenwashing indicators
- JSON-formatted results with recommendations

### **🔄 TCFD SECONDARY Analysis Route**

**When Used**: TCFD is identified as a secondary framework alongside other frameworks.

**Enhanced Crew**:
- **ESG Claims Investigator**: Enhanced with TCFD focus
- **Sustainability Compliance Expert**: Enhanced with TCFD greenwashing detection

**Analysis Focus**:
- Climate-related risks, opportunities, and financial impacts
- TCFD alignment assessment
- Climate metrics and targets
- Scenario analysis and resilience assessment
- Framework-specific validation

**Tools Used**:
- `TCFDAnalyzerTool` for TCFD claims
- `GRIAnalyzerTool` for GRI claims
- `FrameworkGlossaryTool` for other frameworks

**Output**:
- Enhanced ESG claims with TCFD focus
- TCFD-specific greenwashing indicators
- Framework-specific compliance validation
- Balanced multi-framework approach

### **📋 Standard Analysis Route**

**When Used**: TCFD is not detected as a major framework.

**Standard Crew**:
- **ESG Claims Investigator**: General ESG analysis
- **Sustainability Compliance Expert**: Standard greenwashing detection

**Analysis Focus**:
- General ESG claims extraction
- Framework-agnostic analysis
- Standard greenwashing detection
- No climate-specific focus

## **Workflow Integration**

### **Main Workflow Changes**

1. **Framework Detection Storage**:
```python
# Store framework result for TCFD routing logic
detector.last_framework_result = framework_result
```

2. **TCFD Routing Logic**:
```python
# Check if TCFD is a major framework and determine analysis route
tcfd_is_major = detector.is_tcfd_major_framework(detected_frameworks)
tcfd_analysis_route = detector.get_tcfd_analysis_route(detected_frameworks)
```

3. **Conditional Crew Creation**:
```python
if tcfd_is_major:
    # Create TCFD specialized crew
    tcfd_crew = detector.create_tcfd_specialized_crew(tcfd_analysis_route)
else:
    # Create standard crew
    chatgpt_crew = Crew(agents=[detector.esg_analyst(), detector.compliance_checker()], ...)
```

### **Chunking Integration**

The TCFD routing logic works seamlessly with the chunking system:
- Each chunk is processed using the appropriate TCFD route
- TCFD analysis is applied to all chunks consistently
- Results are aggregated across chunks

## **Benefits**

### **🎯 For TCFD Reports**
- **Specialized Analysis**: Deep TCFD expertise and climate focus
- **Framework-Specific Tools**: TCFDAnalyzerTool for comprehensive analysis
- **Climate Greenwashing Detection**: Specialized climate-specific criteria
- **Comprehensive Coverage**: All four TCFD pillars analyzed
- **Financial Impact Focus**: Emphasis on climate-financial integration

### **🔄 For Multi-Framework Reports**
- **Balanced Approach**: TCFD analysis alongside other frameworks
- **Enhanced Climate Focus**: Climate-specific analysis even when TCFD is secondary
- **Framework-Specific Validation**: Each framework gets appropriate analysis
- **Comprehensive Coverage**: All frameworks analyzed with appropriate depth

### **📋 For Non-TCFD Reports**
- **Standard Analysis**: No unnecessary complexity
- **Efficient Processing**: Standard workflow for non-climate reports
- **Framework-Agnostic**: General ESG analysis approach

## **Example Scenarios**

### **Scenario 1: Pure TCFD Report**
```
Framework Detection: TCFD (PRIMARY, 95% confidence)
Route: tcfd_primary
Analysis: Specialized TCFD Compliance Specialist + TCFD Greenwashing Detector
Focus: All four TCFD pillars with deep climate expertise
```

### **Scenario 2: GRI Report with TCFD Climate Section**
```
Framework Detection: GRI (PRIMARY), TCFD (SECONDARY, 85% confidence)
Route: tcfd_secondary
Analysis: Enhanced ESG Claims Investigator + Sustainability Compliance Expert
Focus: GRI analysis with enhanced TCFD climate focus
```

### **Scenario 3: General ESG Report**
```
Framework Detection: GRI (PRIMARY), SASB (SECONDARY)
Route: standard
Analysis: Standard ESG Claims Investigator + Sustainability Compliance Expert
Focus: General ESG analysis without climate specialization
```

## **Technical Implementation**

### **Key Methods**
- `is_tcfd_major_framework()`: Determines if TCFD is major
- `get_tcfd_analysis_route()`: Determines analysis route
- `create_tcfd_specialized_crew()`: Creates specialized crews

### **Integration Points**
- Framework detection result storage
- Conditional crew creation in main workflow
- Chunk processing with appropriate routes
- Result aggregation across chunks

### **Error Handling**
- Graceful fallback to standard analysis if TCFD routing fails
- Logging of TCFD routing decisions
- Exception handling for crew creation

## **Expected Results**

### **For TCFD Reports**
- ✅ Specialized TCFD analysis with deep climate expertise
- ✅ Comprehensive coverage of all four TCFD pillars
- ✅ Climate-specific greenwashing detection
- ✅ Financial impact integration assessment
- ✅ Scenario analysis quality evaluation

### **For Multi-Framework Reports**
- ✅ Enhanced TCFD analysis alongside other frameworks
- ✅ Climate-focused ESG claims extraction
- ✅ Framework-specific validation
- ✅ Balanced multi-framework approach

### **For Non-TCFD Reports**
- ✅ Standard ESG analysis without unnecessary complexity
- ✅ Efficient processing with appropriate focus
- ✅ Framework-agnostic greenwashing detection

This TCFD routing logic ensures that climate-focused reports receive the specialized analysis they need while maintaining efficiency for other types of sustainability reports. 