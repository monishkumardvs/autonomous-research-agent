"""
Build Master Index - Autonomous Research Assistant (Phase 2)
Scans the organized output/ folder and builds:
  - logs/master_index.json  : machine-readable index
  - output/RESEARCH_INDEX.md : beautiful human-readable library index
"""

import os
import json
import pdfplumber
from datetime import datetime

OUTPUT_DIR = "output"
INDEX_JSON = "logs/master_index.json"
INDEX_MD   = os.path.join(OUTPUT_DIR, "RESEARCH_INDEX.md")

# ─────────────────────────────────────────────
def extract_abstract(pdf_path, chars=1200):
    """Pull first ~1200 chars from PDF as abstract snippet."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:2]:
                t = page.extract_text()
                if t:
                    text += t + " "
            # Try to isolate abstract section
            lower = text.lower()
            start = lower.find("abstract")
            if start != -1:
                snippet = text[start:start + chars].strip()
            else:
                snippet = text[:chars].strip()
            return " ".join(snippet.split())   # normalise whitespace
    except Exception:
        return "Abstract not available."

# ─────────────────────────────────────────────
def scan_library(output_dir=OUTPUT_DIR):
    """Walk output/ and collect all PDF metadata."""
    library = {}   # {field: {subtopic: [paper_info, ...]}}

    for field in sorted(os.listdir(output_dir)):
        field_path = os.path.join(output_dir, field)
        if not os.path.isdir(field_path) or field.startswith("."):
            continue

        library[field] = {}

        for subtopic in sorted(os.listdir(field_path)):
            sub_path = os.path.join(field_path, subtopic)
            if not os.path.isdir(sub_path):
                continue

            papers = []
            for fname in sorted(os.listdir(sub_path)):
                if not fname.lower().endswith(".pdf"):
                    continue
                pdf_path = os.path.join(sub_path, fname)
                size_kb  = round(os.path.getsize(pdf_path) / 1024, 1)

                # Parse filename: Year_Title_Author_et_al.pdf
                parts = fname.replace(".pdf", "").split("_")
                year  = parts[0] if parts and parts[0].isdigit() else "Unknown"

                print(f"  📄 Indexing: {fname}")
                abstract = extract_abstract(pdf_path)

                papers.append({
                    "filename": fname,
                    "path":     os.path.relpath(pdf_path),
                    "year":     year,
                    "size_kb":  size_kb,
                    "abstract_snippet": abstract[:600]
                })

            if papers:
                library[field][subtopic] = papers

    return library

# ─────────────────────────────────────────────
def write_json_index(library):
    os.makedirs("logs", exist_ok=True)
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_papers": sum(len(ps) for f in library.values() for ps in f.values()),
        "total_fields": len(library),
        "library": library
    }
    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"\n💾 JSON index saved → {INDEX_JSON}")
    return index

# ─────────────────────────────────────────────
def write_markdown_index(library, total):
    lines = []
    lines.append("# 📚 Research Library Index\n")
    lines.append(f"> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"> **{total} papers** across **{len(library)} fields**\n")
    lines.append("---\n")

    # TOC
    lines.append("## 📑 Table of Contents\n")
    for field in sorted(library):
        anchor = field.lower().replace(" ", "-").replace("_", "-")
        count  = sum(len(ps) for ps in library[field].values())
        lines.append(f"- [{field.replace('_',' ')}](#{anchor}) ({count} papers)")
    lines.append("\n---\n")

    # Per-field sections
    for field in sorted(library):
        display_field = field.replace("_", " ")
        lines.append(f"## 🔬 {display_field}\n")

        for subtopic in sorted(library[field]):
            papers = library[field][subtopic]
            display_sub = subtopic.replace("_", " ")
            lines.append(f"### 📂 {display_sub} ({len(papers)} papers)\n")

            for p in papers:
                lines.append(f"#### 📄 {p['filename'].replace('.pdf','').replace('_',' ')}")
                lines.append(f"> **Year:** {p['year']} | **Size:** {p['size_kb']} KB")
                lines.append(f"\n> {p['abstract_snippet'][:400]}...\n")
                lines.append(f"[📥 Open paper]({p['path']})\n")
                lines.append("---")
        lines.append("")

    with open(INDEX_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📄 Markdown index saved → {INDEX_MD}")

# ─────────────────────────────────────────────
def find_duplicates(library):
    """Flag papers with very similar filenames (potential duplicates)."""
    seen  = {}
    dupes = []
    for field, subtopics in library.items():
        for subtopic, papers in subtopics.items():
            for p in papers:
                key = p["filename"][:40].lower()
                if key in seen:
                    dupes.append((seen[key], p["path"]))
                else:
                    seen[key] = p["path"]
    return dupes

# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*70)
    print("📚 BUILDING MASTER RESEARCH INDEX")
    print("="*70 + "\n")

    library = scan_library()
    total   = sum(len(ps) for f in library.values() for ps in f.values())

    print(f"\n✅ Found {total} papers in {len(library)} fields")

    # Check for duplicates
    dupes = find_duplicates(library)
    if dupes:
        print(f"\n⚠️  Potential duplicates found: {len(dupes)}")
        for a, b in dupes:
            print(f"   {a}  ↔  {b}")
    else:
        print("✅ No duplicates detected")

    write_json_index(library)
    write_markdown_index(library, total)

    print("\n" + "="*70)
    print("🎉 Master index built successfully!")
    print(f"   Open output/RESEARCH_INDEX.md for your full library view")
    print("="*70 + "\n")
