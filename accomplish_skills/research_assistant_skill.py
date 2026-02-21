"""
Accomplish Skill: Organize Research Papers
==========================================
This skill tells the Accomplish AI desktop agent how to use this project.
Place this in the Accomplish skills panel to automate the entire pipeline.

HOW TO USE IN ACCOMPLISH:
1. Open the Accomplish desktop app
2. Add this project folder as a skill
3. Type natural language commands like those below
"""

SKILL_DESCRIPTION = """
# Autonomous Research Assistant Skill

## What I Can Do
- Organize PDF research papers into Field/Subtopic folders automatically
- Extract metadata (title, authors, year, field) from any PDF using AI
- Generate literature reviews for an entire collection of papers
- Build a master index of all your papers
- Generate BibTeX bibliography for academic use
- Open an interactive dashboard in your browser

## Natural Language Commands (use in Accomplish)

"Organize the papers in test_papers folder"
→ Runs: python organize_papers.py

"Build the research index"
→ Runs: python build_index.py

"Generate literature reviews"
→ Runs: python generate_review.py

"Generate BibTeX bibliography"
→ Runs: python generate_bibtex.py

"Open the research dashboard"
→ Opens: output/dashboard.html in browser

"Start watching for new papers"
→ Runs: python watch_papers.py

"Run the full pipeline"
→ Runs all steps in sequence

## Project Files
- organize_papers.py  — Main AI organizer
- build_index.py      — Master index builder
- generate_review.py  — Literature review generator
- generate_bibtex.py  — BibTeX exporter
- watch_papers.py     — Auto-watcher for new PDFs
- output/dashboard.html — Interactive browser dashboard
"""
