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
    
    # --- Step 2a: Run ESG Analysis First ---
    logger.info("\n🔍 Step 2a: Running ESG Analysis")
    logger.info("-" * 40)
    
    # Create a crew with only the ESG analysis task
    esg_crew = Crew(
        agents=[detector.esg_analyst()],
        tasks=[detector.extract_esg_claims()],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute ESG analysis
    start_time = time.time()
    esg_inputs = {
        "file_path": pdf_path,
        "esg_content": esg_content
    }
    
    esg_result = esg_crew.kickoff(inputs=esg_inputs)
    esg_time = time.time() - start_time
    
    logger.info("✅ ESG analysis completed")
    logger.info(f"⏱️  ESG analysis time: {esg_time:.2f} seconds")
    
    # Save ESG analyst output
    detector.save_agent_output_to_md("esg_analyst", "extract_esg_claims", esg_result, pdf_path)
    
    # --- Step 2b: Run Claims Validation with ESG Analyst Output ---
    logger.info("\n🔍 Step 2b: Running Claims Validation")
    logger.info("-" * 40)
    
    # Convert ESG result to string
    esg_output_str = str(esg_result)
    if hasattr(esg_result, 'raw'):
        esg_output_str = str(esg_result.raw)
    
    # Chunk the ESG output for validation to avoid token limits
    logger.info("🔄 Chunking ESG output for claims validation...")
    validation_chunks = detector.chunk_esg_output_for_validation(esg_output_str)
    logger.info(f"✅ Created {len(validation_chunks)} validation chunks")
    
    # Process each validation chunk separately
    all_validation_results = []
    
    for i, validation_chunk in enumerate(validation_chunks, 1):
        logger.info(f"🔍 Processing validation chunk {i} of {len(validation_chunks)}")
        
        # Create a crew with only the claims validation task
        validation_crew = Crew(
            agents=[detector.compliance_checker()],
            tasks=[detector.validate_claims()],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute claims validation with ESG analyst output chunk
        start_time = time.time()
        validation_inputs = {
            "esg_analyst_output": validation_chunk
        }
        
        chunk_validation_result = validation_crew.kickoff(inputs=validation_inputs)
        chunk_validation_time = time.time() - start_time
        
        logger.info(f"✅ Validation chunk {i} completed in {chunk_validation_time:.2f} seconds")
        
        # Add chunk information to result
        chunk_result_with_info = f"## Claims Validation - Chunk {i} of {len(validation_chunks)}\n\n"
        chunk_result_with_info += str(chunk_validation_result)
        chunk_result_with_info += f"\n\n--- Chunk {i} Processing Time: {chunk_validation_time:.2f}s ---\n"
        
        all_validation_results.append(chunk_result_with_info)
    
    # Combine all validation results
    validation_result = f"# Claims Validation Results from {len(validation_chunks)} Chunks\n\n"
    for i, result in enumerate(all_validation_results, 1):
        validation_result += result
        validation_result += "\n\n" + "="*50 + "\n\n"
    
    validation_time = time.time() - start_time  # Total validation time
    
    logger.info("✅ Claims validation completed")
    logger.info(f"⏱️  Claims validation time: {validation_time:.2f} seconds")
    
    # Save compliance checker output
    detector.save_agent_output_to_md("compliance_checker", "validate_claims", validation_result, pdf_path)
    
    total_processing_time = framework_processing_time + esg_time + validation_time
    
    logger.info("🎉 Full Analysis Completed!")
    logger.info(f"⏱️  Total processing time: {total_processing_time:.2f} seconds")
    logger.info("=" * 60)
    
    # Save a combined workflow summary
    detector.save_workflow_summary_to_md(framework_result, f"{esg_result}\n\n{validation_result}", pdf_path, total_processing_time)
    
    # Return combined results
    combined_result = f"""
# Framework Detection Results
{framework_result}

# ESG Analysis Results
{esg_result}

# Claims Validation Results
{validation_result}
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
    
    # Extract detected frameworks for fluff remover
    detected_frameworks = detector._extract_detected_frameworks(framework_result)
    logger.info(f"🎯 Detected frameworks for fluff remover: {detected_frameworks}")
    
    # Store framework result for TCFD routing logic
    detector.last_framework_result = framework_result
    
    # Check if TCFD is a major framework and determine analysis route
    tcfd_is_major = detector.is_tcfd_major_framework(detected_frameworks)
    tcfd_analysis_route = detector.get_tcfd_analysis_route(detected_frameworks)
    
    if tcfd_is_major:
        logger.info(f"🎯 TCFD detected as major framework - Analysis route: {tcfd_analysis_route}")
    else:
        logger.info("📋 TCFD not detected as major framework - Using standard analysis")
    
    # --- Step 2: Framework-Aware Fluff Removal (Ollama) ---
    logger.info("\n🧹 Step 2: Framework-Aware Fluff Removal (Ollama)")
    logger.info("-" * 40)
    
    # First, extract full text from PDF
    pdf_reader = detector.tools["FullPDFReader"]()
    full_text = pdf_reader._run(pdf_path)
    
    # Remove the "PDF Text" prefix to get clean text
    if "PDF Text" in full_text:
        full_text = full_text.split("PDF Text", 1)[1].split("\n\n", 1)[1]
    
    logger.info(f"📄 Full text extracted: {len(full_text)} characters")
    
    # Run framework-aware fluff removal
    fluff_crew = Crew(
        agents=[detector.fluff_remover()],
        tasks=[detector.remove_report_fluff()],
        process=Process.sequential,
        verbose=True
    )
    
    start_time = time.time()
    fluff_result = fluff_crew.kickoff(inputs={
        "report_content": full_text,
        "detected_frameworks": detected_frameworks
    })
    fluff_time = time.time() - start_time
    
    logger.info("✅ Framework-aware fluff removal completed")
    logger.info(f"⏱️  Fluff removal time: {fluff_time:.2f} seconds")
    logger.info(f"🎯 Frameworks preserved: {detected_frameworks}")
    
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
    
    # Process cleaned content for ChatGPT - get all chunks
    all_chunks = detector.process_all_chunks_for_chatgpt(cleaned_content)
    logger.info(f"✅ Created {len(all_chunks)} chunks for ChatGPT processing")
    
    # --- Step 4: ESG Analysis and Claims Validation (ChatGPT) ---
    logger.info("\n🔍 Step 4: ESG Analysis and Claims Validation (ChatGPT)")
    logger.info("-" * 40)
    
    # Process each chunk separately to avoid token limits
    all_results = []
    
    for i, chunk in enumerate(all_chunks, 1):
        logger.info(f"📄 Processing chunk {i} of {len(all_chunks)}")
        
        # Use TCFD routing logic if TCFD is a major framework
        if tcfd_is_major:
            logger.info(f"🎯 Using TCFD specialized analysis route: {tcfd_analysis_route}")
            
            # Create TCFD specialized crew
            tcfd_crew = detector.create_tcfd_specialized_crew(tcfd_analysis_route)
            
            start_time = time.time()
            tcfd_inputs = {
                "file_path": pdf_path,
                "esg_content": chunk,
                "claims_content": chunk
            }
            
            chunk_result = tcfd_crew.kickoff(inputs=tcfd_inputs)
            chunk_time = time.time() - start_time
            
            logger.info(f"✅ TCFD chunk {i} completed in {chunk_time:.2f} seconds")
            
        else:
            # Use standard analysis for non-TCFD reports
            logger.info("📋 Using standard analysis approach")
            
            # First, run ESG claims extraction
            esg_crew = Crew(
                agents=[detector.esg_analyst()],
                tasks=[detector.extract_esg_claims()],
                process=Process.sequential,
                verbose=True
            )
            
            start_time = time.time()
            esg_inputs = {
                "file_path": pdf_path,
                "esg_content": chunk
            }
            
            esg_result = esg_crew.kickoff(inputs=esg_inputs)
            esg_time = time.time() - start_time
            
            logger.info(f"✅ ESG analysis chunk {i} completed in {esg_time:.2f} seconds")
            
            # Then, run claims validation with ESG results
            validation_crew = Crew(
                agents=[detector.compliance_checker()],
                tasks=[detector.validate_claims()],
                process=Process.sequential,
                verbose=True
            )
            
            # Convert ESG result to string and chunk it for validation
            esg_output_str = str(esg_result)
            if hasattr(esg_result, 'raw'):
                esg_output_str = str(esg_result.raw)
            
            # Chunk the ESG output for validation to avoid token limits
            logger.info(f"🔄 Chunking ESG output for validation (chunk {i})...")
            validation_chunks = detector.chunk_esg_output_for_validation(esg_output_str)
            logger.info(f"✅ Created {len(validation_chunks)} validation chunks for chunk {i}")
            
            # Process each validation chunk separately
            all_chunk_validation_results = []
            
            for j, validation_chunk in enumerate(validation_chunks, 1):
                logger.info(f"🔍 Processing validation sub-chunk {j} of {len(validation_chunks)}")
                
                validation_inputs = {
                    "esg_analyst_output": validation_chunk
                }
                
                sub_validation_result = validation_crew.kickoff(inputs=validation_inputs)
                sub_validation_time = time.time() - start_time
                
                logger.info(f"✅ Validation sub-chunk {j} completed in {sub_validation_time:.2f} seconds")
                
                # Add sub-chunk information to result
                sub_result_with_info = f"### Validation Sub-Chunk {j} of {len(validation_chunks)}\n\n"
                sub_result_with_info += str(sub_validation_result)
                
                all_chunk_validation_results.append(sub_result_with_info)
            
            # Combine all validation results for this chunk
            validation_result = f"## Claims Validation Results\n\n"
            for j, result in enumerate(all_chunk_validation_results, 1):
                validation_result += result
                validation_result += "\n\n" + "-"*30 + "\n\n"
            
            validation_time = time.time() - start_time
            
            logger.info(f"✅ Claims validation chunk {i} completed in {validation_time:.2f} seconds")
            
            # Combine ESG and validation results
            chunk_result = f"## ESG Analysis\n{esg_result}\n\n## Claims Validation\n{validation_result}"
        
        all_results.append(chunk_result)
    
    # Combine all chunk results
    combined_chatgpt_result = f"# Analysis Results from {len(all_chunks)} Chunks\n\n"
    for i, result in enumerate(all_results, 1):
        combined_chatgpt_result += f"## Chunk {i} Results\n\n"
        combined_chatgpt_result += result
        combined_chatgpt_result += "\n\n" + "="*50 + "\n\n"
    
    chatgpt_time = sum([time.time() - start_time for _ in all_results])  # Approximate total time
    
    total_time = framework_time + fluff_time + chatgpt_time
    
    logger.info("🎉 Enhanced Workflow Completed!")
    logger.info(f"⏱️  Total processing time: {total_time:.2f} seconds")
    logger.info("=" * 60)
    
    # Save individual agent outputs
    logger.info("💾 Saving individual agent outputs...")
    
    chatgpt_result_str = str(combined_chatgpt_result)
    
    # Save ESG analyst output
    if "ESG Claims Investigator" in chatgpt_result_str or "ESG-related claims" in chatgpt_result_str:
        detector.save_agent_output_to_md("esg_analyst", "extract_esg_claims", combined_chatgpt_result, pdf_path)
    
    # Save compliance checker output
    if "Sustainability Compliance Expert" in chatgpt_result_str or "greenwashing" in chatgpt_result_str.lower():
        detector.save_agent_output_to_md("compliance_checker", "validate_claims", combined_chatgpt_result, pdf_path)
    
    # Save enhanced workflow summary
    detector.save_enhanced_workflow_summary_to_md(framework_result, fluff_result, combined_chatgpt_result, pdf_path, total_time)
    
    # Return combined results
    combined_result = f"""
# Enhanced Greenwashing Detection Workflow Results

## Framework Detection (Ollama)
{framework_result}

## Fluff Removal (Ollama)
Content cleaned and prepared for ChatGPT analysis.

## ESG Analysis and Claims Validation (ChatGPT)
{chatgpt_result_str}

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

