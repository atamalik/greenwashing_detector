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
from .tools.gri_analyzer import GRIAnalyzerTool
import re


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
            "TCFDAnalyzerTool": TCFDAnalyzerTool,
            "GRIAnalyzerTool": GRIAnalyzerTool
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
                self.tools["TCFDAnalyzerTool"](),
                self.tools["FrameworkGlossaryTool"](),
                self.tools["GRIAnalyzerTool"]()
            ]
        )

    @agent
    def compliance_checker(self) -> Agent:
        config = self.agents_config['compliance_checker'].copy()
        if 'tools' in config:
            del config['tools']
        return Agent(
            **config,
            tools=[
                self.tools["TCFDAnalyzerTool"](),
                self.tools["FrameworkGlossaryTool"](),
                self.tools["GRIAnalyzerTool"]()
            ]
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

    def process_fluff_removed_content_with_chatgpt(self, cleaned_content: str, max_tokens_per_chunk: int = 6000) -> str:
        """
        Process fluff-removed content with chunking optimized for ChatGPT (16K token limit).
        
        Args:
            cleaned_content: The cleaned content from the fluff remover
            max_tokens_per_chunk: Maximum tokens per chunk (default 6K to leave buffer for task descriptions)
            
        Returns:
            Processed content ready for ChatGPT analysis
        """
        try:
            logger.info("🧹 Processing fluff-removed content for ChatGPT analysis")
            logger.info(f"📄 Input content length: {len(cleaned_content)} characters")
            
            # More accurate token estimation (1 token ≈ 3.5 characters for English text)
            estimated_tokens = len(cleaned_content) // 3.5
            logger.info(f"📊 Estimated tokens: {estimated_tokens:,}")
            
            if estimated_tokens <= max_tokens_per_chunk:
                # Content fits in single chunk
                logger.info("✅ Content fits in single ChatGPT chunk")
                return cleaned_content
            else:
                # Need to chunk the content
                logger.info(f"🔄 Content needs chunking for ChatGPT (max {max_tokens_per_chunk:,} tokens per chunk)")
                
                # Calculate chunk size in characters (much more conservative)
                chunk_size_chars = int(max_tokens_per_chunk * 2.0)  # Much more conservative estimate
                overlap_chars = 50  # Minimal overlap to avoid token waste
                
                # Split content into chunks
                chunks = []
                start = 0
                chunk_num = 1
                
                while start < len(cleaned_content):
                    end = start + chunk_size_chars
                    
                    # Try to break at sentence boundary
                    if end < len(cleaned_content):
                        # Look for sentence endings within last 100 chars of chunk
                        for i in range(end, max(start + chunk_size_chars - 100, start), -1):
                            if cleaned_content[i] in '.!?':
                                end = i + 1
                                break
                    
                    chunk = cleaned_content[start:end]
                    chunks.append(chunk)
                    
                    logger.info(f"📄 Chunk {chunk_num}: {len(chunk)} characters (~{len(chunk)//3.0:.0f} tokens)")
                    
                    # Move start position with overlap
                    start = end - overlap_chars
                    chunk_num += 1
                    
                    # Safety check to prevent infinite loop
                    if start >= len(cleaned_content):
                        break
                
                logger.info(f"✅ Created {len(chunks)} chunks for ChatGPT processing")
                
                # For ChatGPT analysis, we need to process chunks separately, not combine them
                # Return the first chunk with information about total chunks
                if len(chunks) == 1:
                    return chunks[0]
                else:
                    # Return first chunk with chunk information
                    first_chunk = chunks[0]
                    chunk_info = f"\n\n--- CHUNK INFORMATION ---\n"
                    chunk_info += f"This is chunk 1 of {len(chunks)} total chunks.\n"
                    chunk_info += f"Total content length: {len(cleaned_content)} characters\n"
                    chunk_info += f"Estimated total tokens: {estimated_tokens:,}\n"
                    chunk_info += f"Chunk size: ~{chunk_size_chars} characters (~{chunk_size_chars//3.0:.0f} tokens)\n"
                    chunk_info += f"Please analyze this chunk for ESG claims and framework compliance.\n"
                    chunk_info += f"Additional chunks will be processed separately.\n"
                    
                    return f"{first_chunk}{chunk_info}"
                
        except Exception as e:
            logger.error(f"Error processing fluff-removed content: {e}")
            return f"Error processing cleaned content: {str(e)}"

    def process_all_chunks_for_chatgpt(self, cleaned_content: str, max_tokens_per_chunk: int = 5000) -> List[str]:
        """
        Process all chunks of fluff-removed content for ChatGPT analysis.
        Returns a list of chunks that can be processed separately.
        
        Args:
            cleaned_content: The cleaned content from the fluff remover
            max_tokens_per_chunk: Maximum tokens per chunk (default 5K to leave buffer)
            
        Returns:
            List of chunks ready for ChatGPT analysis
        """
        try:
            logger.info("🧹 Processing all chunks for ChatGPT analysis")
            logger.info(f"📄 Input content length: {len(cleaned_content)} characters")
            
            # More accurate token estimation
            estimated_tokens = len(cleaned_content) // 3.0
            logger.info(f"📊 Estimated tokens: {estimated_tokens:,}")
            
            if estimated_tokens <= max_tokens_per_chunk:
                # Content fits in single chunk
                logger.info("✅ Content fits in single ChatGPT chunk")
                return [cleaned_content]
            else:
                # Need to chunk the content
                logger.info(f"🔄 Content needs chunking for ChatGPT (max {max_tokens_per_chunk:,} tokens per chunk)")
                
                # Calculate chunk size in characters (more conservative)
                chunk_size_chars = int(max_tokens_per_chunk * 3.0)
                overlap_chars = 200
                
                # Split content into chunks
                chunks = []
                start = 0
                chunk_num = 1
                
                while start < len(cleaned_content):
                    end = start + chunk_size_chars
                    
                    # Try to break at sentence boundary
                    if end < len(cleaned_content):
                        for i in range(end, max(start + chunk_size_chars - 100, start), -1):
                            if cleaned_content[i] in '.!?':
                                end = i + 1
                                break
                    
                    chunk = cleaned_content[start:end]
                    
                    # Add chunk information
                    chunk_with_info = f"--- CHUNK {chunk_num} OF {estimated_tokens//max_tokens_per_chunk + 1} ---\n\n"
                    chunk_with_info += chunk
                    chunk_with_info += f"\n\n--- CHUNK {chunk_num} ANALYSIS INSTRUCTIONS ---\n"
                    chunk_with_info += f"Analyze this chunk for ESG claims, framework compliance, and potential greenwashing indicators.\n"
                    chunk_with_info += f"Focus on environmental, social, and governance disclosures.\n"
                    
                    chunks.append(chunk_with_info)
                    
                    logger.info(f"📄 Chunk {chunk_num}: {len(chunk)} characters (~{len(chunk)//3.0:.0f} tokens)")
                    
                    # Move start position with overlap
                    start = end - overlap_chars
                    chunk_num += 1
                    
                    # Safety check
                    if start >= len(cleaned_content):
                        break
                
                logger.info(f"✅ Created {len(chunks)} chunks for ChatGPT processing")
                return chunks
                
        except Exception as e:
            logger.error(f"Error processing all chunks: {e}")
            return [f"Error processing cleaned content: {str(e)}"]

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

    def _extract_detected_frameworks(self, framework_result) -> List[str]:
        """
        Extract detected frameworks from the framework detection result.
        Prioritizes primary frameworks over secondary/reference frameworks.
        
        Args:
            framework_result: The result from framework detection
            
        Returns:
            List of detected framework names (e.g., ["GRI", "TCFD"])
        """
        try:
            # Convert CrewOutput to string if needed
            if hasattr(framework_result, 'raw'):
                result_str = str(framework_result.raw)
            else:
                result_str = str(framework_result)
            
            detected_frameworks = []
            primary_frameworks = []
            secondary_frameworks = []
            reference_frameworks = []
            
            # Common framework names to look for
            framework_patterns = {
                "GRI": ["GRI", "Global Reporting Initiative"],
                "TCFD": ["TCFD", "Task Force on Climate-related Financial Disclosures"],
                "SASB": ["SASB", "Sustainability Accounting Standards Board"],
                "CDP": ["CDP", "Carbon Disclosure Project"],
                "CSRD": ["CSRD", "Corporate Sustainability Reporting Directive"],
                "ESRS": ["ESRS", "European Sustainability Reporting Standards"],
                "ISO": ["ISO 14064", "ISO 14001"],
                "SDG": ["SDG", "Sustainable Development Goals"]
            }
            
            result_lower = result_str.lower()
            
            # First pass: Look for role indicators with improved priority
            for framework, patterns in framework_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in result_lower:
                        # Look for role indicators in the same line or nearby
                        lines = result_str.split('\n')
                        for line in lines:
                            if pattern.lower() in line.lower():
                                line_lower = line.lower()
                                
                                # Check for PRIMARY indicators (strongest evidence)
                                primary_indicators = [
                                    "(primary)", "primary", "prepared in accordance with", 
                                    "this report follows", "we report in accordance with",
                                    "the report is prepared following"
                                ]
                                
                                # Check for SECONDARY indicators (weaker evidence)
                                secondary_indicators = [
                                    "(secondary)", "secondary", "voluntary", "publish against", 
                                    "additional", "supplementary", "aligned with", "consistent with"
                                ]
                                
                                # Check for REFERENCE indicators (weakest evidence)
                                reference_indicators = [
                                    "(reference)", "reference", "consideration to", 
                                    "mentioned for context", "but do not align in full with"
                                ]
                                
                                # Check for role indicators with priority
                                if any(indicator in line_lower for indicator in primary_indicators):
                                    primary_frameworks.append(framework)
                                    break
                                elif any(indicator in line_lower for indicator in secondary_indicators):
                                    secondary_frameworks.append(framework)
                                    break
                                elif any(indicator in line_lower for indicator in reference_indicators):
                                    reference_frameworks.append(framework)
                                    break
                        else:
                            # If no role indicator found, check confidence
                            if "confidence" in result_lower:
                                # Look for confidence scores
                                import re
                                for line in lines:
                                    if pattern.lower() in line.lower() and "confidence" in line.lower():
                                        # Extract confidence score
                                        confidence_match = re.search(r'(\d+)%', line)
                                        if confidence_match:
                                            confidence = int(confidence_match.group(1))
                                            if confidence >= 40:  # Only include if confidence >= 40%
                                                # Default to secondary if no role specified
                                                secondary_frameworks.append(framework)
                                            break
                            else:
                                # If no confidence mentioned, include as secondary
                                secondary_frameworks.append(framework)
                        break  # Only add each framework once
            
            # Prioritize frameworks: Primary first, then secondary, then reference
            detected_frameworks = primary_frameworks + secondary_frameworks + reference_frameworks
            
            # Remove duplicates while preserving order
            unique_frameworks = []
            for framework in detected_frameworks:
                if framework not in unique_frameworks:
                    unique_frameworks.append(framework)
            
            logger.info(f"🎯 Extracted frameworks: {unique_frameworks}")
            logger.info(f"   Primary: {primary_frameworks}")
            logger.info(f"   Secondary: {secondary_frameworks}")
            logger.info(f"   Reference: {reference_frameworks}")
            
            return unique_frameworks
            
        except Exception as e:
            logger.error(f"❌ Error extracting detected frameworks: {e}")
            return []

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
                filename = f"{agent_name}_{task_name}.md"
            else:
                filename = f"{agent_name}_{task_name}.md"
            
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
                filename = f"framework_detection.md"
            else:
                filename = f"framework_detection.md"
            
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
            simple_filename = f"framework_results.md"
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
                filename = f"workflow_summary.md"
            else:
                filename = f"workflow_summary.md"
            
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
                filename = f"enhanced_workflow_summary.md"
            else:
                filename = f"enhanced_workflow_summary.md"
            
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

    def is_tcfd_major_framework(self, detected_frameworks: List[str]) -> bool:
        """
        Determine if TCFD is a major framework that should trigger TCFD-specific analysis.
        
        Args:
            detected_frameworks: List of detected framework names
            
        Returns:
            True if TCFD is a major framework (primary or secondary with high confidence)
        """
        try:
            # Check if TCFD is in the detected frameworks
            if "TCFD" not in detected_frameworks:
                return False
            
            # Get the framework detection result to check confidence
            if hasattr(self, 'last_framework_result'):
                result_str = str(self.last_framework_result)
                
                # Look for TCFD confidence score
                import re
                tcfd_confidence_match = re.search(r'TCFD.*?Confidence.*?(\d+)%', result_str, re.IGNORECASE)
                if tcfd_confidence_match:
                    confidence = int(tcfd_confidence_match.group(1))
                    # TCFD is major if confidence >= 70%
                    return confidence >= 70
                
                # If no confidence found, check if TCFD is mentioned prominently
                tcfd_mentions = result_str.lower().count('tcfd')
                return tcfd_mentions >= 2  # Multiple mentions indicate major framework
            
            # Default: TCFD is major if it's in the detected frameworks
            return True
            
        except Exception as e:
            logger.error(f"Error determining TCFD major framework status: {e}")
            return False

    def get_tcfd_analysis_route(self, detected_frameworks: List[str]) -> str:
        """
        Determine the appropriate TCFD analysis route based on detected frameworks.
        
        Args:
            detected_frameworks: List of detected framework names
            
        Returns:
            Analysis route: 'tcfd_primary', 'tcfd_secondary', or 'standard'
        """
        try:
            if "TCFD" not in detected_frameworks:
                return "standard"
            
            # Get the framework detection result to check role
            if hasattr(self, 'last_framework_result'):
                result_str = str(self.last_framework_result)
                
                # Check if TCFD is marked as PRIMARY (case insensitive)
                if re.search(r'tcfd.*?primary|primary.*?tcfd', result_str, re.IGNORECASE):
                    return "tcfd_primary"
                
                # Check if TCFD is marked as SECONDARY
                if re.search(r'tcfd.*?secondary|secondary.*?tcfd', result_str, re.IGNORECASE):
                    return "tcfd_secondary"
            
            # Default: TCFD secondary if TCFD is detected
            return "tcfd_secondary"
            
        except Exception as e:
            logger.error(f"Error determining TCFD analysis route: {e}")
            return "tcfd_secondary"

    def create_tcfd_specialized_crew(self, analysis_route: str) -> Crew:
        """
        Create a specialized crew for TCFD analysis.
        
        Args:
            analysis_route: 'tcfd_primary' or 'tcfd_secondary'
            
        Returns:
            Specialized crew for TCFD analysis
        """
        from crewai import Crew, Process
        
        if analysis_route == "tcfd_primary":
            # For TCFD primary reports, focus heavily on TCFD analysis
            logger.info("🎯 Creating TCFD PRIMARY specialized crew")
            
            # Create TCFD-focused agents
            tcfd_analyst = Agent(
                role="TCFD Compliance Specialist",
                goal="Perform comprehensive TCFD compliance analysis across all four pillars with deep climate expertise",
                backstory="""You are a senior TCFD compliance specialist with 15+ years of experience in climate-related financial disclosures. 
                You have deep expertise in all four TCFD pillars: Governance, Strategy, Risk Management, and Metrics & Targets. 
                You specialize in identifying climate-related risks and opportunities, assessing scenario analysis quality, 
                and evaluating the integration of climate considerations into business strategy and financial planning.""",
                verbose=True,
                allow_delegation=False,
                tools=[
                    self.tools["TCFDAnalyzerTool"](),
                    self.tools["FrameworkGlossaryTool"]()
                ]
            )
            
            tcfd_validator = Agent(
                role="TCFD Greenwashing Detector",
                goal="Identify potential greenwashing in TCFD disclosures using climate-specific criteria",
                backstory="""You are a climate finance expert specializing in detecting greenwashing in TCFD disclosures. 
                You have extensive experience identifying misleading climate claims, incomplete scenario analysis, 
                and insufficient climate risk integration. You focus on climate-specific greenwashing indicators 
                such as missing Scope 3 emissions, vague climate commitments, and lack of financial impact assessment.""",
                verbose=True,
                allow_delegation=False,
                tools=[
                    self.tools["TCFDAnalyzerTool"](),
                    self.tools["FrameworkGlossaryTool"]()
                ]
            )
            
            # Create TCFD-specific tasks
            tcfd_analysis_task = Task(
                description="""Perform comprehensive TCFD compliance analysis using the TCFDAnalyzerTool.
                
                **TCFD PRIMARY ANALYSIS REQUIREMENTS**:
                
                1. **Governance Analysis (TCFD 1-2)**:
                   - Board oversight of climate issues
                   - Management's role in climate risk assessment
                   - Use TCFDAnalyzerTool with analysis_type="comprehensive"
                
                2. **Strategy Analysis (TCFD 3-5)**:
                   - Climate risk identification across time horizons
                   - Impact on business strategy and financial planning
                   - Climate scenario analysis and resilience assessment
                
                3. **Risk Management Analysis (TCFD 6-8)**:
                   - Climate risk identification and assessment processes
                   - Climate risk management processes
                   - Integration with overall risk management
                
                4. **Metrics & Targets Analysis (TCFD 9-11)**:
                   - Climate metrics and performance indicators
                   - Scope 1, 2, 3 emissions data and methodology
                   - Climate-related targets and performance tracking
                
                **OUTPUT FORMAT**:
                - Comprehensive TCFD compliance scores (0-100) for each pillar
                - Detailed analysis of each TCFD requirement
                - Identification of missing disclosures
                - Climate-specific recommendations
                - JSON-formatted results with greenwashing indicators
                
                Analyze the provided content: {esg_content}""",
                agent=tcfd_analyst,
                expected_output="Comprehensive TCFD compliance analysis with scores, missing elements, and recommendations"
            )
            
            tcfd_validation_task = Task(
                description="""Perform TCFD-specific greenwashing detection using climate-focused criteria.
                
                **TCFD GREENWASHING INDICATORS**:
                
                1. **Governance Greenwashing**:
                   - Missing board oversight of climate issues
                   - No clear climate governance structure
                   - Lack of climate expertise on board
                
                2. **Strategy Greenwashing**:
                   - Vague climate commitments without financial impact
                   - Missing scenario analysis or climate risk quantification
                   - No integration of climate risks into business strategy
                
                3. **Risk Management Greenwashing**:
                   - Incomplete climate risk identification
                   - Missing climate risk assessment processes
                   - No integration with overall risk management
                
                4. **Metrics & Targets Greenwashing**:
                   - Missing Scope 3 emissions or incomplete disclosure
                   - No time-bound climate targets or baselines
                   - Vague climate metrics without methodology
                
                **ANALYSIS APPROACH**:
                - Use TCFDAnalyzerTool for comprehensive analysis
                - Focus on climate-specific greenwashing patterns
                - Evaluate quality of climate disclosures
                - Assess financial impact integration
                
                **OUTPUT FORMAT**:
                - TCFD-specific greenwashing risk assessment
                - Climate disclosure quality evaluation
                - Specific recommendations for improvement
                - Framework-specific compliance validation
                
                Validate the TCFD analysis: {claims_content}""",
                agent=tcfd_validator,
                expected_output="TCFD-specific greenwashing assessment with climate-focused recommendations"
            )
            
            return Crew(
                agents=[tcfd_analyst, tcfd_validator],
                tasks=[tcfd_analysis_task, tcfd_validation_task],
                process=Process.sequential,
                verbose=True
            )
            
        else:  # tcfd_secondary
            # For TCFD secondary reports, include TCFD analysis alongside other frameworks
            logger.info("🔄 Creating TCFD SECONDARY specialized crew")
            
            # Use the existing ESG analyst and compliance checker but with TCFD focus
            esg_analyst = self.esg_analyst()
            compliance_checker = self.compliance_checker()
            
            # Create TCFD-enhanced tasks
            tcfd_enhanced_esg_task = Task(
                description="""Extract ESG claims with enhanced TCFD analysis for climate disclosures.
                
                **ENHANCED TCFD ANALYSIS** (since TCFD is a major framework):
                
                - **Climate Claims**: Focus on climate-related risks, opportunities, and financial impacts
                - **TCFD Alignment**: Assess alignment with TCFD recommendations
                - **Climate Metrics**: Extract climate-related metrics and targets
                - **Scenario Analysis**: Look for climate scenario analysis and resilience assessment
                
                **FRAMEWORK-SPECIFIC ANALYSIS**:
                
                - **For TCFD Claims**: Use TCFDAnalyzerTool with report_content={esg_content} and analysis_type="comprehensive"
                - **For GRI Claims**: Use GRIAnalyzerTool for GRI compliance assessment
                - **For Other Frameworks**: Use FrameworkGlossaryTool for general analysis
                
                **TCFD-SPECIFIC FOCUS AREAS**:
                1. Climate governance and oversight
                2. Climate strategy and financial planning
                3. Climate risk identification and management
                4. Climate metrics, targets, and performance
                5. Scenario analysis and climate resilience
                
                Extract ALL ESG claims with enhanced TCFD focus: {esg_content}""",
                agent=esg_analyst,
                expected_output="Comprehensive ESG claims extraction with enhanced TCFD analysis"
            )
            
            tcfd_enhanced_validation_task = Task(
                description="""Validate claims with enhanced TCFD greenwashing detection.
                
                **ENHANCED TCFD GREENWASHING ANALYSIS** (since TCFD is a major framework):
                
                **TCFD-Specific Greenwashing Indicators**:
                - Missing scenario analysis or climate risk quantification
                - Vague climate commitments without financial impact assessment
                - Lack of board oversight of climate issues
                - No integration of climate risks into business strategy
                - Missing Scope 3 emissions or incomplete emissions disclosure
                - No time-bound climate targets or baselines
                
                **FRAMEWORK-SPECIFIC VALIDATION**:
                
                - **For TCFD Claims**: Use TCFDAnalyzerTool for climate-specific validation
                - **For GRI Claims**: Use GRIAnalyzerTool for GRI-specific validation
                - **For Other Frameworks**: Use FrameworkGlossaryTool for general validation
                
                **TCFD-SPECIFIC CRITERIA**:
                1. Climate disclosure completeness and quality
                2. Financial impact assessment of climate issues
                3. Climate risk integration into business strategy
                4. Climate scenario analysis quality
                5. Climate governance and oversight effectiveness
                
                Validate ALL claims with enhanced TCFD focus: {claims_content}""",
                agent=compliance_checker,
                expected_output="Enhanced claims validation with TCFD-specific greenwashing detection"
            )
            
            return Crew(
                agents=[esg_analyst, compliance_checker],
                tasks=[tcfd_enhanced_esg_task, tcfd_enhanced_validation_task],
                process=Process.sequential,
                verbose=True
            )

    def chunk_esg_output_for_validation(self, esg_output: str, max_tokens_per_chunk: int = 4000) -> List[str]:
        """
        Chunk the ESG analyst output for claims validation to avoid token limits.
        
        Args:
            esg_output: The output from the ESG analyst
            max_tokens_per_chunk: Maximum tokens per chunk (default 4K to leave buffer)
            
        Returns:
            List of chunks ready for claims validation
        """
        try:
            logger.info("🔍 Chunking ESG output for claims validation")
            logger.info(f"📄 ESG output length: {len(esg_output)} characters")
            
            # More accurate token estimation
            estimated_tokens = len(esg_output) // 3.0
            logger.info(f"📊 Estimated tokens: {estimated_tokens:,}")
            
            if estimated_tokens <= max_tokens_per_chunk:
                # Output fits in single chunk
                logger.info("✅ ESG output fits in single validation chunk")
                return [esg_output]
            else:
                # Need to chunk the output
                logger.info(f"🔄 ESG output needs chunking for validation (max {max_tokens_per_chunk:,} tokens per chunk)")
                
                # Calculate chunk size in characters (more conservative)
                chunk_size_chars = int(max_tokens_per_chunk * 3.0)
                overlap_chars = 200
                
                # Split by sections first (look for markdown headers)
                import re
                sections = re.split(r'(## [^\n]+\n)', esg_output)
                
                chunks = []
                current_chunk = ""
                chunk_num = 1
                
                for section in sections:
                    # If adding this section would exceed chunk size, start a new chunk
                    if len(current_chunk + section) > chunk_size_chars and current_chunk:
                        # Add chunk information
                        chunk_with_info = f"--- ESG ANALYSIS CHUNK {chunk_num} ---\n\n"
                        chunk_with_info += current_chunk
                        chunk_with_info += f"\n\n--- VALIDATION INSTRUCTIONS ---\n"
                        chunk_with_info += f"Analyze the ESG claims above for potential greenwashing indicators.\n"
                        chunk_with_info += f"Focus on specificity, verifiability, and evidence quality.\n"
                        
                        chunks.append(chunk_with_info)
                        
                        logger.info(f"📄 Validation chunk {chunk_num}: {len(current_chunk)} characters (~{len(current_chunk)//3.5:.0f} tokens)")
                        
                        # Start new chunk with overlap
                        current_chunk = current_chunk[-overlap_chars:] + section
                        chunk_num += 1
                    else:
                        current_chunk += section
                
                # Add the last chunk
                if current_chunk.strip():
                    chunk_with_info = f"--- ESG ANALYSIS CHUNK {chunk_num} ---\n\n"
                    chunk_with_info += current_chunk
                    chunk_with_info += f"\n\n--- VALIDATION INSTRUCTIONS ---\n"
                    chunk_with_info += f"Analyze the ESG claims above for potential greenwashing indicators.\n"
                    chunk_with_info += f"Focus on specificity, verifiability, and evidence quality.\n"
                    
                    chunks.append(chunk_with_info)
                    
                    logger.info(f"📄 Validation chunk {chunk_num}: {len(current_chunk)} characters (~{len(current_chunk)//3.5:.0f} tokens)")
                
                logger.info(f"✅ Created {len(chunks)} chunks for claims validation")
                return chunks
                
        except Exception as e:
            logger.error(f"Error chunking ESG output: {e}")
            return [esg_output]  # Fallback to single chunk