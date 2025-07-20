# End-to-End Greenwashing Detection Workflow Diagram

## 📋 **Complete Workflow Overview**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GREENWASHING DETECTOR WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INPUT STAGE   │    │  OLLAMA STAGE   │    │  CHATGPT STAGE  │    │  OUTPUT STAGE   │
│                 │    │                 │    │                 │    │                 │
│ PDF Upload      │───▶│ Framework       │───▶│ ESG Analysis    │───▶│ Markdown        │
│                 │    │ Detection       │    │ & Claims        │    │ Reports         │
│ Text Extraction │    │ Structure ID    │    │ Validation      │    │ JSON Logs       │
│                 │    │ Section Filter  │    │                 │    │ Summary Files   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 **Detailed Flow Breakdown**

### **STAGE 1: INPUT PROCESSING**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                INPUT STAGE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. PDF Upload                                                                   │
│    ├── FullPDFReader._run(pdf_path)                                            │
│    ├── OCR Processing (if needed)                                              │
│    ├── Table of Contents Detection                                             │
│    └── Text Extraction                                                         │
│                                                                                 │
│ 2. Content Preparation                                                          │
│    ├── Raw text extraction                                                     │
│    ├── Character count: ~100K-500K                                             │
│    ├── Estimated tokens: ~30K-150K                                             │
│    └── Smart chunking for Ollama                                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **STAGE 2: OLLAMA PROCESSING (Framework Detection)**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              OLLAMA STAGE                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. Structure Identifier Agent (llama2:latest)                                  │
│    ├── Task: extract_report_structure                                          │
│    ├── Input: {report_content}                                                 │
│    ├── Output: TOC/section titles                                              │
│    └── Token usage: ~500-1000                                                  │
│                                                                                 │
│ 2. Section Filter Agent (llama2:latest)                                        │
│    ├── Task: extract_framework_sections                                        │
│    ├── Input: {report_content}                                                 │
│    ├── Output: Framework-relevant sections                                     │
│    └── Token usage: ~500-1000                                                  │
│                                                                                 │
│ 3. Framework Detector Agent (llama2:latest)                                    │
│    ├── Task: detect_reporting_framework                                        │
│    ├── Input: {report_content}                                                 │
│    ├── Output: Framework list with roles/confidence                            │
│    └── Token usage: ~500-1000                                                  │
│                                                                                 │
│ 4. Framework Analysis                                                           │
│    ├── TCFD Detection: Is TCFD PRIMARY?                                        │
│    ├── Routing Decision: TCFD vs Standard                                      │
│    └── Framework Logging & Markdown Saving                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **STAGE 3: FLUFF REMOVAL (Ollama)**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            FLUFF REMOVAL STAGE                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. Fluff Remover Agent (llama2:latest)                                         │
│    ├── Task: remove_report_fluff                                               │
│    ├── Input: {report_content, detected_frameworks}                            │
│    ├── Output: Cleaned ESG-relevant content                                    │
│    └── Token usage: ~500-1000                                                  │
│                                                                                 │
│ 2. Content Processing                                                           │
│    ├── Remove marketing filler                                                 │
│    ├── Preserve ESG frameworks, emissions, targets                             │
│    ├── Preserve governance, risk assessments                                   │
│    └── Output: ~50K-200K characters                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **STAGE 4: CHATGPT PROCESSING (ESG Analysis & Claims Validation)**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CHATGPT STAGE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. Content Chunking for ChatGPT                                                │
│    ├── Input: Cleaned content (~50K-200K chars)                               │
│    ├── Chunk size: 6000 tokens max                                            │
│    ├── Character multiplier: 2.0x (conservative)                              │
│    ├── Overlap: 50 characters                                                  │
│    └── Output: Multiple chunks (~10K chars each)                              │
│                                                                                 │
│ 2. TCFD Routing Logic                                                          │
│    ├── Is TCFD PRIMARY framework?                                              │
│    │   ├── YES: Use TCFD Specialized Crew                                     │
│    │   └── NO: Use Standard Analysis Crew                                     │
│    └── Analysis Route: Primary vs Secondary                                    │
│                                                                                 │
│ 3A. TCFD Specialized Analysis (if TCFD is PRIMARY)                            │
│    ├── TCFD Specialized Crew                                                   │
│    ├── Agents: TCFD Analyst, Compliance Checker                               │
│    ├── Tools: TCFDAnalyzerTool                                                 │
│    └── Output: TCFD-specific analysis                                         │
│                                                                                 │
│ 3B. Standard Analysis (if TCFD is not PRIMARY)                                │
│    ├── ESG Analyst Agent (gpt-3.5-turbo-0125)                                 │
│    │   ├── Task: extract_esg_claims                                           │
│    │   ├── Input: {esg_content} (chunk)                                       │
│    │   ├── Tools: TCFDAnalyzerTool, GRIAnalyzerTool, FrameworkGlossaryTool    │
│    │   └── Output: ESG claims extraction                                       │
│    │                                                                           │
│    ├── Claims Validation                                                       │
│    │   ├── ESG output chunking (4000 tokens max)                              │
│    │   ├── Compliance Checker Agent (gpt-3.5-turbo-0125)                      │
│    │   ├── Task: validate_claims                                              │
│    │   ├── Input: {esg_analyst_output} (chunked)                              │
│    │   └── Output: Greenwashing analysis                                       │
│    └── Combined Results                                                        │
│                                                                                 │
│ 4. Chunk Processing Loop                                                       │
│    ├── For each chunk:                                                         │
│    │   ├── Process with appropriate crew                                      │
│    │   ├── Save individual results                                             │
│    │   └── Track processing time                                               │
│    └── Combine all chunk results                                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **STAGE 5: OUTPUT GENERATION**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT STAGE                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. Markdown Report Generation                                                   │
│    ├── Framework Detection Results                                             │
│    ├── Fluff Removal Summary                                                   │
│    ├── ESG Analysis Results                                                    │
│    ├── Claims Validation Results                                               │
│    └── Processing Summary                                                      │
│                                                                                 │
│ 2. Individual Agent Outputs                                                    │
│    ├── save_agent_output_to_md()                                               │
│    ├── Framework detector output                                               │
│    ├── ESG analyst output                                                      │
│    ├── Compliance checker output                                               │
│    └── Enhanced workflow summary                                               │
│                                                                                 │
│ 3. JSON Logging                                                                 │
│    ├── Framework detection logs                                                │
│    ├── Processing timestamps                                                   │
│    ├── Error logs                                                              │
│    └── Performance metrics                                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 **Tool Integration Points**

