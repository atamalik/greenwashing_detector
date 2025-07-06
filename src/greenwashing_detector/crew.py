from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import logging
import json
from datetime import datetime
from .tools.pdf_loader import FrameworkPDFReader, FullPDFReader, ESGChunkProcessor
from .tools.framework_glossary import FrameworkGlossaryTool
from .tools.section_extractor import RelevantSectionExtractor
from .tools.fluff_remover import FluffRemover
from .tools.tcfd_analyzer import TCFDAnalyzerTool


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@CrewBase
class GreenwashingDetector():
    """GreenwashingDetector crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        super().__init__()
        self.tools = {
            "FrameworkPDFReader": FrameworkPDFReader,
            "FullPDFReader": FullPDFReader,
            "FrameworkGlossaryTool": FrameworkGlossaryTool,
            "RelevantSectionExtractor": RelevantSectionExtractor,
            "FluffRemover": FluffRemover,
            "TCFDAnalyzerTool": TCFDAnalyzerTool
        }
        self.detected_frameworks = None
        self.esg_chunk_processor = None

    
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def structure_identifier(self) -> Agent:
        config = self.agents_config['structure_identifier'].copy()
        if 'tools' in config:
            del config['tools']
        
        # Check if using Ollama - if so, don't use tools
        if config.get('llm', '').startswith('ollama/'):
            logger.info("🔧 Creating Ollama-compatible structure identifier without tools")
            return Agent(
                **config,
                tools=[]  # No tools for Ollama
            )
        else:
            # Use tools for other models (OpenAI, etc.)
            return Agent(
                **config,
                tools=[self.tools["FrameworkPDFReader"]()]
            )

    @agent
    def framework_detector(self) -> Agent:
        config = self.agents_config['framework_detector'].copy()
        if 'tools' in config:
            del config['tools']
        
        # Check if using Ollama - if so, don't use tools
        if config.get('llm', '').startswith('ollama/'):
            logger.info("🔧 Creating Ollama-compatible framework detector without tools")
            return Agent(
                **config,
                tools=[]  # No tools for Ollama
            )
        else:
            # Use tools for other models (OpenAI, etc.)
            return Agent(
                **config,
                tools=[self.tools["FrameworkPDFReader"](),
                       self.tools["FrameworkGlossaryTool"]()]
            )

    @agent
    def section_filter(self) -> Agent:
        config = self.agents_config['section_filter'].copy()
        if 'tools' in config:
            del config['tools']
        
        # Check if using Ollama - if so, don't use tools
        if config.get('llm', '').startswith('ollama/'):
            logger.info("🔧 Creating Ollama-compatible section filter without tools")
            return Agent(
                **config,
                tools=[]  # No tools for Ollama
            )
        else:
            # Use tools for other models (OpenAI, etc.)
            return Agent(
                **config,
                tools=[self.tools["RelevantSectionExtractor"]()]
            )

    @agent
    def fluff_remover(self) -> Agent:
        config = self.agents_config['fluff_remover'].copy()
        if 'tools' in config:
            del config['tools']
        
        # Check if using Ollama - if so, don't use tools
        if config.get('llm', '').startswith('ollama/'):
            logger.info("🔧 Creating Ollama-compatible fluff remover without tools")
            return Agent(
                **config,
                tools=[]  # No tools for Ollama
            )
        else:
            # Use tools for other models (OpenAI, etc.)
            return Agent(
                **config,
                tools=[self.tools["FluffRemover"]()]
            )

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

    @agent
    def compliance_checker(self) -> Agent:
        config = self.agents_config['compliance_checker'].copy()
        if 'tools' in config:
            del config['tools']
        return Agent(
            **config,
            tools=[]  # Disabled web search tool
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_report_structure(self) -> Task:
        return Task(
            config=self.tasks_config['extract_report_structure'],
            output_file='structure_analysis.md'
        )

    @task
    def extract_framework_sections(self) -> Task:
        return Task(
            config=self.tasks_config['extract_framework_sections'],
            output_file='section_extraction.md'
        )

    @task
    def detect_reporting_framework(self) -> Task:
        return Task(
            config=self.tasks_config['detect_reporting_framework'],
            output_file='framework_detection.md'
        )

    @task
    def remove_report_fluff(self) -> Task:
        return Task(
            config=self.tasks_config['remove_report_fluff'],
            output_file='fluff_removal.md'
        )

    @task
    def extract_esg_claims(self) -> Task:
        return Task(
            config=self.tasks_config['extract_esg_claims'],
            output_file='esg_claims.md'
        )

    @task
    def validate_claims(self) -> Task:
        return Task(
            config=self.tasks_config['validate_claims'],
            output_file='compliance_validation.md'
        )

    def process_esg_analysis_chunks(self, file_path: str) -> str:
        """
        Process ESG analysis in chunks and aggregate results.
        This method handles large PDFs by processing them in manageable chunks.
        """
        try:
            # Initialize the chunk processor
            pdf_reader = FullPDFReader()
            self.esg_chunk_processor = ESGChunkProcessor(pdf_reader)
            
            # Get all chunks
            chunks = self.esg_chunk_processor.process_all_chunks(file_path)
            
            logger.info(f"📊 Processing {len(chunks)} chunks for ESG analysis")
            
            if len(chunks) == 1:
                # Single chunk, return directly
                logger.info("📄 Using single chunk for ESG analysis")
                return f"PDF Text (Complete Document):\n\n{chunks[0]}"
            else:
                # Multiple chunks - combine them intelligently
                logger.info(f"🔄 Combining {len(chunks)} chunks for complete analysis")
                
                # Combine all chunks with clear separators
                combined_text = ""
                for i, chunk in enumerate(chunks, 1):
                    combined_text += f"\n\n--- CHUNK {i} OF {len(chunks)} ---\n\n"
                    combined_text += chunk
                
                # Add summary information
                combined_text += f"\n\n--- ANALYSIS SUMMARY ---\n"
                combined_text += f"Total chunks processed: {len(chunks)}\n"
                combined_text += f"Total content length: {len(combined_text)} characters\n"
                combined_text += f"Please analyze ALL chunks above for comprehensive ESG assessment.\n"
                
                logger.info(f"✅ Combined {len(chunks)} chunks into {len(combined_text)} characters")
                return combined_text
                
        except Exception as e:
            logger.error(f"Error processing ESG analysis chunks: {e}")
            return f"Error processing PDF chunks: {str(e)}"

    def process_claims_across_chunks(self, file_path: str) -> str:
        """
        Process claims extraction across all chunks and aggregate results.
        This ensures we capture claims from the entire document.
        """
        try:
            # Initialize the chunk processor
            pdf_reader = FullPDFReader()
            self.esg_chunk_processor = ESGChunkProcessor(pdf_reader)
            
            # Get all chunks
            chunks = self.esg_chunk_processor.process_all_chunks(file_path)
            
            logger.info(f"📊 Processing claims across {len(chunks)} chunks")
            
            if len(chunks) == 1:
                # Single chunk, return directly
                logger.info("📄 Using single chunk for claims extraction")
                return f"PDF Text (Complete Document for Claims Extraction):\n\n{chunks[0]}"
            else:
                # Multiple chunks - combine for claims extraction
                logger.info(f"🔄 Combining {len(chunks)} chunks for claims extraction")
                
                # Combine all chunks with clear separators
                combined_text = ""
                for i, chunk in enumerate(chunks, 1):
                    combined_text += f"\n\n--- SECTION {i} OF {len(chunks)} ---\n\n"
                    combined_text += chunk
                
                # Add instructions for claims extraction
                combined_text += f"\n\n--- CLAIMS EXTRACTION INSTRUCTIONS ---\n"
                combined_text += f"Extract ALL ESG claims from ALL {len(chunks)} sections above.\n"
                combined_text += f"Look for environmental, social, and governance claims throughout the document.\n"
                combined_text += f"Ensure comprehensive coverage of the entire sustainability report.\n"
                
                logger.info(f"✅ Combined {len(chunks)} chunks for claims extraction")
                return combined_text
                
        except Exception as e:
            logger.error(f"Error processing claims across chunks: {e}")
            return f"Error processing PDF chunks for claims: {str(e)}"

    def process_fluff_removed_content_with_chatgpt(self, cleaned_content: str, max_tokens_per_chunk: int = 14000) -> str:
        """
        Process fluff-removed content with chunking optimized for ChatGPT (16K token limit).
        
        Args:
            cleaned_content: The cleaned content from the fluff remover
            max_tokens_per_chunk: Maximum tokens per chunk (default 14K to leave buffer)
            
        Returns:
            Processed content ready for ChatGPT analysis
        """
        try:
            logger.info("🧹 Processing fluff-removed content for ChatGPT analysis")
            logger.info(f"📄 Input content length: {len(cleaned_content)} characters")
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(cleaned_content) // 4
            logger.info(f"📊 Estimated tokens: {estimated_tokens:,}")
            
            if estimated_tokens <= max_tokens_per_chunk:
                # Content fits in single chunk
                logger.info("✅ Content fits in single ChatGPT chunk")
                return cleaned_content
            else:
                # Need to chunk the content
                logger.info(f"🔄 Content needs chunking for ChatGPT (max {max_tokens_per_chunk:,} tokens per chunk)")
                
                # Calculate chunk size in characters
                chunk_size_chars = max_tokens_per_chunk * 4
                overlap_chars = 1000  # 250 tokens overlap
                
                # Split content into chunks
                chunks = []
                start = 0
                chunk_num = 1
                
                while start < len(cleaned_content):
                    end = start + chunk_size_chars
                    
                    # Try to break at sentence boundary
                    if end < len(cleaned_content):
                        # Look for sentence endings
                        for i in range(end, max(start + chunk_size_chars - 500, start), -1):
                            if cleaned_content[i] in '.!?':
                                end = i + 1
                                break
                    
                    chunk = cleaned_content[start:end]
                    chunks.append(chunk)
                    
                    logger.info(f"📄 Chunk {chunk_num}: {len(chunk)} characters")
                    
                    # Move start position with overlap
                    start = end - overlap_chars
                    chunk_num += 1
                
                logger.info(f"✅ Created {len(chunks)} chunks for ChatGPT processing")
                
                # Combine chunks with clear separators
                combined_content = ""
                for i, chunk in enumerate(chunks, 1):
                    combined_content += f"\n\n--- CHUNK {i} OF {len(chunks)} (ChatGPT Optimized) ---\n\n"
                    combined_content += chunk
                
                # Add processing instructions
                combined_content += f"\n\n--- CHATGPT PROCESSING INSTRUCTIONS ---\n"
                combined_content += f"This content has been cleaned of fluff and chunked for ChatGPT analysis.\n"
                combined_content += f"Total chunks: {len(chunks)}\n"
                combined_content += f"Max tokens per chunk: {max_tokens_per_chunk:,}\n"
                combined_content += f"Please analyze ALL chunks above for comprehensive ESG assessment.\n"
                
                logger.info(f"✅ Combined {len(chunks)} chunks into {len(combined_content)} characters")
                return combined_content
                
        except Exception as e:
            logger.error(f"Error processing fluff-removed content: {e}")
            return f"Error processing cleaned content: {str(e)}"

    def log_detected_frameworks(self, framework_result: str):
        """Log the detected frameworks with timestamp and details."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log the raw result
            logger.info("🔍 FRAMEWORK DETECTION RESULTS")
            logger.info("=" * 50)
            logger.info(f"📅 Timestamp: {timestamp}")
            logger.info(f"📄 Raw Result: {framework_result}")
            
            # Try to parse and structure the result
            frameworks_detected = []
            
            # Simple parsing of bullet points
            lines = framework_result.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    # Extract framework name and confidence
                    if '**' in line:
                        # Format: **GRI**: Description. Confidence: 95%
                        parts = line.split('**')
                        if len(parts) >= 3:
                            framework_name = parts[1].strip()
                            description = parts[2].replace(':', '', 1).strip()
                            
                            # Extract confidence score
                            confidence = "N/A"
                            if "confidence" in description.lower():
                                import re
                                confidence_match = re.search(r'(\d+)%', description.lower())
                                if confidence_match:
                                    confidence = f"{confidence_match.group(1)}%"
                            
                            frameworks_detected.append({
                                "framework": framework_name,
                                "description": description,
                                "confidence": confidence
                            })
            
            # Log structured results
            if frameworks_detected:
                logger.info("📋 DETECTED FRAMEWORKS:")
                for framework in frameworks_detected:
                    logger.info(f"   🏷️  {framework['framework']}")
                    logger.info(f"   📝 {framework['description']}")
                    logger.info(f"   🎯 Confidence: {framework['confidence']}")
                    logger.info("")
            else:
                logger.info("⚠️  No frameworks detected or unable to parse results")
            
            # Save to JSON file for later analysis
            framework_log = {
                "timestamp": timestamp,
                "raw_result": framework_result,
                "parsed_frameworks": frameworks_detected,
                "total_frameworks_detected": len(frameworks_detected)
            }
            
            import os
            log_dir = "framework_logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_filename = f"{log_dir}/framework_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, 'w') as f:
                json.dump(framework_log, f, indent=2)
            
            logger.info(f"💾 Framework detection log saved to: {log_filename}")
            
            # Store for potential use by other agents
            self.detected_frameworks = frameworks_detected
            
        except Exception as e:
            logger.error(f"❌ Error logging detected frameworks: {e}")
            logger.info(f"📄 Raw framework result: {framework_result}")

    def log_framework_detection_start(self, file_path: str):
        """Log the start of framework detection process."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("🚀 STARTING FRAMEWORK DETECTION")
        logger.info("=" * 50)
        logger.info(f"📅 Timestamp: {timestamp}")
        logger.info(f"📄 PDF File: {file_path}")
        
        # Check file size
        try:
            import os
            file_size = os.path.getsize(file_path)
            logger.info(f"📏 File Size: {file_size:,} bytes")
        except Exception as e:
            logger.warning(f"⚠️  Could not determine file size: {e}")

    def log_framework_detection_complete(self, framework_result, processing_time: float = None):
        """Log the completion of framework detection with performance metrics."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("✅ FRAMEWORK DETECTION COMPLETED")
        logger.info("=" * 50)
        logger.info(f"📅 Timestamp: {timestamp}")
        if processing_time:
            logger.info(f"⏱️  Processing Time: {processing_time:.2f} seconds")
        
        # Convert CrewOutput to string if needed
        if hasattr(framework_result, 'raw'):
            result_str = str(framework_result.raw)
        else:
            result_str = str(framework_result)
        
        logger.info(f"📄 Result Length: {len(result_str)} characters")
        
        # Log the actual framework detection output
        logger.info("🔍 FRAMEWORK DETECTOR OUTPUT:")
        logger.info("-" * 30)
        logger.info(result_str)
        logger.info("-" * 30)
        
        # Call the detailed logging function
        self.log_detected_frameworks(result_str)

    def log_agent_execution(self, agent_name: str, task_name: str, input_data: str = None, output_data: str = None):
        """Log agent execution details for monitoring."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"🤖 AGENT EXECUTION: {agent_name}")
        logger.info("=" * 50)
        logger.info(f"📅 Timestamp: {timestamp}")
        logger.info(f"🎯 Task: {task_name}")
        
        if input_data:
            logger.info(f"📥 Input Length: {len(input_data)} characters")
            # Log first 200 chars of input for debugging
            preview = input_data[:200] + "..." if len(input_data) > 200 else input_data
            logger.info(f"📥 Input Preview: {preview}")
        
        if output_data:
            logger.info(f"📤 Output Length: {len(output_data)} characters")
            # Log first 500 chars of output for debugging
            preview = output_data[:500] + "..." if len(output_data) > 500 else output_data
            logger.info(f"📤 Output Preview: {preview}")
        
        logger.info("")

    def log_crew_execution_summary(self, results: dict):
        """Log a summary of the entire crew execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("📊 CREW EXECUTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📅 Timestamp: {timestamp}")
        
        for task_name, result in results.items():
            logger.info(f"✅ {task_name}: {len(str(result))} characters")
        
        # Log framework detection summary if available
        if self.detected_frameworks:
            logger.info(f"🎯 Frameworks Detected: {len(self.detected_frameworks)}")
            for framework in self.detected_frameworks:
                logger.info(f"   - {framework['framework']} ({framework['confidence']})")
        
        logger.info("")

    @crew
    def crew(self) -> Crew:
        """Creates the GreenwashingDetector crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        crew_instance = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
        
        # Add callback to log framework detection results
        def on_task_complete(task_output, task_name):
            if task_name == "detect_reporting_framework":
                logger.info("🎯 Framework detection task completed!")
                self.log_framework_detection_complete(task_output)
        
        # Note: CrewAI doesn't have built-in task callbacks, so we'll handle this in the main execution
        return crew_instance

    def save_agent_output_to_md(self, agent_name: str, task_name: str, result, file_path: str = None):
        """
        Save individual agent output to a markdown file in the output folder.
        
        Args:
            agent_name: Name of the agent that produced the output
            task_name: Name of the task that was executed
            result: The result from the agent
            file_path: Optional custom file path, otherwise auto-generated
        """
        try:
            import os
            from datetime import datetime
            
            # Convert CrewOutput to string if needed
            if hasattr(result, 'raw'):
                result_str = str(result.raw)
            else:
                result_str = str(result)
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_path:
                # Extract filename from provided path
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                filename = f"{agent_name}_{task_name}_{base_name}_{timestamp}.md"
            else:
                filename = f"{agent_name}_{task_name}_{timestamp}.md"
            
            output_path = os.path.join(output_dir, filename)
            
            # Create markdown content
            md_content = f"""# {agent_name.replace('_', ' ').title()} - {task_name.replace('_', ' ').title()}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Agent:** {agent_name}
