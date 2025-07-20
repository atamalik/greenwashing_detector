#!/usr/bin/env python3
"""
Debug script to examine paragraph 13 to see what content is actually there.
"""

import os
from PyPDF2 import PdfReader

def examine_paragraph_13():
    """Examine paragraph 13 to see what content is actually there."""
    
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
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    
    print(f"📊 Total paragraphs: {len(paragraphs)}")
    
    # Examine paragraph 13
    if len(paragraphs) > 13:
        para_13 = paragraphs[13]
        print(f"\n📋 Paragraph 13 content:")
        print("=" * 80)
        print(para_13)
        print("=" * 80)
        
        # Search for specific words in paragraph 13
        para_13_lower = para_13.lower()
        
        print(f"\n🔍 Searching for specific words in paragraph 13:")
        search_words = ['cdp', 'participates', 'responds', 'prepared in accordance with', 'complies', 'implements']
        
        for word in search_words:
            if word in para_13_lower:
                print(f"  ✅ '{word}' found in paragraph 13")
            else:
                print(f"  ❌ '{word}' NOT found in paragraph 13")
        
        # Show context around CDP if it exists
        if 'cdp' in para_13_lower:
            cdp_index = para_13_lower.find('cdp')
            start = max(0, cdp_index - 100)
            end = min(len(para_13), cdp_index + 100)
            print(f"\n📝 Context around 'CDP' in paragraph 13:")
            print(f"  ...{para_13[start:end]}...")
        
        # Show context around "participates" if it exists
        if 'participates' in para_13_lower:
            participates_index = para_13_lower.find('participates')
            start = max(0, participates_index - 100)
            end = min(len(para_13), participates_index + 100)
            print(f"\n📝 Context around 'participates' in paragraph 13:")
            print(f"  ...{para_13[start:end]}...")
        
        # Show context around "responds" if it exists
        if 'responds' in para_13_lower:
            responds_index = para_13_lower.find('responds')
            start = max(0, responds_index - 100)
            end = min(len(para_13), responds_index + 100)
            print(f"\n📝 Context around 'responds' in paragraph 13:")
            print(f"  ...{para_13[start:end]}...")
    
    else:
        print(f"❌ Paragraph 13 not found. Only {len(paragraphs)} paragraphs available.")

if __name__ == "__main__":
    examine_paragraph_13() 