#!/usr/bin/env python3
"""
Final Framework Detection Test with Corrected Classification Logic
Tests the smart framework detection algorithm on the City Cement Sustainability Report.
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_pdf_content(pdf_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            return content
    except ImportError:
        logger.error("PyPDF2 not available. Please install: pip install PyPDF2")
        return ""
    except Exception as e:
        logger.error(f"Error extracting PDF content: {e}")
        return ""

def find_framework_occurrences_smart(content: str, framework_patterns: Dict) -> List[Dict]:
    """Find framework occurrences with smart patterns and word boundaries."""
    occurrences = []
    
    for framework_name, patterns in framework_patterns.items():
        for pattern_info in patterns['search_patterns']:
            pattern_type = pattern_info['type']
            pattern_text = pattern_info['text']
            
            # Create regex pattern with word boundaries
            if pattern_type == 'exact':
                # Exact match with word boundaries
                regex_pattern = r'\b' + re.escape(pattern_text) + r'\b'
            elif pattern_type == 'phrase':
                # Phrase match (case insensitive)
                regex_pattern = r'\b' + re.escape(pattern_text) + r'\b'
            elif pattern_type == 'standard':
                # Standard match (case insensitive)
                regex_pattern = r'\b' + re.escape(pattern_text) + r'\b'
            else:
                continue
            
            # Find all matches
            matches = re.finditer(regex_pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Extract sentence context
                start_pos = max(0, match.start() - 200)
                end_pos = min(len(content), match.end() + 200)
                context = content[start_pos:end_pos]
                
                # Find sentence boundaries
                sentence_start = context.rfind('.', 0, 200) + 1
                sentence_end = context.find('.', 200)
                if sentence_end == -1:
                    sentence_end = len(context)
                
                sentence = context[sentence_start:sentence_end].strip()
                
                occurrences.append({
                    'framework': framework_name,
                    'pattern': pattern_text,
                    'pattern_type': pattern_type,
                    'start': match.start(),
                    'end': match.end(),
                    'sentence': sentence,
                    'full_context': context
                })
    
    return occurrences

def analyze_framework_context_smart(occurrences: List[Dict]) -> Dict:
    """Analyze context for each framework with intelligent evidence classification."""
    framework_analysis = {}
    
    # Define evidence indicators with proper classification
    evidence_indicators = {
        'GRI': {
            'primary': [
                'gri standards', 'global reporting initiative', 'in accordance', 
                'prepared following', 'meets requirements', 'reporting framework'
            ],
            'secondary': [
                'gri', 'reporting', 'disclosure', 'sustainability'
            ],
            'compliance': [
                'compliance', 'certified', 'audited', 'verified'
            ]
        },
        'ISO': {
            'primary': [
                'report prepared following iso', 'report in accordance with iso', 
                'sustainability report based on iso', 'esg reporting following iso',
                'iso reporting framework', 'iso sustainability standards'
            ],
            'secondary': [
                'iso 14001', 'iso 14064', 'iso 26000', 'iso 50001',
                'iso certification', 'iso management system', 'iso environmental management',
                'iso quality management', 'iso energy management'
            ],
            'compliance': [
                'iso certified', 'iso audited', 'iso verified', 'iso accredited'
            ]
        },
        'IFRS': {
            'primary': [
                'international financial reporting standards', 'ifrs s1', 'ifrs s2'
            ],
            'secondary': [
                'ifrs financial reporting', 'ifrs accounting standards', 'ifrs financial statements'
            ],
            'compliance': [
                'ifrs compliance', 'ifrs adoption', 'ifrs implementation'
            ]
        },
        'TCFD': {
            'primary': [
                'task force on climate-related financial disclosures', 'tcfd'
            ],
            'secondary': [
                'climate risk', 'climate disclosure', 'climate-related'
            ],
            'compliance': [
                'compliance', 'alignment', 'adoption'
            ]
        },
        'SASB': {
            'primary': [
                'sustainability accounting standards board', 'sasb standards'
            ],
            'secondary': [
                'sasb', 'accounting standards', 'sustainability accounting'
            ],
            'compliance': [
                'compliance', 'adoption', 'implementation'
            ]
        },
        'CDP': {
            'primary': [
                'carbon disclosure project', 'cdp'
            ],
            'secondary': [
                'carbon disclosure', 'climate disclosure', 'emissions disclosure'
            ],
            'compliance': [
                'response', 'submission', 'participation'
            ]
        },
        'CSRD': {
            'primary': [
                'corporate sustainability reporting directive', 'csrd', 'esrs'
            ],
            'secondary': [
                'sustainability reporting', 'esg reporting', 'non-financial reporting'
            ],
            'compliance': [
                'compliance', 'implementation', 'adoption'
            ]
        }
    }
    
    for occurrence in occurrences:
        framework = occurrence['framework']
        sentence = occurrence['sentence'].lower()
        
        if framework not in framework_analysis:
            framework_analysis[framework] = {
                'total_occurrences': 0,
                'relevant_occurrences': 0,
                'primary_evidence': 0,
                'secondary_evidence': 0,
                'compliance_evidence': 0,
                'evidence': [],
                'occurrences': []
            }
        
        framework_analysis[framework]['total_occurrences'] += 1
        
        # Check for evidence indicators
        primary_found = []
        secondary_found = []
        compliance_found = []
        
        if framework in evidence_indicators:
            indicators = evidence_indicators[framework]
            
            # Check primary indicators
            for indicator in indicators['primary']:
                if indicator in sentence:
                    primary_found.append(indicator)
            
            # Check secondary indicators
            for indicator in indicators['secondary']:
                if indicator in sentence:
                    secondary_found.append(indicator)
            
            # Check compliance indicators
            for indicator in indicators['compliance']:
                if indicator in sentence:
                    compliance_found.append(indicator)
        
        # Determine if this occurrence is relevant
        is_relevant = len(primary_found) > 0 or len(secondary_found) > 0 or len(compliance_found) > 0
        
        if is_relevant:
            framework_analysis[framework]['relevant_occurrences'] += 1
            framework_analysis[framework]['primary_evidence'] += len(primary_found)
            framework_analysis[framework]['secondary_evidence'] += len(secondary_found)
            framework_analysis[framework]['compliance_evidence'] += len(compliance_found)
            
            framework_analysis[framework]['evidence'].append({
                'sentence': occurrence['sentence'],
                'primary_indicators': primary_found,
                'secondary_indicators': secondary_found,
                'compliance_indicators': compliance_found,
                'pattern': occurrence['pattern'],
                'pattern_type': occurrence['pattern_type']
            })
        
        framework_analysis[framework]['occurrences'].append({
            'sentence': occurrence['sentence'],
            'is_relevant': is_relevant,
            'primary_indicators': primary_found,
            'secondary_indicators': secondary_found,
            'compliance_indicators': compliance_found,
            'pattern': occurrence['pattern'],
            'pattern_type': occurrence['pattern_type']
        })
    
    return framework_analysis

def calculate_framework_confidence_smart(framework_analysis: Dict) -> Dict:
    """Calculate confidence scores with corrected classification logic."""
    results = {}
    
    for framework_name, analysis in framework_analysis.items():
        total_occurrences = analysis['total_occurrences']
        relevant_occurrences = analysis['relevant_occurrences']
        primary_evidence = analysis['primary_evidence']
        secondary_evidence = analysis['secondary_evidence']
        compliance_evidence = analysis['compliance_evidence']
        
        if total_occurrences == 0:
            continue
        
        # Calculate evidence strength
        evidence_strength = (
            primary_evidence * 25 +      # Primary indicators are strongest
            compliance_evidence * 20 +   # Compliance indicators are strong
            secondary_evidence * 10      # Secondary indicators are weaker
        )
        
        # Calculate relevance ratio
        relevance_ratio = relevant_occurrences / total_occurrences if total_occurrences > 0 else 0
        
        # Calculate confidence based on evidence quality and quantity
        if relevant_occurrences == 0:
            confidence = min(10, total_occurrences * 2)
        elif relevant_occurrences == 1:
            if primary_evidence > 0:
                confidence = min(50 + evidence_strength, 70)
            else:
                confidence = min(30 + evidence_strength, 50)
        elif relevant_occurrences >= 2:
            if primary_evidence > 0:
                confidence = min(60 + evidence_strength, 85)
            else:
                confidence = min(40 + evidence_strength, 60)
        else:
            confidence = min(evidence_strength, 40)
        
        # CORRECTED: Determine role based on evidence quality
        # Only frameworks with strong primary evidence should be primary
        if primary_evidence >= 5:  # Require significant primary evidence for primary classification
            role = "primary"
        elif primary_evidence > 0 or compliance_evidence > 0:
            role = "secondary"
        else:
            role = "reference"
        
        results[framework_name] = {
            'confidence': confidence,
            'role': role,
            'total_occurrences': total_occurrences,
            'relevant_occurrences': relevant_occurrences,
            'relevance_ratio': relevance_ratio,
            'evidence_strength': evidence_strength,
            'primary_evidence': primary_evidence,
            'secondary_evidence': secondary_evidence,
            'compliance_evidence': compliance_evidence,
            'evidence': analysis['evidence'],
            'all_occurrences': analysis['occurrences']
        }
    
    return results

def detect_frameworks_smart(content: str) -> Dict:
    """Smart framework detection with proper word boundaries and intelligent analysis."""
    logger.info("🧠 Starting smart framework detection with word boundaries")
    
    # Define framework patterns with proper search patterns
    framework_patterns = {
        'GRI': {
            'search_patterns': [
                {'type': 'exact', 'text': 'GRI'},
                {'type': 'phrase', 'text': 'Global Reporting Initiative'},
                {'type': 'standard', 'text': 'GRI Standards'},
                {'type': 'standard', 'text': 'GRI Universal Standards'},
                {'type': 'standard', 'text': 'GRI Topic Standards'}
            ]
        },
        'TCFD': {
            'search_patterns': [
                {'type': 'exact', 'text': 'TCFD'},
                {'type': 'phrase', 'text': 'Task Force on Climate-related Financial Disclosures'}
            ]
        },
        'SASB': {
            'search_patterns': [
                {'type': 'exact', 'text': 'SASB'},
                {'type': 'phrase', 'text': 'Sustainability Accounting Standards Board'},
                {'type': 'standard', 'text': 'SASB Standards'}
            ]
        },
        'CDP': {
            'search_patterns': [
                {'type': 'exact', 'text': 'CDP'},
                {'type': 'phrase', 'text': 'Carbon Disclosure Project'}
            ]
        },
        'ISO': {
            'search_patterns': [
                {'type': 'standard', 'text': 'ISO 14064'},
                {'type': 'standard', 'text': 'ISO 14001'},
                {'type': 'standard', 'text': 'ISO 26000'},
                {'type': 'standard', 'text': 'ISO 50001'}
            ]
        },
        'IFRS': {
            'search_patterns': [
                {'type': 'standard', 'text': 'IFRS S1'},
                {'type': 'standard', 'text': 'IFRS S2'},
                {'type': 'phrase', 'text': 'International Financial Reporting Standards'}
            ]
        },
        'CSRD': {
            'search_patterns': [
                {'type': 'exact', 'text': 'CSRD'},
                {'type': 'phrase', 'text': 'Corporate Sustainability Reporting Directive'},
                {'type': 'exact', 'text': 'ESRS'}
            ]
        }
    }
    
    # Find all framework occurrences with smart patterns
    all_occurrences = find_framework_occurrences_smart(content, framework_patterns)
    
    logger.info(f"📊 Found {len(all_occurrences)} total framework occurrences with word boundaries")
    
    # Analyze context for each framework
    framework_analysis = analyze_framework_context_smart(all_occurrences)
    
    # Calculate confidence scores
    results = calculate_framework_confidence_smart(framework_analysis)
    
    # Convert to list format for consistency
    detected_frameworks = []
    for framework_name, result in results.items():
        if result['confidence'] > 0:
            detected_frameworks.append({
                'framework': framework_name,
                'confidence': result['confidence'],
                'role': result['role'],
                'total_occurrences': result['total_occurrences'],
                'relevant_occurrences': result['relevant_occurrences'],
                'relevance_ratio': result['relevance_ratio'],
                'evidence_strength': result['evidence_strength'],
                'primary_evidence': result['primary_evidence'],
                'secondary_evidence': result['secondary_evidence'],
                'compliance_evidence': result['compliance_evidence'],
                'evidence': result['evidence'],
                'all_occurrences': result['all_occurrences']
            })
    
    # Sort by confidence
    detected_frameworks.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'frameworks': detected_frameworks,
        'total_detected': len(detected_frameworks),
        'primary_frameworks': [f for f in detected_frameworks if f['role'] == 'primary'],
        'secondary_frameworks': [f for f in detected_frameworks if f['role'] == 'secondary'],
        'reference_frameworks': [f for f in detected_frameworks if f['role'] == 'reference'],
        'total_occurrences': len(all_occurrences)
    }

def generate_smart_report(detection_results: Dict) -> str:
    """Generate a comprehensive report for the smart framework detection."""
    report = []
    report.append("# Smart Framework Detection Report - FINAL CORRECTED")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("## Key Improvements")
    report.append("- ✅ Uses proper word boundaries (\\b) to avoid false matches")
    report.append("- ✅ Regex patterns prevent matching 'gri' in 'integrity' or 'agriculture'")
    report.append("- ✅ Intelligent context analysis with framework-specific indicators")
    report.append("- ✅ Evidence quality weighting (primary > compliance > secondary)")
    report.append("- ✅ CORRECTED: Proper primary/secondary classification logic")
    report.append("- ✅ CORRECTED: Only frameworks with strong primary evidence are primary")
    report.append("")
    
    # Summary
    report.append("## Summary")
    report.append(f"- Total frameworks detected: {detection_results['total_detected']}")
    report.append(f"- Primary frameworks: {len(detection_results['primary_frameworks'])}")
    report.append(f"- Secondary frameworks: {len(detection_results['secondary_frameworks'])}")
    report.append(f"- Reference frameworks: {len(detection_results['reference_frameworks'])}")
    report.append(f"- Total framework occurrences found: {detection_results['total_occurrences']}")
    report.append("")
    
    # Framework details
    for framework in detection_results['frameworks']:
        report.append(f"## {framework['framework']}")
        report.append(f"- **Confidence**: {framework['confidence']:.1f}%")
        report.append(f"- **Role**: {framework['role']}")
        report.append(f"- **Total Occurrences**: {framework['total_occurrences']}")
        report.append(f"- **Relevant Occurrences**: {framework['relevant_occurrences']}")
        report.append(f"- **Relevance Ratio**: {framework['relevance_ratio']:.2f}")
        report.append(f"- **Evidence Strength**: {framework['evidence_strength']:.1f}")
        report.append(f"- **Primary Evidence**: {framework['primary_evidence']}")
        report.append(f"- **Secondary Evidence**: {framework['secondary_evidence']}")
        report.append(f"- **Compliance Evidence**: {framework['compliance_evidence']}")
        report.append("")
        
        # Relevant evidence
        if framework['evidence']:
            report.append("### Relevant Evidence")
            for i, evidence in enumerate(framework['evidence'], 1):
                report.append(f"#### Evidence {i}")
                report.append(f"- **Sentence**: {evidence['sentence']}")
                if evidence['primary_indicators']:
                    report.append(f"- **Primary Indicators**: {', '.join(evidence['primary_indicators'])}")
                if evidence['secondary_indicators']:
                    report.append(f"- **Secondary Indicators**: {', '.join(evidence['secondary_indicators'])}")
                if evidence['compliance_indicators']:
                    report.append(f"- **Compliance Indicators**: {', '.join(evidence['compliance_indicators'])}")
                report.append(f"- **Pattern Matched**: {evidence['pattern']}")
                report.append("")
        
        # All occurrences (first 50 to avoid huge reports)
        report.append("### All Occurrences")
        for i, occurrence in enumerate(framework['all_occurrences'][:50], 1):
            status = "✅ RELEVANT" if occurrence['is_relevant'] else "❌ NOT RELEVANT"
            report.append(f"#### Occurrence {i} - {status}")
            report.append(f"- **Pattern**: {occurrence['pattern']} ({occurrence['pattern_type']})")
            report.append(f"- **Sentence**: {occurrence['sentence']}")
            if occurrence['primary_indicators']:
                report.append(f"- **Primary Indicators**: {', '.join(occurrence['primary_indicators'])}")
            if occurrence['secondary_indicators']:
                report.append(f"- **Secondary Indicators**: {', '.join(occurrence['secondary_indicators'])}")
            if occurrence['compliance_indicators']:
                report.append(f"- **Compliance Indicators**: {', '.join(occurrence['compliance_indicators'])}")
            report.append("")
        
        if len(framework['all_occurrences']) > 50:
            report.append(f"*... and {len(framework['all_occurrences']) - 50} more occurrences*")
            report.append("")
    
    return "\n".join(report)

def test_framework_detection_final():
    """Test the final corrected framework detection algorithm."""
    logger.info("🚀 Starting Final Framework Detection Test")
    logger.info("=" * 60)
    
    try:
        # Use the Standard Chartered PLC report
        pdf_path = "output/standard-chartered-plc-full-year-2024-report.pdf"
        
        if not os.path.exists(pdf_path):
            logger.error(f"❌ PDF file not found: {pdf_path}")
            return
        
        logger.info(f"📄 Processing PDF: {pdf_path}")
        
        # Extract PDF content
        pdf_content = extract_pdf_content(pdf_path)
        
        if not pdf_content:
            logger.error("❌ Failed to extract PDF content")
            return
        
        logger.info(f"📊 PDF content length: {len(pdf_content)} characters")
        
        # Run smart framework detection
        detection_results = detect_frameworks_smart(pdf_content)
        
        # Generate report
        report = generate_smart_report(detection_results)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"framework_detection_final_standard_chartered_{timestamp}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Final report saved to: {report_filename}")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("🎉 FINAL FRAMEWORK DETECTION COMPLETED!")
        logger.info("=" * 60)
        
        for framework in detection_results['frameworks']:
            logger.info(f"   🏷️  {framework['framework']}: {framework['confidence']:.1f}% ({framework['role']}) - {framework['relevant_occurrences']}/{framework['total_occurrences']} relevant")
        
        logger.info(f"\n🔗 Final Report: {os.path.abspath(report_filename)}")
        
        return {
            "success": True,
            "detection_results": detection_results,
            "report_filename": report_filename
        }
        
    except Exception as e:
        logger.error(f"❌ Final test failed: {e}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main function to run the test."""
    result = test_framework_detection_final()
    if result['success']:
        logger.info("✅ Final test completed successfully")
    else:
        logger.error("❌ Final test failed")

if __name__ == "__main__":
    main() 