**Task:** {task_name}
**PDF File:** {file_path if file_path else "Not specified"}

## Analysis Results

{result_str}

## Task Summary

This report contains the output from the {agent_name} agent executing the {task_name} task. The analysis was performed as part of the ESG framework detection and greenwashing analysis pipeline.

### Agent Role

{self.agents_config.get(agent_name, {}).get('role', 'Not specified')}

### Task Description

{self.tasks_config.get(task_name, {}).get('description', 'Not specified')}

---
*Report generated by Greenwashing Detector Analysis System*
"""
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"💾 {agent_name} output saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving {agent_name} output to markdown: {e}")
            return None

    def save_framework_detection_to_md(self, framework_result, file_path: str = None):
        """
        Save the framework detection results to a markdown file in the output folder.
        
        Args:
            framework_result: The framework detection result from the agent
            file_path: Optional custom file path, otherwise auto-generated
        """
        try:
            import os
            from datetime import datetime
            
            # Convert CrewOutput to string if needed
            if hasattr(framework_result, 'raw'):
                result_str = str(framework_result.raw)
            else:
                result_str = str(framework_result)
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_path:
                # Extract filename from provided path
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                filename = f"framework_detection_{base_name}_{timestamp}.md"
            else:
                filename = f"framework_detection_{timestamp}.md"
            
            output_path = os.path.join(output_dir, filename)
            
            # Create markdown content
            md_content = f"""# Framework Detection Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**PDF File:** {file_path if file_path else "Not specified"}

