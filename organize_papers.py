"""
Organize Research Papers - Autonomous Research Assistant
Full pipeline: Extract text → AI metadata → Rename → Organize into folders
Uses Ollama (local, FREE, no rate limits) with llama3.2
"""

import os
import re
import shutil
import json
import pdfplumber
import requests

# ─────────────────────────────────────────────
# OLLAMA CONFIG
# ─────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

def ask_ollama(prompt):
    """Send prompt to Ollama and return response text."""
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300}
        }, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠️  Ollama error: {e}")
        return None

def test_ollama():
    """Quick check that Ollama is running."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=10)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            print(f"✅ Ollama is running! Models: {', '.join(models)}\n")
            return True
    except Exception as e:
        pass
    print("❌ Ollama not responding. Make sure Ollama is running (open Ollama app).")
    return False

# ─────────────────────────────────────────────
# PDF TEXT EXTRACTION
# ─────────────────────────────────────────────
def extract_text(pdf_path, pages=2):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:pages]:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text.strip() or None
    except Exception as e:
        print(f"  ⚠️  PDF read error: {e}")
        return None

# ─────────────────────────────────────────────
# METADATA EXTRACTION VIA OLLAMA
# ─────────────────────────────────────────────
def extract_metadata(text):
    prompt = f"""You are a research paper metadata extractor. Read the text below and extract metadata.

TEXT FROM PAPER:
{text[:2500]}

Extract and return ONLY a JSON object with these exact fields:
{{
  "title": "the exact paper title",
  "authors": ["LastName1", "LastName2"],
  "year": 2024,
  "field": "Machine Learning",
  "subtopic": "Random Forest"
}}

Rules:
- field must be ONE of: Machine Learning, Computer Vision, Natural Language Processing, Data Science, Robotics, Other
- subtopic is the specific technique (e.g. Transformers, Object Detection, BERT, XGBoost)
- year should be a number, estimate if not found
- Return ONLY the JSON, nothing else, no explanation"""

    raw = ask_ollama(prompt)
    if not raw:
        return None

    try:
        # Find JSON in response
        start = raw.find('{')
        end   = raw.rfind('}') + 1
        if start == -1 or end == 0:
            return None
        return json.loads(raw[start:end])
    except Exception as e:
        print(f"  ⚠️  JSON parse error: {e}")
        print(f"  Raw response: {raw[:200]}")
        return None

# ─────────────────────────────────────────────
# FILENAME GENERATION
# ─────────────────────────────────────────────
def clean(text, maxlen=50):
    text = re.sub(r'[^\w\s-]', '', str(text))
    text = re.sub(r'[-\s]+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text[:maxlen]

def make_filename(meta):
    year     = meta.get('year', 'Unknown')
    title    = clean(meta.get('title', 'Untitled'), 50)
    authors  = meta.get('authors', [])
    first    = clean(authors[0].split()[-1], 20) if authors else "Unknown"
    suffix   = "_et_al" if len(authors) > 1 else ""
    return f"{year}_{title}_{first}{suffix}.pdf"

def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

# ─────────────────────────────────────────────
# PROCESS ONE PAPER
# ─────────────────────────────────────────────
def process_paper(pdf_path, output_dir="output"):
    original_name = os.path.basename(pdf_path)

    # 1. Extract text
    text = extract_text(pdf_path)
    if not text:
        return {"success": False, "file": original_name, "error": "No text extracted"}

    # 2. Get metadata from Ollama
    meta = extract_metadata(text)
    if not meta:
        return {"success": False, "file": original_name, "error": "Metadata extraction failed"}

    print(f"  📌 {meta.get('title','?')[:65]}")
    print(f"  👤 {', '.join(meta.get('authors', []))[:50]}")
    print(f"  📅 {meta.get('year','?')}  |  🏷️  {meta.get('field','?')} / {meta.get('subtopic','?')}")

    # 3. Build destination: output/Field/Subtopic/
    field    = clean(meta.get('field',    'Other'),   30)
    subtopic = clean(meta.get('subtopic', 'General'), 30)
    dest_dir = os.path.join(output_dir, field, subtopic)
    os.makedirs(dest_dir, exist_ok=True)

    # 4. New filename
    new_name  = make_filename(meta)
    dest_path = unique_path(os.path.join(dest_dir, new_name))

    # 5. Copy → remove original
    try:
        shutil.copy2(pdf_path, dest_path)
        os.remove(pdf_path)
        print(f"  📁 → {os.path.relpath(dest_path)}")
        return {
            "success": True, "file": original_name,
            "new_name": new_name, "path": dest_path,
            "field": meta['field'], "subtopic": meta['subtopic'],
            "meta": meta
        }
    except Exception as e:
        print(f"  ❌ Move error: {e}")
        return {"success": False, "file": original_name, "error": str(e)}

# ─────────────────────────────────────────────
# MAIN: ORGANIZE ALL PAPERS
# ─────────────────────────────────────────────
def organize_all(source_dir="test_papers", output_dir="output"):
    pdfs = sorted([f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')])
    if not pdfs:
        print(f"❌ No PDFs in {source_dir}/")
        return

    print(f"\n{'='*70}")
    print(f"🎯 ORGANIZING {len(pdfs)} PAPERS WITH OLLAMA ({OLLAMA_MODEL})")
    print(f"{'='*70}\n")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    results  = []
    by_field = {}

    for i, fname in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] {fname}")
        print("─" * 60)
        r = process_paper(os.path.join(source_dir, fname), output_dir)
        results.append(r)
        if r['success']:
            by_field[r['field']] = by_field.get(r['field'], 0) + 1

    # Summary
    success = sum(1 for r in results if r['success'])
    failed  = len(results) - success

    print(f"\n{'='*70}")
    print(f"📊 DONE!")
    print(f"   ✅ Organized : {success} / {len(results)} papers")
    print(f"   ❌ Failed    : {failed}")
    print(f"\n📁 Papers by Field:")
    for field, cnt in sorted(by_field.items(), key=lambda x: -x[1]):
        print(f"   {field}: {cnt} papers")
    print(f"\n📂 Check the output/ folder!")
    print(f"{'='*70}\n")

    with open('logs/organize_results.json', 'w', encoding='utf-8') as f:
        json.dump({"total": len(results), "success": success, "failed": failed,
                   "by_field": by_field, "papers": results}, f, indent=2)
    print("💾 Log → logs/organize_results.json")
    return results

# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🦙 Autonomous Research Assistant — Powered by Ollama\n")
    if not test_ollama():
        print("\n👉 Fix: Open the Ollama app or run 'ollama serve' in a terminal")
        exit(1)
    organize_all()
