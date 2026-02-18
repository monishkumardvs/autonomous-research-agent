"""
Test PDF Reading - Autonomous Research Assistant
Extracts text from a PDF and displays the first 1000 characters.
"""

import pdfplumber
import sys
import os

def test_pdf_reading(file_path):
    """Test basic PDF text extraction."""
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return False
    
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"✅ PDF opened successfully!")
            print(f"📄 Total pages: {len(pdf.pages)}")
            print(f"\n{'='*60}")
            print(f"EXTRACTING FIRST 2 PAGES")
            print(f"{'='*60}\n")
            
            text = ""
            for i, page in enumerate(pdf.pages[:2]):  # First 2 pages
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    print(f"Page {i+1}: Extracted {len(page_text)} characters")
            
            print(f"\n{'='*60}")
            print(f"FIRST 1000 CHARACTERS")
            print(f"{'='*60}\n")
            print(text[:1000])
            print(f"\n{'='*60}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error reading PDF: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Default test path
        test_papers_dir = "test_papers"
        if os.path.exists(test_papers_dir):
            pdfs = [f for f in os.listdir(test_papers_dir) if f.endswith('.pdf')]
            if pdfs:
                pdf_path = os.path.join(test_papers_dir, pdfs[0])
                print(f"Using first PDF found: {pdfs[0]}\n")
            else:
                print("No PDFs found in test_papers/ folder")
                print("Please download sample papers first or provide a path:")
                print("Usage: python test_pdf_reader.py path/to/paper.pdf")
                sys.exit(1)
        else:
            print("test_papers/ folder not found")
            sys.exit(1)
    
    test_pdf_reading(pdf_path)