## Detected Frameworks

{result_str}

## Analysis Summary

This report contains the ESG and sustainability reporting frameworks detected in the analyzed document. The detection was performed using smart chunking to focus on sections most likely to contain framework mentions, such as "About this Report", "Methodology", "Reporting Approach", and "Assurance" sections.

### Detection Method

- **Smart Chunking**: Focused on framework-relevant sections
- **Target Frameworks**: GRI, TCFD, SASB, CDP, CSRD, ESRS, ISO 14064, and others
- **Confidence Scoring**: Each framework includes a confidence score (0-100%)
- **Evidence**: Supporting quotes and context from the document

### Notes

- Frameworks marked with high confidence (80%+) are likely explicitly mentioned
- Medium confidence (40-79%) indicates implicit or inferred references
- Low confidence (<40%) suggests possible but uncertain mentions
- "Not mentioned" indicates the framework was not detected in the document

---
*Report generated by Greenwashing Detector Framework Analysis System*
"""
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"💾 Framework detection saved to: {output_path}")
            
            # Also save a simple version with just the results
            simple_filename = f"framework_results_{timestamp}.md"
            simple_path = os.path.join(output_dir, simple_filename)
            
            with open(simple_path, 'w', encoding='utf-8') as f:
                f.write(result_str)
            
            logger.info(f"💾 Simple results saved to: {simple_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving framework detection to markdown: {e}")
            return None

    def save_workflow_summary_to_md(self, framework_result, remaining_result, file_path: str = None, processing_time: float = None):
        """
        Save a comprehensive workflow summary to a markdown file in the output folder.
        
        Args:
            framework_result: The framework detection result
            remaining_result: The ESG analysis and claims validation result
            file_path: Optional custom file path
            processing_time: Total processing time in seconds
        """
        try:
            import os
            from datetime import datetime
            
            # Convert CrewOutput to string if needed
            if hasattr(framework_result, 'raw'):
                framework_str = str(framework_result.raw)
            else:
                framework_str = str(framework_result)
                
            if hasattr(remaining_result, 'raw'):
                remaining_str = str(remaining_result.raw)
            else:
                remaining_str = str(remaining_result)
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_path:
                # Extract filename from provided path
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                filename = f"workflow_summary_{base_name}_{timestamp}.md"
            else:
                filename = f"workflow_summary_{timestamp}.md"
            
            output_path = os.path.join(output_dir, filename)
            
            # Create markdown content
            md_content = f"""# Greenwashing Detection Workflow Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**PDF File:** {file_path if file_path else "Not specified"}
