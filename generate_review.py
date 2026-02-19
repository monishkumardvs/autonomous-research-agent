"""
Generate Literature Reviews - Autonomous Research Assistant (Phase 3)
Uses Ollama (local, free) to generate:
  - Per-subtopic mini-reviews
  - Per-field full literature reviews
  - Cross-topic synthesis (the WOW feature)
  - output/LITERATURE_REVIEWS.md
"""

import os
import json
import pdfplumber
import requests
from datetime import datetime

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
OUTPUT_DIR   = "output"
REVIEWS_PATH = os.path.join(OUTPUT_DIR, "LITERATURE_REVIEWS.md")

# ─────────────────────────────────────────────
# OLLAMA HELPERS
# ─────────────────────────────────────────────
def ask_ollama(prompt, max_tokens=800):
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": max_tokens}
        }, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠️  Ollama error: {e}")
        return None

def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False

# ─────────────────────────────────────────────
# TEXT EXTRACTION
# ─────────────────────────────────────────────
def extract_text(pdf_path, chars=4000):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:4]:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text[:chars].strip()
    except Exception:
        return ""

# ─────────────────────────────────────────────
# REVIEW GENERATORS
# ─────────────────────────────────────────────
def generate_paper_summary(pdf_path, filename):
    """One-paragraph summary of a single paper."""
    print(f"    📖 Summarising: {filename[:55]}")
    text = extract_text(pdf_path, 3000)
    if not text:
        return "Summary unavailable (could not extract text)."

    prompt = f"""You are a research assistant. Read this excerpt from a research paper and write a concise 3-4 sentence summary.
Focus on: what problem it solves, the method used, and the key results.

Paper excerpt:
{text}

Write a clear, academic-style summary (3-4 sentences only):"""

    result = ask_ollama(prompt, 250)
    return result or "Summary unavailable."

def generate_subtopic_review(papers_info, subtopic, field):
    """Mini literature review for one subtopic."""
    print(f"\n  📝 Writing subtopic review: {subtopic}")
    summaries_text = "\n\n".join(
        f"Paper: {p['name']}\nSummary: {p['summary']}" for p in papers_info
    )

    prompt = f"""You are a research expert writing a mini literature review on "{subtopic}" in the field of {field}.

You have summaries of {len(papers_info)} papers:
{summaries_text}

Write a coherent 2-3 paragraph mini literature review that:
1. Introduces the {subtopic} area
2. Discusses the key approaches and findings from these papers
3. Highlights any trends, gaps, or open problems

Write in academic style, connecting the papers into a narrative:"""

    return ask_ollama(prompt, 500) or "Review generation failed."

def generate_field_review(subtopic_reviews, field):
    """Full field-level literature review."""
    print(f"\n  📚 Writing field review: {field}")
    combined = "\n\n---\n\n".join(
        f"### {sub}\n{review}" for sub, review in subtopic_reviews.items()
    )

    prompt = f"""You are writing a comprehensive literature review for the field: {field.replace('_',' ')}

Below are mini-reviews for each subtopic in this field:
{combined[:3000]}

Write an executive-style field overview (3-4 paragraphs) that:
1. Introduces the field and its importance
2. Synthesises the main themes across subtopics
3. Identifies the state-of-the-art and trends
4. Notes future research directions

Use academic, professional language:"""

    return ask_ollama(prompt, 600) or "Field review generation failed."

def generate_cross_topic_synthesis(field_reviews):
    """The WOW feature — synthesis across ALL fields."""
    print(f"\n🌟 Generating cross-topic synthesis...")
    combined = "\n\n".join(
        f"**{f.replace('_',' ')}**:\n{rev[:800]}" for f, rev in field_reviews.items()
    )

    prompt = f"""You are a senior research scientist producing a cross-disciplinary synthesis report.

You have reviewed papers from these fields:
{combined[:4000]}

Write a powerful 4-5 paragraph cross-topic synthesis that:
1. Identifies overarching themes cutting across ALL fields
2. Points out how different fields are converging or diverging
3. Highlights emerging interdisciplinary opportunities
4. Makes specific, actionable recommendations for future research

This should read like the introduction of a major survey paper:"""

    return ask_ollama(prompt, 800) or "Synthesis generation failed."

# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def generate_all_reviews(output_dir=OUTPUT_DIR):
    """Full Phase 3 pipeline."""
    all_data        = {}   # {field: {subtopic: {papers:[{name,summary}], review:str}}}
    field_reviews   = {}
    all_paper_count = 0

    # Walk output directory
    for field in sorted(os.listdir(output_dir)):
        field_path = os.path.join(output_dir, field)
        if not os.path.isdir(field_path) or field.startswith("."):
            continue

        print(f"\n{'='*70}")
        print(f"🔬 FIELD: {field.replace('_',' ')}")
        print(f"{'='*70}")

        all_data[field] = {}
        subtopic_reviews = {}

        for subtopic in sorted(os.listdir(field_path)):
            sub_path = os.path.join(field_path, subtopic)
            if not os.path.isdir(sub_path):
                continue

            pdfs = [f for f in os.listdir(sub_path) if f.lower().endswith(".pdf")]
            if not pdfs:
                continue

            print(f"\n  📂 {subtopic} ({len(pdfs)} papers)")

            papers_info = []
            for fname in pdfs:
                pdf_path = os.path.join(sub_path, fname)
                summary  = generate_paper_summary(pdf_path, fname)
                papers_info.append({"name": fname, "summary": summary})
                all_paper_count += 1

            sub_review = generate_subtopic_review(papers_info, subtopic.replace("_"," "), field.replace("_"," "))
            subtopic_reviews[subtopic] = sub_review
            all_data[field][subtopic]  = {"papers": papers_info, "review": sub_review}

        # Field-level review
        if subtopic_reviews:
            field_rev = generate_field_review(subtopic_reviews, field.replace("_"," "))
            field_reviews[field] = field_rev

    # Cross-topic synthesis
    synthesis = generate_cross_topic_synthesis(field_reviews) if len(field_reviews) > 1 else ""

    return all_data, field_reviews, synthesis, all_paper_count

# ─────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────
def write_reviews_markdown(all_data, field_reviews, synthesis, total):
    lines = []
    lines.append("# 🎓 Autonomous Literature Review Report\n")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"> Papers reviewed: **{total}**  |  Fields: **{len(all_data)}**\n")
    lines.append("---\n")

    # Cross-topic synthesis first (most impressive)
    if synthesis:
        lines.append("## 🌟 Cross-Topic Synthesis\n")
        lines.append(synthesis)
        lines.append("\n---\n")

    # TOC
    lines.append("## 📑 Contents\n")
    for field in sorted(all_data):
        display = field.replace("_", " ")
        count   = sum(len(all_data[field][s]["papers"]) for s in all_data[field])
        lines.append(f"- **{display}** — {count} papers")
        for sub in sorted(all_data[field]):
            lines.append(f"  - {sub.replace('_',' ')} ({len(all_data[field][sub]['papers'])} papers)")
    lines.append("\n---\n")

    # Field sections
    for field in sorted(all_data):
        display_field = field.replace("_", " ")
        total_f = sum(len(all_data[field][s]["papers"]) for s in all_data[field])
        lines.append(f"## 🔬 {display_field} ({total_f} papers)\n")

        if field in field_reviews:
            lines.append("### Field Overview\n")
            lines.append(field_reviews[field])
            lines.append("")

        for subtopic in sorted(all_data[field]):
            display_sub = subtopic.replace("_", " ")
            papers      = all_data[field][subtopic]["papers"]
            review      = all_data[field][subtopic]["review"]

            lines.append(f"### 📂 {display_sub}\n")
            lines.append(f"**Subtopic Literature Review**\n")
            lines.append(review)
            lines.append("")
            lines.append(f"**Papers in this section:**\n")
            for p in papers:
                clean = p["name"].replace(".pdf","").replace("_"," ")
                lines.append(f"- **{clean}**")
                lines.append(f"  > {p['summary']}\n")
            lines.append("---\n")

    with open(REVIEWS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n📄 Literature reviews saved → {REVIEWS_PATH}")

    # Save JSON backup
    os.makedirs("logs", exist_ok=True)
    with open("logs/reviews_data.json", "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_papers": total,
            "fields": list(all_data.keys()),
            "synthesis": synthesis,
            "data": {f: {s: {"review": all_data[f][s]["review"],
                             "papers": [p["name"] for p in all_data[f][s]["papers"]]}
                         for s in all_data[f]}
                     for f in all_data}
        }, f, indent=2)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 AUTONOMOUS LITERATURE REVIEW GENERATOR  (Phase 3)")
    print("="*70 + "\n")

    if not check_ollama():
        print("❌ Ollama not running. Start it first.")
        exit(1)
    print("✅ Ollama is running\n")

    all_data, field_reviews, synthesis, total = generate_all_reviews()

    write_reviews_markdown(all_data, field_reviews, synthesis, total)

    print("\n" + "="*70)
    print("🎉 LITERATURE REVIEW GENERATION COMPLETE!")
    print(f"   📄 Open: output/LITERATURE_REVIEWS.md")
    print(f"   📊 {total} papers reviewed across {len(all_data)} fields")
    print("="*70 + "\n")
