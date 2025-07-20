# src/greenwashing_detector/tools/pdf_loader.py

from crewai.tools import BaseTool
from PyPDF2 import PdfReader
import os
import re
from typing import Annotated, List, Dict, Tuple, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
import logging
import pytesseract
from PIL import Image
import io
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFReportReader(BaseTool):
    name: Annotated[str, "PDFReportReader"] = "PDFReportReader"
    description: Annotated[str, "Tool description"] = "Extracts and chunks raw text from a given sustainability PDF report to avoid LLM token limits."

    def extract_framework_sections(self, full_text: str) -> str:
        """
        Extract sections most likely to contain framework mentions.
        These sections typically contain framework declarations and methodology.
        """
        # Define key sections that typically contain framework information
        framework_sections = [
            r"about this report",
            r"reporting approach",
            r"methodology",
            r"assurance",
            r"reporting standards",
            r"framework",
            r"compliance",
            r"third-party",
            r"verification",
            r"certification",
            r"standards",
            r"guidelines",
            r"principles",
            r"scope",
            r"boundary",
            r"materiality",
            r"stakeholder",
            r"governance",
            r"disclosure",
            r"transparency"
        ]
        
        # Split text into paragraphs
        paragraphs = full_text.split('\n\n')
        relevant_sections = []
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Check if paragraph contains framework-related keywords
            framework_keywords = [
                "gri", "tcfd", "sasb", "cdp", "iso", "ghg", "isae", "csrd", "esrs",
                "ifrs", "sustainability", "esg", "reporting", "standard", "framework",
                "accordance", "compliance", "assurance", "verification", "certification"
            ]
            
            # Check for section headers that might contain framework info
            section_match = any(re.search(section, paragraph_lower) for section in framework_sections)
            
            # Check for framework keywords
            keyword_match = any(keyword in paragraph_lower for keyword in framework_keywords)
            
            # Check for explicit framework mentions
            explicit_frameworks = [
                r"global reporting initiative",
                r"task force on climate",
                r"sustainability accounting standards",
                r"carbon disclosure project",
                r"international organization for standardization",
                r"greenhouse gas protocol",
                r"international standard on assurance engagements",
                r"corporate sustainability reporting directive",
                r"european sustainability reporting standards",
                r"international financial reporting standards",
                r"GRI",
                r"TCFD",
                r"SASB",
                r"CDP",
                r"ISO",
                r"GHG Protocol",
                r"ISAE",
                r"CSR",
                r"ESRS",
                r"IFRS",
            ]
            
            explicit_match = any(re.search(framework, paragraph_lower) for framework in explicit_frameworks)
            
            if section_match or keyword_match or explicit_match:
                relevant_sections.append(paragraph)
        
        # If we found relevant sections, return them
        if relevant_sections:
            return '\n\n'.join(relevant_sections)
        else:
            # Fallback: return first few paragraphs (likely to contain executive summary)
            return '\n\n'.join(paragraphs[:5])

    def smart_chunk_pdf_text(self, full_text: str, chunk_size: int = 2000, chunk_overlap: int = 200, max_chunks: int = 3) -> str:
        """
        Smart chunking that focuses on sections most likely to contain framework mentions.
        """
        # Extract framework-relevant sections first
        framework_sections = self.extract_framework_sections(full_text)
        
        # If framework sections are substantial, use them
        if len(framework_sections) > 1000:
            text_to_chunk = framework_sections
            print(f"🎯 Using smart chunking: Found {len(framework_sections)} chars of framework-relevant content")
        else:
            # Fallback to regular chunking if not enough framework content found
            text_to_chunk = full_text
            print(f"⚠️  Smart chunking fallback: Using full text ({len(full_text)} chars)")
        
        # Apply chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )
        chunks = splitter.split_text(text_to_chunk)
        
        # Return the most relevant chunks
        result = "\n\n".join(chunks[:max_chunks])
        
        print(f"📊 Smart chunking result: {len(result)} chars from {len(text_to_chunk)} chars input")
        return result

    def chunk_pdf_text(self, full_text: str, chunk_size: int = 2000, chunk_overlap: int = 200, max_chunks: int = 2) -> str:
        """Legacy chunking function - now uses smart chunking by default."""
        return self.smart_chunk_pdf_text(full_text, chunk_size, chunk_overlap, max_chunks)

    def _run(self, file_path: str) -> str:
        """Implementation of the tool's functionality"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Use smart chunking for framework detection
            chunked_text = self.smart_chunk_pdf_text(text)
            return f"PDF Text (Smart Chunked for Framework Detection):\n\n{chunked_text}"
                
        except Exception as e:
            return f"Failed to read PDF: {str(e)}"

class SmartChunkingProcessor:
    """
    Enhanced smart chunking with OCR and TOC detection for framework detection.
    """
    
    def __init__(self):
        self.framework_keywords = [
            'framework', 'standard', 'guideline', 'protocol', 'methodology',
            'reporting', 'assurance', 'certification', 'compliance', 'alignment',
            'gri', 'tcfd', 'sasb', 'cdp', 'csrd', 'esrs', 'iso', 'ipieca',
            'ghg protocol', 'isae', 'osha', 'api', 'sdgs', 'un sustainable'
        ]
        
        self.toc_indicators = [
            'contents', 'table of contents', 'index', 'overview',
            'about this report', 'methodology', 'reporting approach',
            'assurance', 'governance', 'data', 'appendix'
        ]
        
        self.framework_sections = [
            'about this report', 'reporting standards', 'methodology',
            'assurance', 'governance', 'data', 'compliance',
            'reporting boundaries', 'basis of preparation'
        ]

    def extract_toc(self, doc) -> List[Dict]:
        """
        Extract table of contents using multiple methods.
        """
        toc_entries = []
        
        # Method 1: Look for common TOC patterns in text
        for page_num in range(min(10, len(doc))):  # Check first 10 pages
            page = doc[page_num]
            text = page.get_text()
            
            # Look for page numbers and section titles
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Pattern: "Section Title ................ 15" or "Section Title 15"
                if re.search(r'\.{3,}\s*\d+$', line) or re.search(r'\s+\d+$', line):
                    # Extract title and page number
                    title_match = re.match(r'^(.+?)(?:\.{3,}\s*|\s+)(\d+)$', line)
                    if title_match:
                        title, page_num_str = title_match.groups()
                        toc_entries.append({
                            'title': title.strip(),
                            'page': int(page_num_str),
                            'confidence': 'high'
                        })
                
                # Look for section headers with numbers
                elif re.match(r'^\d+\.?\s+[A-Z]', line):
                    toc_entries.append({
                        'title': line,
                        'page': page_num + 1,
                        'confidence': 'medium'
                    })
        
        # Method 2: Use document structure (if available)
        if hasattr(doc, 'get_toc'):
            try:
                doc_toc = doc.get_toc()
                for entry in doc_toc:
                    toc_entries.append({
                        'title': entry[1],
                        'page': entry[2],
                        'confidence': 'high'
                    })
            except:
                pass
        
        return toc_entries

    def detect_framework_sections(self, doc, toc_entries: List[Dict]) -> List[Dict]:
        """
        Identify sections most likely to contain framework information.
        """
        framework_sections = []
        
        # Use TOC to find relevant sections
        for entry in toc_entries:
            title_lower = entry['title'].lower()
            
            # Check if section title contains framework-related keywords
            if any(keyword in title_lower for keyword in self.framework_sections):
                framework_sections.append({
                    'title': entry['title'],
                    'page': entry['page'],
                    'confidence': 'high',
                    'reason': 'TOC match'
                })
        
        # If no TOC matches, scan text for framework sections
        if not framework_sections:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().lower()
                
                # Look for section headers
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if any(section in line for section in self.framework_sections):
                        framework_sections.append({
                            'title': line,
                            'page': page_num + 1,
                            'confidence': 'medium',
                            'reason': 'Text scan'
                        })
        
        return framework_sections

    def extract_text_with_ocr(self, page) -> str:
        """
        Extract text from page using OCR if regular text extraction fails.
        """
        # First try regular text extraction
        text = page.get_text()
        
        # If text is minimal or seems like it might be an image, use OCR
        if len(text.strip()) < 100:  # Threshold for minimal text
            try:
                # Convert page to image
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Use OCR to extract text
                ocr_text = pytesseract.image_to_string(img)
                
                if len(ocr_text.strip()) > len(text.strip()):
                    logger.info(f"OCR extracted {len(ocr_text)} chars vs {len(text)} chars from regular extraction")
                    return ocr_text
                    
            except Exception as e:
                logger.warning(f"OCR failed: {e}")
        
        return text

    def create_smart_chunks(self, doc, target_chunk_size: int = 2000) -> List[str]:
        """
        Create intelligent chunks focused on framework-relevant content.
        """
        logger.info("🔍 Creating smart chunks with OCR and TOC detection...")
        
        # Step 1: Extract TOC
        toc_entries = self.extract_toc(doc)
        logger.info(f"📋 Found {len(toc_entries)} TOC entries")
        
        # Step 2: Identify framework-relevant sections
        framework_sections = self.detect_framework_sections(doc, toc_entries)
        logger.info(f"🎯 Identified {len(framework_sections)} framework-relevant sections")
        
        # Step 3: Create prioritized chunks
        chunks = []
        
        # Priority 1: Framework-relevant sections
        for section in framework_sections:
            page_num = section['page'] - 1  # Convert to 0-based index
            
            if 0 <= page_num < len(doc):
                page = doc[page_num]
                text = self.extract_text_with_ocr(page)
                
                # Create chunk with context
                chunk = f"=== FRAMEWORK SECTION: {section['title']} (Page {section['page']}) ===\n\n"
                chunk += text
                
                if len(chunk) > target_chunk_size:
                    # Split large chunks
                    sub_chunks = self.split_chunk(chunk, target_chunk_size)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(chunk)
        
        # Priority 2: Look for framework keywords in remaining pages
        if len(chunks) < 3:  # If we don't have enough framework-specific chunks
            logger.info("🔍 Scanning remaining pages for framework keywords...")
            
            for page_num in range(len(doc)):
                # Skip pages we already processed
                if any(f"Page {page_num + 1}" in chunk for chunk in chunks):
                    continue
                
                page = doc[page_num]
                text = self.extract_text_with_ocr(page)
                
                # Check if page contains framework keywords
                text_lower = text.lower()
                keyword_matches = sum(1 for keyword in self.framework_keywords if keyword in text_lower)
                
                if keyword_matches >= 2:  # At least 2 framework keywords
                    chunk = f"=== KEYWORD MATCH: Page {page_num + 1} ({keyword_matches} framework keywords) ===\n\n"
                    chunk += text
                    
                    if len(chunk) > target_chunk_size:
                        sub_chunks = self.split_chunk(chunk, target_chunk_size)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(chunk)
        
        # Priority 3: Add overview/executive summary if available
        if chunks:
            # Look for executive summary or overview in first few pages
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                text = self.extract_text_with_ocr(page)
                text_lower = text.lower()
                
                if any(word in text_lower for word in ['executive summary', 'overview', 'about this report']):
                    chunk = f"=== EXECUTIVE SUMMARY: Page {page_num + 1} ===\n\n"
                    chunk += text
                    chunks.insert(0, chunk)  # Add at beginning
                    break
        
        logger.info(f"✅ Created {len(chunks)} smart chunks")
        return chunks

    def split_chunk(self, chunk: str, target_size: int) -> List[str]:
        """
        Split a large chunk into smaller pieces while preserving context.
        """
        if len(chunk) <= target_size:
            return [chunk]
        
        chunks = []
        current_chunk = ""
        lines = chunk.split('\n')
        
        for line in lines:
            if len(current_chunk + line) > target_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

class FrameworkPDFReader(PDFReportReader):
    """
    Enhanced PDF reader with smart chunking, OCR, and TOC detection for framework detection.
    """
    
    name: str = "FrameworkPDFReader"
    description: str = """
    Enhanced PDF reader that uses smart chunking with OCR and TOC detection to extract 
    framework-relevant content from sustainability reports. Focuses on sections most likely 
    to contain ESG framework mentions.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize smart processor after parent initialization
        self._smart_processor = SmartChunkingProcessor()

    def _run(self, file_path: str) -> str:
        """
        Extract framework-relevant content using smart chunking with OCR and TOC detection.
        """
        try:
            logger.info(f"📄 Reading PDF with smart chunking: {file_path}")
            
            # Open PDF
            doc = fitz.open(file_path)
            logger.info(f"📊 PDF has {len(doc)} pages")
            
            # Create smart chunks
            chunks = self._smart_processor.create_smart_chunks(doc)
            
            if not chunks:
                logger.warning("⚠️ No smart chunks created, falling back to regular extraction")
                # Fallback to regular text extraction
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                return text
            
            # Combine chunks with clear separators
            combined_text = "\n\n" + "="*80 + "\n\n".join(chunks)
            
            logger.info(f"✅ Smart chunking completed: {len(chunks)} chunks, {len(combined_text)} characters")
            
            doc.close()
            return combined_text
            
        except Exception as e:
            logger.error(f"❌ Error in smart PDF reading: {e}")
            return f"Error reading PDF: {str(e)}"