**Processing Time:** {f"{processing_time:.2f} seconds" if processing_time else "Not recorded"}

## Workflow Overview

This report summarizes the complete greenwashing detection workflow execution, including all stages from framework detection to claims validation.

### Workflow Stages

1. **Framework Detection** - Identified ESG reporting frameworks used in the document
2. **ESG Claims Extraction** - Extracted key sustainability claims from the document
3. **Claims Validation** - Assessed claims for potential greenwashing using compliance standards

## Framework Detection Results

{framework_str}

## ESG Analysis and Claims Validation Results

{remaining_str}

## Processing Details

- **Total Processing Time:** {f"{processing_time:.2f} seconds" if processing_time else "Not recorded"}
- **Analysis Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Document Analyzed:** {file_path if file_path else "Not specified"}

## Workflow Performance

This analysis was performed using the enhanced greenwashing detection system with:
- Smart chunking for large documents
- Framework detection with confidence scoring
- Comprehensive claims extraction and validation
- Detailed logging and output generation

---
*Report generated by Greenwashing Detector Analysis System*
"""
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"💾 Workflow summary saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving workflow summary to markdown: {e}")
            return None

    def save_enhanced_workflow_summary_to_md(self, framework_result, fluff_result, chatgpt_result, file_path: str = None, processing_time: float = None):
        """
        Save a comprehensive enhanced workflow summary to a markdown file in the output folder.
        
        Args:
            framework_result: The framework detection result
            fluff_result: The fluff removal result
            chatgpt_result: The ChatGPT analysis result
            file_path: Optional custom file path
            processing_time: Total processing time in seconds
        """
        try:
            import os
            from datetime import datetime
            
            # Convert CrewOutput to string if needed
            if hasattr(framework_result, 'raw'):
                framework_str = str(framework_result.raw)
            else:
                framework_str = str(framework_result)
                
            if hasattr(fluff_result, 'raw'):
                fluff_str = str(fluff_result.raw)
            else:
                fluff_str = str(fluff_result)
                
            if hasattr(chatgpt_result, 'raw'):
                chatgpt_str = str(chatgpt_result.raw)
            else:
                chatgpt_str = str(chatgpt_result)
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_path:
                # Extract filename from provided path
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                filename = f"enhanced_workflow_summary_{base_name}_{timestamp}.md"
            else:
                filename = f"enhanced_workflow_summary_{timestamp}.md"
            
            output_path = os.path.join(output_dir, filename)
            
            # Create markdown content
            md_content = f"""# Enhanced Greenwashing Detection Workflow Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**PDF File:** {file_path if file_path else "Not specified"}