### **Available Tools**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                TOOLS                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ 1. TCFDAnalyzerTool                                                             │
│    ├── Purpose: TCFD compliance analysis                                       │
│    ├── Arguments: report_content, analysis_type, pillar                        │
│    ├── Usage: When TCFD framework detected                                     │
│    └── Agent: ESG Analyst                                                      │
│                                                                                 │
│ 2. GRIAnalyzerTool                                                              │
│    ├── Purpose: GRI compliance analysis                                        │
│    ├── Arguments: report_content, analysis_type, disclosure_id, company_info  │
│    ├── Usage: When GRI framework detected                                      │
│    └── Agent: ESG Analyst                                                      │
│                                                                                 │
│ 3. FrameworkGlossaryTool                                                        │
│    ├── Purpose: Framework descriptions and identifiers                         │
│    ├── Arguments: query                                                        │
│    ├── Usage: General framework information                                    │
│    └── Agent: ESG Analyst                                                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## ⚠️ **Current Error Analysis**

### **Error Location**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ERROR ANALYSIS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ Error occurs in: ChatGPT Stage - ESG Analysis                                  │
│                                                                                 │
│ 1. ESG Analyst Agent                                                           │
│    ├── Task: extract_esg_claims                                                │
│    ├── Tools: TCFDAnalyzerTool, GRIAnalyzerTool, FrameworkGlossaryTool        │
│    ├── Error: "Action 'the action to take' don't exist"                       │
│    └── Fallback: Manual extraction                                             │
│                                                                                 │
│ 2. Compliance Checker Agent                                                    │
│    ├── Task: validate_claims                                                   │
│    ├── Input: {esg_analyst_output}                                             │
│    ├── Error: Receives manual extraction instead of structured analysis        │
│    └── Result: Incomplete validation                                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **Tool Configuration Issues**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TOOL CONFIGURATION                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ Problem: Tools not properly configured in agent                                │
│                                                                                 │
│ 1. ESG Analyst Agent                                                           │
│    ├── Expected: Tools available for use                                       │
│    ├── Actual: Tools not accessible                                            │
│    ├── Result: Manual extraction fallback                                      │
│    └── Impact: Loss of framework-specific analysis                             │
│                                                                                 │
│ 2. Tool Registration                                                            │
│    ├── Tools defined in tools/ directory                                       │
│    ├── Tools imported in crew.py                                               │
│    ├── Tools assigned to agents                                                │
│    └── Tools accessible during execution                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📊 **Token Usage Breakdown**

### **Per Stage Token Consumption**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            TOKEN USAGE                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ Ollama Stage (llama2:latest)                                                   │
│ ├── Structure Identifier: ~500-1000 tokens                                     │
│ ├── Section Filter: ~500-1000 tokens                                           │
│ ├── Framework Detector: ~500-1000 tokens                                       │
│ ├── Fluff Remover: ~500-1000 tokens                                            │
│ └── Total Ollama: ~2000-4000 tokens                                            │
│                                                                                 │
│ ChatGPT Stage (gpt-3.5-turbo-0125)                                             │
│ ├── Task Description: ~200-300 tokens                                          │
│ ├── Content Chunk: ~10,000 tokens max                                          │
│ ├── Agent Instructions: ~500-1000 tokens                                       │
│ ├── Tool Descriptions: ~200-500 tokens                                         │
│ └── Total ChatGPT: ~11,000-12,000 tokens per chunk                             │
│                                                                                 │
│ Safety Margin: ~4,000-5,000 tokens                                             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔍 **Manual Analysis Points**

### **Key Decision Points**
1. **Framework Detection**: Is TCFD PRIMARY or SECONDARY?
2. **Routing Logic**: Which analysis path to take?
3. **Chunking**: How many chunks created?
4. **Tool Usage**: Are tools properly configured?
5. **Content Processing**: Is content being passed correctly?

### **Error Investigation Points**
1. **Tool Registration**: Are tools properly imported and assigned?
2. **Agent Configuration**: Are agents configured with correct tools?
3. **Task Descriptions**: Are template variables correct?
4. **Content Flow**: Is content being passed between stages correctly?
5. **Token Limits**: Are chunks staying within limits?

This diagram shows the complete end-to-end flow and highlights where the current error is occurring in the ChatGPT stage during ESG analysis. 