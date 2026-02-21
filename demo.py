"""
Demo Script — Autonomous Research Assistant
Run this for the hackathon demo. Shows the full pipeline live.
"""

import os, time, subprocess, webbrowser

DEMO_PAPER = None   # Will pick first PDF from test_papers/ automatically

def banner(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print('='*70 + '\n')

def step(n, total, text):
    print(f"\n[{n}/{total}] {text}")
    print("─" * 50)

def wait(msg="Press Enter to continue..."):
    input(f"\n⏸  {msg}")

def run(cmd, desc=""):
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0

def demo():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    banner("🔬 AUTONOMOUS RESEARCH ASSISTANT — LIVE DEMO")
    print("  Platform   : Accomplish + Python + Ollama (llama3.2)")
    print("  Everything runs locally — no API keys, no cloud, no cost")
    print("  Hackathon  : Automate Me If You Can")

    wait("Ready? Press Enter to start the demo...")

    # Step 1: Show test papers
    step(1, 5, "DROP PAPERS → Auto-detect & process")
    pdfs = [f for f in os.listdir("test_papers") if f.endswith(".pdf")]
    print(f"  📥 Papers in test_papers/: {len(pdfs)} PDFs")
    for p in pdfs[:5]:
        print(f"     {p}")
    if len(pdfs) > 5:
        print(f"     ...and {len(pdfs)-5} more")

    wait()

    # Step 2: Organize
    step(2, 5, "AI ORGANIZE → Extract metadata + rename + sort")
    print("  🤖 Ollama (llama3.2) extracts:")
    print("     Title, Authors, Year, Field, Subtopic")
    print("  📁 Files renamed → Year_Title_Author_et_al.pdf")
    print("  📂 Moved to → output/Field/Subtopic/\n")
    # Show output structure
    for field in os.listdir("output"):
        fpath = os.path.join("output", field)
        if os.path.isdir(fpath) and not field.startswith("."):
            count = sum(len(os.listdir(os.path.join(fpath, s)))
                       for s in os.listdir(fpath) if os.path.isdir(os.path.join(fpath, s)))
            print(f"  output/{field}/  ({count} papers)")

    wait()

    # Step 3: Index
    step(3, 5, "MASTER INDEX → Build searchable library")
    print("  Running: python build_index.py\n")
    run("python build_index.py")

    wait()

    # Step 4: Dashboard
    step(4, 5, "DASHBOARD → Open interactive browser view")
    dashboard = os.path.abspath("output/dashboard.html")
    print(f"  Opening: {dashboard}")
    webbrowser.open(f"file://{dashboard}")
    print("\n  ✅ Dashboard open — shows papers, fields, search, charts")

    wait()

    # Step 5: Literature Review
    step(5, 5, "LITERATURE REVIEWS → AI-generated academic reviews")
    print("  ✅ Already generated: output/LITERATURE_REVIEWS.md")
    print("  Includes:")
    print("    • 3-4 sentence summary per paper")
    print("    • Subtopic literature review (narrative)")
    print("    • Field-level overview (ML / CV / NLP)")
    print("    • Cross-topic synthesis across all fields")

    banner("🏆 DEMO COMPLETE!")
    print("  GitHub: https://github.com/monishkumardvs/autonomous-research-agent")
    print("\n  Key outputs:")
    print("    📊 output/dashboard.html   — interactive dashboard")
    print("    📚 output/RESEARCH_INDEX.md — full library")
    print("    🎓 output/LITERATURE_REVIEWS.md — AI reviews")
    print("    📖 output/bibliography.bib — BibTeX export")
    print("\n  Built with Accomplish + Ollama (local AI) — 100% free, 100% private\n")

if __name__ == "__main__":
    demo()