**Processing Time:** {f"{processing_time:.2f} seconds" if processing_time else "Not recorded"}

## Enhanced Workflow Overview

This report summarizes the enhanced greenwashing detection workflow execution, including fluff removal and ChatGPT-optimized chunking.

### Enhanced Workflow Stages

1. **Framework Detection (Ollama)** - Identified ESG reporting frameworks using local Ollama model
2. **Fluff Removal (Ollama)** - Removed unnecessary content and marketing language using local Ollama model
3. **ChatGPT Chunking** - Processed cleaned content with intelligent chunking for ChatGPT (16K token limit)
4. **ESG Analysis (ChatGPT)** - Extracted key sustainability claims from cleaned content
5. **Claims Validation (ChatGPT)** - Assessed claims for potential greenwashing using compliance standards

## Framework Detection Results (Ollama)

{framework_str}

## Fluff Removal Results (Ollama)

{fluff_str}

## ESG Analysis and Claims Validation Results (ChatGPT)

{chatgpt_str}

## Processing Details

- **Total Processing Time:** {f"{processing_time:.2f} seconds" if processing_time else "Not recorded"}
- **Analysis Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Document Analyzed:** {file_path if file_path else "Not specified"}

## Enhanced Workflow Performance

This analysis was performed using the enhanced greenwashing detection system with:
- **Ollama Integration**: Local model processing for framework detection and fluff removal
- **Intelligent Fluff Removal**: Surgical removal of marketing language while preserving ESG content
- **ChatGPT Optimization**: Smart chunking for 16K token limit with overlap and sentence boundary detection
- **Hybrid Model Approach**: Ollama for initial processing, ChatGPT for detailed analysis
- **Comprehensive Logging**: Detailed output generation for all workflow stages

## Model Usage

- **Ollama (llama2:latest)**: Framework detection and fluff removal
- **ChatGPT (gpt-3.5-turbo-0125)**: ESG claims extraction and greenwashing validation
- **Smart Chunking**: Optimized for ChatGPT's 16K token context window

---
*Report generated by Enhanced Greenwashing Detector Analysis System*
"""
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"💾 Enhanced workflow summary saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving enhanced workflow summary to markdown: {e}")
            return None