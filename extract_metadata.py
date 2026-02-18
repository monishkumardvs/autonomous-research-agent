"""
Extract Metadata from Research Papers - Autonomous Research Assistant
Uses Google Gemini (FREE) to extract title, authors, year, and research field.
"""

import pdfplumber
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    """Configure Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_key_here":
        print("❌ ERROR: Please set your GEMINI_API_KEY in .env file")
        print("\nGet a FREE key at: https://aistudio.google.com/app/apikey")
        return False
    genai.configure(api_key=api_key)
    return True

def extract_first_page(pdf_path):
    """Extract text from first 2 pages of PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:2]:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text if text else None
    except Exception as e:
        print(f"  ⚠️  Error reading PDF: {str(e)}")
        return None

def extract_metadata_with_gemini(text_excerpt):
    """
    Use Gemini to extract structured metadata from paper text.
    Returns dict with title, authors, year, field, subtopic.
    """
    prompt = f"""You are analyzing a research paper. Extract the following from the text:

1. Paper Title (exact title)
2. Authors (list of names)
3. Publication Year (4-digit year, or estimate from context)
4. Research Field (ONE of: Machine Learning, Computer Vision, Natural Language Processing, Data Science, Robotics, Other)
5. Subtopic (specific technique, e.g. "Random Forest", "Object Detection", "Transformers", "BERT")

TEXT:
{text_excerpt[:3000]}

Return ONLY valid JSON, no explanation:
{{
  "title": "Paper Title Here",
  "authors": ["Author1", "Author2"],
  "year": 2024,
  "field": "Machine Learning",
  "subtopic": "Deep Learning"
}}"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Free tier model
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Remove markdown code blocks if present
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"):
            result = result.replace("```", "").strip()

        return json.loads(result)

    except Exception as e:
        print(f"  ⚠️  Gemini API error: {str(e)}")
        return None

def process_pdf(pdf_path):
    """
    Full pipeline: PDF → Text → Gemini → Metadata dict.
    """
    print(f"\n📄 Processing: {os.path.basename(pdf_path)}")

    text = extract_first_page(pdf_path)
    if not text:
        print("  ❌ Could not extract text (may be scanned image PDF)")
        return None

    print(f"  ✅ Extracted {len(text)} characters")
    print(f"  🤖 Calling Gemini...")

    metadata = extract_metadata_with_gemini(text)
    if not metadata:
        print("  ❌ Metadata extraction failed")
        return None

    print(f"  ✅ Got metadata:")
    print(f"     Title:    {metadata.get('title', 'N/A')[:60]}")
    print(f"     Authors:  {', '.join(metadata.get('authors', []))[:50]}")
    print(f"     Year:     {metadata.get('year', 'N/A')}")
    print(f"     Field:    {metadata.get('field', 'N/A')}")
    print(f"     Subtopic: {metadata.get('subtopic', 'N/A')}")

    return metadata

if __name__ == "__main__":
    import sys

    if not configure_gemini():
        sys.exit(1)

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        test_dir = "test_papers"
        pdfs = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
        if not pdfs:
            print("No PDFs found in test_papers/")
            sys.exit(1)
        pdf_path = os.path.join(test_dir, pdfs[0])
        print(f"Using: {pdfs[0]}\n")

    metadata = process_pdf(pdf_path)
    if metadata:
        print("\n" + "="*60)
        print("✅ SUCCESS! Metadata extraction working!")
        print("="*60)
        print(json.dumps(metadata, indent=2))
