"""
Rename Research Papers - Autonomous Research Assistant
Renames PDFs based on AI-extracted metadata using Google Gemini (FREE).
Format: Year_Title_FirstAuthor_et_al.pdf
"""

import os
import re
import json
from extract_metadata import process_pdf, configure_gemini

def clean_filename(text, max_length=50):
    """Clean text for use in filename."""
    text = re.sub(r'[^\w\s-]', '', str(text))
    text = re.sub(r'[-\s]+', '_', text)
    text = re.sub(r'_+', '_', text)
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip('_')

def generate_new_filename(metadata):
    """
    Generate new filename from metadata.
    Format: Year_Title_FirstAuthor_et_al.pdf
    """
    year = metadata.get('year', 'Unknown')
    title = metadata.get('title', 'Untitled')
    authors = metadata.get('authors', [])

    clean_title = clean_filename(title, max_length=50)

    if authors:
        first_author = authors[0]
        if ' ' in first_author:
            first_author = first_author.split()[-1]
        first_author = clean_filename(first_author, max_length=20)
    else:
        first_author = "Unknown"

    suffix = "_et_al" if len(authors) > 1 else ""
    return f"{year}_{clean_title}_{first_author}{suffix}.pdf"

def rename_paper(pdf_path, dry_run=False):
    """
    Rename a single paper based on its metadata.
    Returns: (success, new_path, metadata)
    """
    metadata = process_pdf(pdf_path)
    if not metadata:
        return False, None, None

    new_filename = generate_new_filename(metadata)
    directory = os.path.dirname(pdf_path)
    new_path = os.path.join(directory, new_filename)

    # Handle duplicate filenames
    if os.path.exists(new_path) and new_path != pdf_path:
        base, ext = os.path.splitext(new_filename)
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(directory, f"{base}_{counter}{ext}")
            counter += 1

    print(f"  📝 New name: {os.path.basename(new_path)}")

    if dry_run:
        return True, new_path, metadata

    try:
        os.rename(pdf_path, new_path)
        print(f"  ✅ Renamed!")
        return True, new_path, metadata
    except Exception as e:
        print(f"  ❌ Rename failed: {str(e)}")
        return False, None, metadata

def rename_all_papers(directory="test_papers", dry_run=False):
    """Rename all PDFs in a directory."""
    pdfs = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    if not pdfs:
        print(f"❌ No PDFs found in {directory}/")
        return None

    print(f"\n🚀 Renaming {len(pdfs)} papers...\n")
    results = {'total': len(pdfs), 'success': 0, 'failed': 0, 'files': []}

    for pdf_file in pdfs:
        pdf_path = os.path.join(directory, pdf_file)
        success, new_path, metadata = rename_paper(pdf_path, dry_run)
        if success:
            results['success'] += 1
            results['files'].append({'original': pdf_file, 'new': os.path.basename(new_path), 'metadata': metadata})
        else:
            results['failed'] += 1

    print(f"\n{'='*60}")
    print(f"✅ Renamed: {results['success']}  ❌ Failed: {results['failed']}")
    return results

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    if not configure_gemini():
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("🔍 DRY RUN - No files will be renamed\n")

    rename_all_papers(dry_run=dry_run)
