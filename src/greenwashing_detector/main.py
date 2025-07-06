#!/usr/bin/env python
import sys
import warnings
import logging
import time
from datetime import datetime
from greenwashing_detector.crew import GreenwashingDetector

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
# src/greenwashing_detector/main.py

def run_greenwashing_crew(pdf_path: str) -> str:
    """
    Run the greenwashing detection crew with comprehensive framework logging and proper chunk processing.
    
    Args:
        pdf_path: Path to the PDF file to analyze
        
    Returns:
        Analysis results as a string
    """
    logger.info("🚀 Starting Greenwashing Detection Analysis")
    logger.info(f"📄 Analyzing PDF: {pdf_path}")
    logger.info("=" * 60)
    
    detector = GreenwashingDetector()
    
    # Log framework detection start
    detector.log_framework_detection_start(pdf_path)
    
    # --- FIX: Run framework detection separately first ---
    logger.info("🔍 Step 1: Running Framework Detection")
    logger.info("-" * 40)
    
    # Extract PDF content first since Ollama agents don't have tools
    logger.info("📄 Extracting PDF content for framework detection...")
    from greenwashing_detector.tools.pdf_loader import FrameworkPDFReader
    pdf_reader = FrameworkPDFReader()
    try:
        report_content = pdf_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Extracted {len(report_content)} characters for framework detection")
    except Exception as e:
        logger.error(f"❌ Error extracting PDF content: {e}")
        # Fallback to simple text extraction
        from greenwashing_detector.tools.pdf_loader import FullPDFReader
        fallback_reader = FullPDFReader()
        report_content = fallback_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Fallback extraction: {len(report_content)} characters")
    
    # Create a crew with only the framework detection task
    from crewai import Crew, Process
    
    framework_crew = Crew(
        agents=[detector.framework_detector()],
        tasks=[detector.detect_reporting_framework()],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute framework detection with timing
    start_time = time.time()
    framework_result = framework_crew.kickoff(inputs={"report_content": report_content})
    end_time = time.time()
    framework_processing_time = end_time - start_time
    
    # Log and save framework detection results
    logger.info("✅ Framework detection completed successfully")
    detector.log_framework_detection_complete(framework_result, framework_processing_time)
    framework_md_path = detector.save_framework_detection_to_md(framework_result, pdf_path)
    if framework_md_path:
        logger.info(f"📄 Framework detection report saved to: {framework_md_path}")
    
    # Also save individual agent output for framework detection
    detector.save_agent_output_to_md("framework_detector", "detect_reporting_framework", framework_result, pdf_path)
    
    # --- Step 2: Run the rest of the pipeline ---
    logger.info("\n🔍 Step 2: Running ESG Analysis and Claims Validation")
    logger.info("-" * 40)
    
    # Pre-process chunks for different agents
    logger.info("🔄 Pre-processing PDF chunks for different analysis tasks...")
    
    # Process chunks for ESG analysis (combines all chunks)
    esg_content = detector.process_esg_analysis_chunks(pdf_path)
    logger.info(f"✅ ESG content prepared: {len(esg_content)} characters")
    
    # Process chunks for claims extraction (combines all chunks)
    claims_content = detector.process_claims_across_chunks(pdf_path)
    logger.info(f"✅ Claims content prepared: {len(claims_content)} characters")
    
    # Create a crew with the remaining tasks (ESG analysis and claims validation)
    remaining_crew = Crew(
        agents=[detector.esg_analyst(), detector.compliance_checker()],
        tasks=[detector.extract_esg_claims(), detector.validate_claims()],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the remaining tasks
    start_time = time.time()
    remaining_inputs = {
        "file_path": pdf_path,
        "esg_content": esg_content,
        "claims_content": claims_content
    }
    
    remaining_result = remaining_crew.kickoff(inputs=remaining_inputs)
    end_time = time.time()
    remaining_processing_time = end_time - start_time
    
    total_processing_time = framework_processing_time + remaining_processing_time
    
    logger.info("🎉 Full Analysis Completed!")
    logger.info(f"⏱️  Total processing time: {total_processing_time:.2f} seconds")
    logger.info("=" * 60)
    
    # Save individual agent outputs for debugging
    logger.info("💾 Saving individual agent outputs for debugging...")
    
    # Extract individual results from the remaining crew output
    # Note: CrewAI returns a combined result, so we need to parse it
    remaining_result_str = str(remaining_result)
    
    # Save ESG analyst output (first part of the result)
    if "ESG Claims Investigator" in remaining_result_str or "ESG-related claims" in remaining_result_str:
        detector.save_agent_output_to_md("esg_analyst", "extract_esg_claims", remaining_result, pdf_path)
    
    # Save compliance checker output (second part of the result)
    if "Sustainability Compliance Expert" in remaining_result_str or "greenwashing" in remaining_result_str.lower():
        detector.save_agent_output_to_md("compliance_checker", "validate_claims", remaining_result, pdf_path)
    
    # Save a combined workflow summary
    detector.save_workflow_summary_to_md(framework_result, remaining_result, pdf_path, total_processing_time)
    
    # Return combined results
    combined_result = f"""
# Framework Detection Results
{framework_result}

# ESG Analysis and Claims Validation
{remaining_result}
"""
    
    return combined_result

def run_framework_detection_only(pdf_path: str) -> str:
    """
    Run only the framework detection task for testing with enhanced logging.
    
    Args:
        pdf_path: Path to the PDF file to analyze
        
    Returns:
        Framework detection results as a string
    """
    logger.info("🔍 Running Framework Detection Only")
    logger.info(f"📄 Analyzing PDF: {pdf_path}")
    logger.info("=" * 60)
    
    detector = GreenwashingDetector()
    
    # Log framework detection start
    detector.log_framework_detection_start(pdf_path)
    
    # Create a crew with only the framework detection task
    from crewai import Crew, Process
    
    framework_crew = Crew(
        agents=[detector.framework_detector()],
        tasks=[detector.detect_reporting_framework()],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute with timing
    start_time = time.time()
    result = framework_crew.kickoff(inputs={"file_path": pdf_path})
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Log the results with enhanced details
    detector.log_framework_detection_complete(result, processing_time)
    
    # Save framework detection results to markdown
    framework_md_path = detector.save_framework_detection_to_md(result, pdf_path)
    if framework_md_path:
        logger.info(f"📄 Framework detection report saved to: {framework_md_path}")
    
    # Also save individual agent output for framework detection
    detector.save_agent_output_to_md("framework_detector", "detect_reporting_framework", result, pdf_path)
    
    return result

def run_framework_detection_with_monitoring(pdf_path: str) -> str:
    """
    Run framework detection with detailed monitoring and logging.
    
    Args:
        pdf_path: Path to the PDF file to analyze
        
    Returns:
        Framework detection results as a string
    """
    logger.info("🔍 Running Framework Detection with Enhanced Monitoring")
    logger.info(f"📄 Analyzing PDF: {pdf_path}")
    logger.info("=" * 60)
    
    detector = GreenwashingDetector()
    
    # Log framework detection start
    detector.log_framework_detection_start(pdf_path)
    
    # Extract PDF content first since Ollama agents don't have tools
    logger.info("📄 Extracting PDF content for framework detection...")
    from greenwashing_detector.tools.pdf_loader import FrameworkPDFReader
    pdf_reader = FrameworkPDFReader()
    try:
        report_content = pdf_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Extracted {len(report_content)} characters for framework detection")
    except Exception as e:
        logger.error(f"❌ Error extracting PDF content: {e}")
        # Fallback to simple text extraction
        from greenwashing_detector.tools.pdf_loader import FullPDFReader
        fallback_reader = FullPDFReader()
        report_content = fallback_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Fallback extraction: {len(report_content)} characters")
    
    # Get agent and task details for monitoring
    framework_agent = detector.framework_detector()
    framework_task = detector.detect_reporting_framework()
    
    logger.info("🤖 Framework Detector Agent Details:")
    logger.info(f"   🏷️  Role: {framework_agent.role}")
    logger.info(f"   🎯 Goal: {framework_agent.goal}")
    logger.info(f"   🔧 Tools: {[tool.name for tool in framework_agent.tools] if framework_agent.tools else []}")
    logger.info("")
    
    logger.info("📋 Framework Detection Task Details:")
    logger.info(f"   📝 Description: {framework_task.description}")
    logger.info(f"   🎯 Expected Output: {framework_task.expected_output}")
    logger.info("")
    
    # Create and execute crew
    from crewai import Crew, Process
    
    framework_crew = Crew(
        agents=[framework_agent],
        tasks=[framework_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute with timing
    start_time = time.time()
    result = framework_crew.kickoff(inputs={"report_content": report_content})
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Log comprehensive results
    detector.log_framework_detection_complete(result, processing_time)
    
    # Save framework detection results to markdown
    framework_md_path = detector.save_framework_detection_to_md(result, pdf_path)
    if framework_md_path:
        logger.info(f"📄 Framework detection report saved to: {framework_md_path}")
    
    # Log execution summary
    detector.log_crew_execution_summary({"framework_detection": result})
    
    return result

def run_enhanced_greenwashing_workflow(pdf_path: str) -> str:
    """
    Run the enhanced greenwashing detection workflow with fluff remover and ChatGPT chunking.
    
    Workflow:
    1. Framework Detection (Ollama) - Identify ESG frameworks
    2. Fluff Removal (Ollama) - Remove unnecessary content
    3. ChatGPT Chunking - Process cleaned content for ChatGPT
    4. ESG Analysis (ChatGPT) - Extract claims from cleaned content
    5. Claims Validation (ChatGPT) - Validate claims for greenwashing
    
    Args:
        pdf_path: Path to the PDF file to analyze
        
    Returns:
        Analysis results as a string
    """
    logger.info("🚀 Starting Enhanced Greenwashing Detection Workflow")
    logger.info(f"📄 Analyzing PDF: {pdf_path}")
    logger.info("=" * 60)
    
    detector = GreenwashingDetector()
    
    # --- Step 1: Framework Detection (Ollama) ---
    logger.info("🔍 Step 1: Framework Detection (Ollama)")
    logger.info("-" * 40)
    
    # Extract PDF content first since Ollama agents don't have tools
    logger.info("📄 Extracting PDF content for framework detection...")
    from greenwashing_detector.tools.pdf_loader import FrameworkPDFReader
    pdf_reader = FrameworkPDFReader()
    try:
        report_content = pdf_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Extracted {len(report_content)} characters for framework detection")
    except Exception as e:
        logger.error(f"❌ Error extracting PDF content: {e}")
        # Fallback to simple text extraction
        from greenwashing_detector.tools.pdf_loader import FullPDFReader
        fallback_reader = FullPDFReader()
        report_content = fallback_reader._run(pdf_path)
        # Remove the prefix to get clean content
        if "PDF Text" in report_content:
            report_content = report_content.split("PDF Text", 1)[1].split("\n\n", 1)[1]
        logger.info(f"✅ Fallback extraction: {len(report_content)} characters")
    
    from crewai import Crew, Process
    
    framework_crew = Crew(
        agents=[detector.framework_detector()],
        tasks=[detector.detect_reporting_framework()],
        process=Process.sequential,
        verbose=True
    )
    
    start_time = time.time()
    framework_result = framework_crew.kickoff(inputs={"report_content": report_content})
    framework_time = time.time() - start_time
    
    logger.info("✅ Framework detection completed")
    detector.log_framework_detection_complete(framework_result, framework_time)
    detector.save_framework_detection_to_md(framework_result, pdf_path)
    detector.save_agent_output_to_md("framework_detector", "detect_reporting_framework", framework_result, pdf_path)
    
    # --- Step 2: Fluff Removal (Ollama) ---
    logger.info("\n🧹 Step 2: Fluff Removal (Ollama)")
    logger.info("-" * 40)
    
    # First, extract full text from PDF
    pdf_reader = detector.tools["FullPDFReader"]()
    full_text = pdf_reader._run(pdf_path)
    
    # Remove the "PDF Text" prefix to get clean text
    if "PDF Text" in full_text:
        full_text = full_text.split("PDF Text", 1)[1].split("\n\n", 1)[1]
    
    logger.info(f"📄 Full text extracted: {len(full_text)} characters")
    
    # Run fluff removal
    fluff_crew = Crew(
        agents=[detector.fluff_remover()],
        tasks=[detector.remove_report_fluff()],
        process=Process.sequential,
        verbose=True
    )
    
    start_time = time.time()
    fluff_result = fluff_crew.kickoff(inputs={"report_content": full_text})
    fluff_time = time.time() - start_time
    
    logger.info("✅ Fluff removal completed")
    logger.info(f"⏱️  Fluff removal time: {fluff_time:.2f} seconds")
    
    # Save fluff removal results
    detector.save_agent_output_to_md("fluff_remover", "remove_report_fluff", fluff_result, pdf_path)
    
    # Extract cleaned content
    cleaned_content = str(fluff_result)
    if hasattr(fluff_result, 'raw'):
        cleaned_content = str(fluff_result.raw)
    
    logger.info(f"📄 Cleaned content: {len(cleaned_content)} characters")
    
    # --- Step 3: ChatGPT Chunking ---
    logger.info("\n🔄 Step 3: ChatGPT Chunking")
    logger.info("-" * 40)
    
    # Process cleaned content for ChatGPT
    chatgpt_content = detector.process_fluff_removed_content_with_chatgpt(cleaned_content)
    logger.info(f"✅ ChatGPT content prepared: {len(chatgpt_content)} characters")
    
    # --- Step 4: ESG Analysis and Claims Validation (ChatGPT) ---
    logger.info("\n🔍 Step 4: ESG Analysis and Claims Validation (ChatGPT)")
    logger.info("-" * 40)
    
    # Create crew for ChatGPT-based analysis
    chatgpt_crew = Crew(
        agents=[detector.esg_analyst(), detector.compliance_checker()],
        tasks=[detector.extract_esg_claims(), detector.validate_claims()],
        process=Process.sequential,
        verbose=True
    )
    
    start_time = time.time()
    chatgpt_inputs = {
        "file_path": pdf_path,
        "esg_content": chatgpt_content,
        "claims_content": chatgpt_content
    }
    
    chatgpt_result = chatgpt_crew.kickoff(inputs=chatgpt_inputs)
    chatgpt_time = time.time() - start_time
    
    total_time = framework_time + fluff_time + chatgpt_time
    
    logger.info("🎉 Enhanced Workflow Completed!")
    logger.info(f"⏱️  Total processing time: {total_time:.2f} seconds")
    logger.info("=" * 60)
    
    # Save individual agent outputs
    logger.info("💾 Saving individual agent outputs...")
    
    chatgpt_result_str = str(chatgpt_result)
    
    # Save ESG analyst output
    if "ESG Claims Investigator" in chatgpt_result_str or "ESG-related claims" in chatgpt_result_str:
        detector.save_agent_output_to_md("esg_analyst", "extract_esg_claims", chatgpt_result, pdf_path)
    
    # Save compliance checker output
    if "Sustainability Compliance Expert" in chatgpt_result_str or "greenwashing" in chatgpt_result_str.lower():
        detector.save_agent_output_to_md("compliance_checker", "validate_claims", chatgpt_result, pdf_path)
    
    # Save enhanced workflow summary
    detector.save_enhanced_workflow_summary_to_md(framework_result, fluff_result, chatgpt_result, pdf_path, total_time)
    
    # Return combined results
    combined_result = f"""
# Enhanced Greenwashing Detection Workflow Results

## Framework Detection (Ollama)
{framework_result}

## Fluff Removal (Ollama)
Content cleaned and prepared for ChatGPT analysis.

## ESG Analysis and Claims Validation (ChatGPT)
{chatgpt_result}

## Processing Summary
- Framework Detection: {framework_time:.2f}s
- Fluff Removal: {fluff_time:.2f}s  
- ChatGPT Analysis: {chatgpt_time:.2f}s
- Total Time: {total_time:.2f}s
"""
    
    return combined_result

if __name__ == "__main__":
    # Example usage
    pdf_file = "uploaded_reports/sustainability_report.pdf"
    
    # Run framework detection with enhanced monitoring
    result = run_framework_detection_with_monitoring(pdf_file)
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(result)

