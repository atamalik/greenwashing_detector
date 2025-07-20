# Greenwashing Detection Workflow Documentation

**Generated:** 2025-07-06 13:30:00  
**Version:** Enhanced Workflow with Ollama Integration  
**System:** ESG Framework Detection and Greenwashing Analysis

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Workflow Stages](#workflow-stages)
4. [Agent Descriptions](#agent-descriptions)
5. [Tool Descriptions](#tool-descriptions)
6. [Configuration](#configuration)
7. [Execution Flow](#execution-flow)
8. [Output Files](#output-files)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)

## Overview

The Greenwashing Detection System is a comprehensive AI-powered analysis pipeline designed to detect ESG (Environmental, Social, and Governance) reporting frameworks and identify potential greenwashing in corporate sustainability reports. The system uses a hybrid approach combining local Ollama models for initial processing and OpenAI models for detailed analysis.

### Key Features

- **Smart PDF Processing**: OCR-enabled text extraction with Table of Contents detection
- **Framework Detection**: Identifies ESG reporting standards (GRI, TCFD, SASB, etc.)
- **Intelligent Chunking**: Processes large documents without token limits
- **Fluff Removal**: Eliminates marketing language while preserving ESG content
- **Claims Extraction**: Identifies key sustainability claims
- **Greenwashing Validation**: Assesses claims against compliance standards
- **Comprehensive Logging**: Detailed execution tracking and output generation

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Upload    │───▶│  Smart Chunking │───▶│ Framework Det.  │
│                 │    │   (OCR + TOC)   │    │   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Output Files  │◀───│ Claims Analysis │◀───│ Fluff Removal   │
│   (Markdown)    │    │   (ChatGPT)     │    │   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Model Usage Strategy

- **Ollama (llama2:latest)**: Framework detection, structure identification, fluff removal
- **ChatGPT (gpt-3.5-turbo-0125)**: ESG claims extraction, greenwashing validation
- **Hybrid Approach**: Local processing for initial tasks, cloud-based for detailed analysis

## Workflow Stages

### Stage 1: Framework Detection (Ollama)
**Purpose**: Identify ESG reporting frameworks used in the document

**Process**:
1. Extract PDF content using smart chunking
2. Focus on framework-relevant sections (About this Report, Methodology, etc.)
3. Analyze content for framework mentions (GRI, TCFD, SASB, CDP, etc.)
4. Generate confidence scores and supporting evidence

**Output**: List of detected frameworks with confidence scores

### Stage 2: Fluff Removal (Ollama)
**Purpose**: Remove marketing language while preserving ESG content

**Process**:
1. Extract full PDF text
2. Apply surgical content filtering
3. Retain ESG-relevant statements, metrics, and claims
4. Remove promotional content and boilerplate

**Output**: Cleaned content optimized for analysis

### Stage 3: ChatGPT Chunking
**Purpose**: Prepare cleaned content for ChatGPT analysis

**Process**:
1. Apply intelligent chunking (16K token limit)
2. Maintain sentence boundaries and context
3. Add processing instructions for each chunk
4. Ensure comprehensive coverage

**Output**: Chunked content ready for ChatGPT processing

### Stage 4: ESG Analysis (ChatGPT)
**Purpose**: Extract key sustainability claims from the document

**Process**:
1. Analyze all chunks for ESG-related claims
2. Focus on environmental, social, and governance statements
3. Identify specific commitments, targets, and achievements
4. Extract up to 5 key claims with context

**Output**: Structured list of ESG claims

### Stage 5: Claims Validation (ChatGPT)
**Purpose**: Assess claims for potential greenwashing

**Process**:
1. Evaluate each claim against ESG frameworks
2. Check for specificity, measurability, and time-bound commitments
3. Assess alignment with recognized standards
4. Flag potential greenwashing with confidence scores

**Output**: Greenwashing assessment report

## Agent Descriptions

### 1. Structure Identifier (Ollama)
- **Role**: ESG Report Structure Identifier
- **Goal**: Detect and extract report structure, Table of Contents, and key section headers
- **Tools**: None (content provided directly)
- **Output**: Structured list of sections and page references

### 2. Section Filter (Ollama)
- **Role**: ESG Report Section Extractor
- **Goal**: Identify sections most likely to mention ESG frameworks
- **Tools**: None (content provided directly)
- **Output**: Framework-relevant sections and paragraphs

### 3. Framework Detector (Ollama)
- **Role**: ESG Framework Identifier
- **Goal**: Detect ESG reporting frameworks with supporting evidence
- **Tools**: None (content provided directly)
- **Output**: Framework list with confidence scores and quotes

### 4. Fluff Remover (Ollama)
- **Role**: ESG Intelligence Extractor
- **Goal**: Remove marketing language while preserving ESG content
- **Tools**: None (content provided directly)
- **Output**: Cleaned, analysis-ready content

### 5. ESG Analyst (ChatGPT)
- **Role**: ESG Claims Investigator
- **Goal**: Extract key ESG-related claims from sustainability reports
- **Tools**: FullPDFReader (for content extraction)
- **Output**: Structured list of ESG claims

### 6. Compliance Checker (ChatGPT)
- **Role**: Sustainability Compliance Expert
- **Goal**: Assess claims for greenwashing using global standards
- **Tools**: None (web search disabled)
- **Output**: Greenwashing validation report

## Tool Descriptions

### FrameworkPDFReader
- **Purpose**: Enhanced PDF reader with smart chunking for framework detection
- **Features**: OCR, TOC detection, framework-relevant content extraction
- **Output**: Chunked content focused on framework mentions

### FullPDFReader
- **Purpose**: Comprehensive PDF reader for ESG analysis
- **Features**: Full text extraction with result aggregation
- **Output**: Complete document content for analysis

### FrameworkGlossaryTool
- **Purpose**: Provides ESG framework descriptions and identifiers
- **Features**: Framework definitions, key indicators, detection guidance
- **Output**: Framework information for analysis

### RelevantSectionExtractor
- **Purpose**: Extract sections most likely to contain framework mentions
- **Features**: Keyword-based filtering, section identification
- **Output**: Framework-relevant content sections

### FluffRemover
- **Purpose**: Remove non-essential content while preserving ESG information
- **Features**: Surgical content filtering, ESG content preservation
- **Output**: Cleaned content for analysis

## Configuration

### Agent Configuration (agents.yaml)
```yaml
framework_detector:
  role: ESG Framework Identifier
  goal: Detect ESG reporting frameworks
  llm: ollama/llama2:latest
  memory: true
  verbose: true
```

### Task Configuration (tasks.yaml)
```yaml
detect_reporting_framework:
  description: Analyze content for ESG frameworks
  expected_output: Framework list with confidence scores
  agent: framework_detector
```

### Model Configuration
- **Ollama**: Local model for initial processing
- **ChatGPT**: Cloud model for detailed analysis
- **Hybrid**: Optimized for cost and performance

## Execution Flow

### 1. Initialization
```python
detector = GreenwashingDetector()
detector.log_framework_detection_start(pdf_path)
```

### 2. Content Extraction
```python
pdf_reader = FrameworkPDFReader()
report_content = pdf_reader._run(pdf_path)
```

### 3. Framework Detection
```python
framework_crew = Crew(
    agents=[detector.framework_detector()],
    tasks=[detector.detect_reporting_framework()],
    process=Process.sequential
)
framework_result = framework_crew.kickoff(inputs={"report_content": report_content})
```

### 4. Fluff Removal
```python
fluff_crew = Crew(
    agents=[detector.fluff_remover()],
    tasks=[detector.remove_report_fluff()],
    process=Process.sequential
)
fluff_result = fluff_crew.kickoff(inputs={"report_content": full_text})
```

### 5. ChatGPT Analysis
```python
chatgpt_crew = Crew(
    agents=[detector.esg_analyst(), detector.compliance_checker()],
    tasks=[detector.extract_esg_claims(), detector.validate_claims()],
    process=Process.sequential
)
chatgpt_result = chatgpt_crew.kickoff(inputs={"esg_content": chatgpt_content})
```

### 6. Output Generation
```python
detector.save_framework_detection_to_md(framework_result, pdf_path)
detector.save_enhanced_workflow_summary_to_md(framework_result, fluff_result, chatgpt_result, pdf_path)
```

## Output Files

### Generated Files
1. **framework_detection_{timestamp}.md**: Detailed framework detection report
2. **framework_results_{timestamp}.md**: Simple framework results
3. **enhanced_workflow_summary_{timestamp}.md**: Complete workflow summary
4. **{agent}_{task}_{timestamp}.md**: Individual agent outputs
5. **framework_detection_{timestamp}.json**: Framework detection logs

### File Locations
- **Output Directory**: `/output/`
- **Logs Directory**: `/framework_logs/`
- **Uploads Directory**: `/uploaded_reports/`

### Output Format
```markdown
# Framework Detection Report

**Generated:** 2025-07-06 13:30:00
**PDF File:** sustainability_report.pdf

## Detected Frameworks

- **GRI Standards**: Mentioned explicitly. **Confidence**: 98%
- **TCFD**: Climate risk alignment indicators. **Confidence**: 85%
- **CDP**: Not mentioned. **Confidence**: 10%

## Analysis Summary

Detection method: Smart chunking with framework focus
Target frameworks: GRI, TCFD, SASB, CDP, CSRD, ESRS, ISO 14064
```

## Troubleshooting

### Common Issues

#### 1. Ollama Tool Calling Errors
**Problem**: `IndexError: list index out of range`
**Solution**: Ollama models don't support tool calls. Use content extraction in Python instead.

#### 2. Token Limit Exceeded
**Problem**: Context length exceeded errors
**Solution**: Ensure chunking is applied. Check chunk sizes in configuration.

#### 3. PDF Extraction Failures
**Problem**: OCR or text extraction errors
**Solution**: Check PDF format. Use fallback extraction methods.

#### 4. Model Connection Issues
**Problem**: Ollama or OpenAI API errors
**Solution**: Verify model availability and API keys.

### Debug Steps
1. Check log files in `/framework_logs/`
2. Verify model availability: `ollama list`
3. Test individual components with test scripts
4. Check input file format and size

## Performance Optimization

### Chunking Strategy
- **Framework Detection**: 2000 tokens, 200 overlap, max 3 chunks
- **ESG Analysis**: 3500 tokens, 300 overlap, max 5 chunks
- **ChatGPT**: 14000 tokens, 1000 overlap, sentence boundaries

### Model Selection
- **Ollama**: Fast, local, cost-effective for initial processing
- **ChatGPT**: High-quality analysis for complex tasks
- **Hybrid**: Optimized for performance and cost

### Caching Strategy
- **Content Extraction**: Cache extracted content
- **Framework Detection**: Cache detection results
- **Chunking**: Reuse chunks across tasks

### Monitoring
- **Execution Time**: Track processing time per stage
- **Token Usage**: Monitor token consumption
- **Quality Metrics**: Track confidence scores and accuracy

## Future Enhancements

### Planned Features
1. **Multi-language Support**: Non-English report analysis
2. **Visual Content Analysis**: Chart and image interpretation
3. **Real-time Monitoring**: Live analysis dashboard
4. **Custom Framework Training**: Domain-specific framework detection
5. **Batch Processing**: Multiple report analysis

### Performance Improvements
1. **Parallel Processing**: Concurrent agent execution
2. **Streaming Analysis**: Real-time content processing
3. **Advanced Caching**: Intelligent result caching
4. **Model Optimization**: Fine-tuned models for specific tasks

---

*This documentation is generated by the Greenwashing Detection Analysis System. For technical support or questions, refer to the source code and configuration files.* 