class FullPDFReader(PDFReportReader):
    """PDF reader that chunks full text for ESG analysis with result aggregation."""
    
    name: Annotated[str, "FullPDFReader"] = "FullPDFReader"
    description: Annotated[str, "Tool description"] = "Extracts and chunks full text from sustainability PDF reports for comprehensive ESG analysis, with result aggregation capabilities."

    def chunk_for_esg_analysis(self, full_text: str, chunk_size: int = 3500, chunk_overlap: int = 300, max_chunks: int = 5) -> List[str]:
        """
        Chunk the full text for ESG analysis with larger chunks and overlap.
        Returns a list of chunks for processing.
        """
        # Apply chunking with larger chunks for ESG analysis
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )
        chunks = splitter.split_text(full_text)
        
        # Limit to max_chunks to avoid overwhelming the LLM
        limited_chunks = chunks[:max_chunks]
        
        print(f"📄 ESG Analysis Chunking: {len(full_text)} chars → {len(limited_chunks)} chunks")
        print(f"   📏 Average chunk size: {sum(len(chunk) for chunk in limited_chunks) // len(limited_chunks)} chars")
        
        return limited_chunks

    def _run(self, file_path: str) -> str:
        """Implementation for full text extraction with chunking for ESG analysis."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Check if text is too large and needs chunking
            if len(text) > 15000:  # Rough estimate: 15K chars ≈ 4000 tokens
                print(f"⚠️  Large PDF detected ({len(text)} chars). Using chunking for ESG analysis.")
                chunks = self.chunk_for_esg_analysis(text)
                
                # Return the first chunk with information about total chunks
                first_chunk = chunks[0]
                chunk_info = f"\n\n[NOTE: This is chunk 1 of {len(chunks)}. Total PDF size: {len(text)} characters]"
                
                return f"PDF Text (Chunk 1 of {len(chunks)} for ESG Analysis):\n\n{first_chunk}{chunk_info}"
            else:
                # For smaller PDFs, return full text
                return f"PDF Text (Full Report for ESG Analysis):\n\n{text}"
                
        except Exception as e:
            return f"Failed to read PDF: {str(e)}"

class ESGChunkProcessor:
    """Helper class to process multiple chunks for ESG analysis and aggregate results."""
    
    def __init__(self, pdf_reader: FullPDFReader):
        self.pdf_reader = pdf_reader
    
    def process_all_chunks(self, file_path: str) -> List[str]:
        """Process all chunks of a PDF and return results for each chunk."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            chunks = self.pdf_reader.chunk_for_esg_analysis(text)
            return chunks
            
        except Exception as e:
            return [f"Failed to process PDF: {str(e)}"]
    
    def aggregate_esg_claims(self, chunk_results: List[str]) -> str:
        """Aggregate ESG claims from multiple chunk results."""
        aggregated = []
        aggregated.append("# ESG Analysis Results (Aggregated from Multiple Chunks)")
        aggregated.append(f"Total chunks processed: {len(chunk_results)}")
        aggregated.append("\n" + "="*50 + "\n")
        
        for i, result in enumerate(chunk_results, 1):
            aggregated.append(f"## Chunk {i} Results")
            aggregated.append(result)
            aggregated.append("\n" + "-"*30 + "\n")
        
        return "\n".join(aggregated)
