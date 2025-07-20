#!/usr/bin/env python3
"""
Debug script to search for exact occurrences of "CDP" in the full report.
"""

import os
import re
from PyPDF2 import PdfReader

def search_for_cdp():
    """Search for exact occurrences of 'CDP' in the full report."""
    
    pdf_path = "output/standard-chartered-plc-full-year-2024-report.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"📄 Processing PDF: {pdf_path}")
    
    # Extract PDF content
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    print(f"📊 PDF content length: {len(text)} characters")
    
    # Search for exact occurrences of "CDP"
    cdp_occurrences = []
    
    # Method 1: Simple string search
    simple_count = text.count("CDP")
    print(f"\n🔍 Simple string count of 'CDP': {simple_count}")
    
    # Method 2: Case-insensitive search
    cdp_lower_count = text.lower().count("cdp")
    print(f"🔍 Case-insensitive count of 'cdp': {cdp_lower_count}")
    
    # Method 3: Regex search with word boundaries
    cdp_regex = re.findall(r'\bCDP\b', text)
    print(f"🔍 Regex word boundary count of 'CDP': {len(cdp_regex)}")
    
    # Method 4: Find all occurrences with context
    lines = text.split('\n')
    for line_num, line in enumerate(lines):
        if 'CDP' in line:
            cdp_occurrences.append({
                'line': line_num + 1,
                'context': line.strip()[:200] + "..." if len(line) > 200 else line.strip()
            })
    
    print(f"\n📋 Found {len(cdp_occurrences)} lines containing 'CDP':")
    for i, occurrence in enumerate(cdp_occurrences):
        print(f"  {i+1}. Line {occurrence['line']}: {occurrence['context']}")
    
    # Method 5: Search for CDP-related terms
    cdp_related_terms = ['CDP', 'Carbon Disclosure Project', 'carbon disclosure']
    print(f"\n🔍 Searching for CDP-related terms:")
    for term in cdp_related_terms:
        count = text.count(term)
        print(f"  '{term}': {count} occurrences")
    
    # Method 6: Check if CDP appears in framework detection patterns
    cdp_patterns = ["CDP", "Carbon Disclosure Project", "CDP reporting"]
    print(f"\n🔍 Checking CDP patterns used in framework detection:")
    for pattern in cdp_patterns:
        count = text.count(pattern)
        print(f"  '{pattern}': {count} occurrences")
    
    return {
        'simple_count': simple_count,
        'case_insensitive_count': cdp_lower_count,
        'regex_count': len(cdp_regex),
        'line_occurrences': cdp_occurrences
    }

if __name__ == "__main__":
    search_for_cdp() 