# 📖 Autonomous Research Assistant — Full Project Documentation

> **Project:** Autonomous Research Assistant MVP  
> **Hackathon:** "Automate Me If You Can"  
> **GitHub:** https://github.com/monishkumardvs/autonomous-research-agent  
> **Stack:** Python · Ollama (llama3.2, local AI) · Accomplish · pdfplumber · watchdog  

---

## 1. What We Built and Why

### The Problem
Researchers accumulate dozens of PDF papers with random filenames like `2310.04567.pdf`. Finding a specific paper, understanding what a collection covers, or writing a literature review requires hours of manual work.

### The Solution
An **AI pipeline** that takes a folder of raw PDFs and automatically:

1. Reads each PDF and uses local AI to extract metadata
2. Renames files to a clean, consistent format
3. Sorts them into a structured `Field → Subtopic` folder hierarchy
4. Builds a searchable master index
5. Writes full literature reviews — per paper, per subtopic, per field, and a cross-topic synthesis
6. Presents everything in an interactive browser dashboard
7. Watches for new papers and processes them automatically

**Everything runs locally** — no cloud API, no cost, full data privacy — using **Ollama** with the `llama3.2` model.

---

## 2. How We Accomplished It — Phase by Phase

### Phase 1: Foundation (Days 1-2)
- Set up the project folder structure
- Downloaded 16 research papers from arXiv covering ML, CV, and NLP
- Built `test_pdf_reader.py` to verify PDF text extraction works
- Built `extract_metadata.py` to call Ollama and extract structured metadata
- Built `rename_papers.py` to rename files to `Year_Title_Author_et_al.pdf`
- Built `organize_papers.py` to put it all together — extract → rename → sort
- Pushed everything to GitHub

### Phase 2: Intelligent Organization (Days 2-3)  
- Built `build_index.py` to scan the already-organized `output/` folder
- Generates `logs/master_index.json` (machine-readable) and `output/RESEARCH_INDEX.md` (human-readable)
- Added duplicate detection that flags files with similar names

### Phase 3: Literature Review Generation (Day 3)
- Built `generate_review.py` — the most complex script
- For each paper: reads first 4 pages, sends to Ollama, gets a 3-4 sentence academic summary
- For each subtopic: sends all paper summaries to Ollama, gets a 2-3 paragraph mini-review
- For each field: synthesises all subtopic reviews into a full field overview
- Cross-topic synthesis: sends all field overviews to Ollama, gets an interdisciplinary synthesis
- All output written to `output/LITERATURE_REVIEWS.md`

### Phase 4: Dashboard & Analytics (Day 4)
- Built `output/dashboard.html` — a self-contained, no-server-needed dashboard
- Built `generate_bibtex.py` — converts the master index into a `.bib` bibliography

### Phase 5: Automation (Day 5)
- Built `watch_papers.py` using the `watchdog` library
- Monitors `test_papers/` in real-time; any new PDF is auto-processed through the full pipeline

### Phase 6: Demo & Submission (Day 6)
- Built `demo.py` — interactive step-by-step demo script for the hackathon video
- Polished `README.md` with full documentation and architecture diagram
- Created `accomplish_skills/` with proper Accomplish desktop agent integration

---

## 3. Data Flow — How Information Moves Through the System

```
test_papers/
  └── 2310.04567v1.pdf       ← raw downloaded PDF
        │
        ▼
extract_metadata.py
  ├── pdfplumber reads first 4 pages
  ├── Sends text excerpt to Ollama (llama3.2)
  └── Gets back: {title, authors, year, field, subtopic, keywords}
        │
        ▼
rename_papers.py
  └── New filename: 2023_Detecting_LLM_Hallucinations_MaticKorun.pdf
        │
        ▼
organize_papers.py (main orchestrator)
  └── Moves to: output/Machine_Learning/Transformers/2023_Detecting_LLM_Hallucinations_MaticKorun.pdf
        │
        ▼
build_index.py
  ├── Scans all of output/**/*.pdf
  ├── Writes logs/master_index.json
  └── Writes output/RESEARCH_INDEX.md
        │
        ▼
generate_review.py
  ├── For each paper → 3-4 sentence AI summary
  ├── For each subtopic → 2-3 paragraph mini-review
  ├── For each field → full field overview
  ├── Cross-topic synthesis → interdisciplinary narrative
  └── Writes output/LITERATURE_REVIEWS.md
        │
        ▼
generate_bibtex.py
  └── Reads master_index.json → writes output/bibliography.bib
        │
        ▼
output/dashboard.html
  └── Reads master_index.json (or embedded fallback) → interactive UI
```

---

## 4. File-by-File Breakdown

---

### `organize_papers.py` — Main AI Pipeline

**What it does:** The master orchestrator. Takes every PDF in `test_papers/`, processes it through the full AI chain, and organizes it.

**How it works, step by step:**
1. Lists all `.pdf` files in `test_papers/`
2. For each PDF, calls `extract_metadata()` → sends first 4 pages to Ollama with a structured prompt asking for title, authors, year, research field, and subtopic
3. Cleans the returned values (caps special chars, handles missing data)
4. Constructs the new filename: `Year_Title_Author_et_al.pdf`
5. Determines the target folder: `output/[Field]/[Subtopic]/`
6. Creates the folder if it doesn't exist
7. Copies/moves the renamed PDF into the correct location
8. Logs every action to `logs/organize_log.json`

**Input:** Raw PDFs in `test_papers/`  
**Output:** Organized PDFs in `output/Field/Subtopic/` + `logs/organize_log.json`

**Example:**
```
Before: test_papers/2310.04567v1.pdf
After:  output/Machine_Learning/Transformers/2023_Detecting_LLM_Hallucinations_MaticKorun.pdf
```

---

### `extract_metadata.py` — AI Metadata Extractor

**What it does:** The brain of the system. Uses pdfplumber to read PDF text and Ollama to understand it.

**How it works:**
1. Opens the PDF with `pdfplumber`, reads up to 4 pages
2. Extracts raw text and trims to ~3000 characters
3. Sends to Ollama with a very specific prompt:
   ```
   Extract these fields from this research paper:
   - Title: ...
   - Authors: (first author surname only)
   - Year: ...
   - Field: (one of: Machine_Learning, Computer_Vision, NLP, ...)
   - Subtopic: (e.g. Transformers, Random_Forest, BERT)
   ```
4. Parses Ollama's response line by line into a Python dictionary
5. Falls back to filename-based guesses if Ollama returns incomplete data

**Input:** Path to a single PDF file  
**Output:** Python dict `{title, authors, year, field, subtopic, keywords}`

**Ollama model used:** `llama3.2` (runs at `http://localhost:11434`)

---

### `rename_papers.py` — File Renaming Logic

**What it does:** Takes the metadata dict and constructs a clean, consistent filename.

**How it works:**
1. Takes `{year, title, authors}` from `extract_metadata()`
2. Cleans the title: removes punctuation, truncates to 50 chars, replaces spaces with underscores
3. Cleans author: takes first author's surname only
4. Builds: `{year}_{clean_title}_{clean_author}_et_al.pdf`
5. Also handles edge cases: unknown year → uses `0000`, missing author → uses `Unknown`

**Input:** Metadata dict + original filename  
**Output:** New filename string like `2023_Detecting_LLM_Hallucinations_MaticKorun_et_al.pdf`

---

### `build_index.py` — Master Library Index Builder

**What it does:** Walks the entire `output/` folder and builds both a JSON index and a Markdown library page.

**How it works:**
1. Recursively lists all PDFs inside `output/Field/Subtopic/`
2. For each PDF: reads first 2 pages and extracts the abstract section
3. Stores: filename, path, year (from filename), size, abstract snippet (600 chars)
4. Runs duplicate detection: flags files with identical first-40-chars of name
5. Writes `logs/master_index.json` with full structure
6. Writes `output/RESEARCH_INDEX.md` with formatted Markdown (headings, links, abstracts)

**Input:** Everything in `output/`  
**Output:**
- `logs/master_index.json` — machine-readable, used by dashboard and BibTeX generator
- `output/RESEARCH_INDEX.md` — human-readable library page with abstracts

---

### `generate_review.py` — AI Literature Review Generator

**What it does:** The most sophisticated script. Uses Ollama to write academic literature reviews at 4 levels of depth.

**How it works (4-level hierarchy):**

**Level 1 — Per-paper summary**
- Reads each PDF (first 3000 chars)
- Prompt: *"Write a 3-4 sentence academic summary focusing on: problem, method, results"*
- Output: short summary stored in memory

**Level 2 — Subtopic mini-review**
- Collects all paper summaries for one subtopic (e.g., all Transformers papers)
- Prompt: *"Write a 2-3 paragraph literature review for [subtopic] connecting these papers into a narrative"*
- Output: coherent narrative about the subtopic

**Level 3 — Field overview**
- Collects all subtopic reviews for one field (e.g., Machine Learning)
- Prompt: *"Write a 3-4 paragraph executive overview synthesising all subtopics"*
- Output: full field literature review

**Level 4 — Cross-topic synthesis** (the WOW feature)
- Sends all 3 field overviews together
- Prompt: *"Write a cross-disciplinary synthesis identifying overarching themes, convergences, and future directions"*
- Output: reads like the introduction of a major survey paper

**Input:** All PDFs in `output/`  
**Output:**
- `output/LITERATURE_REVIEWS.md` — full report with all 4 levels
- `logs/reviews_data.json` — JSON backup of all generated content

---

### `generate_bibtex.py` — BibTeX Bibliography Generator

**What it does:** Converts the master index into a `.bib` file for academic writing tools like LaTeX or Zotero.

**How it works:**
1. Reads `logs/master_index.json`
2. For each paper: constructs a unique BibTeX citation key (`Author2023_ShortTitle`)
3. Fills in `@article{}` entry with: title, year, journal (arXiv), keywords (field+subtopic), abstract snippet
4. Groups entries by field with comment headers
5. Writes `output/bibliography.bib`

**Input:** `logs/master_index.json`  
**Output:** `output/bibliography.bib` (16 entries, ready for LaTeX/Zotero)

---

### `output/dashboard.html` — Interactive Browser Dashboard

**What it does:** A fully self-contained HTML/JS web app that visualizes the entire research library. Open it in any browser — no server, no internet needed.

**How it works:**
1. On load: fetches `../logs/master_index.json` via JavaScript
2. If fetch fails (e.g., opened directly from file system): falls back to embedded demo data
3. Computes a **priority score** for each paper: `score = (year-2000)×0.5 + size_score + text_depth_score`. High-priority papers get 🔥 or ⭐ icons.
4. Renders three panels:
   - **Stats row**: total papers, fields, subtopics, library size, latest year
   - **Sidebar**: field filter buttons + bar charts by field and year
   - **Paper grid**: card for each paper with title, year, abstract preview, field/subtopic tags

**Interactive features:**
- 🔍 Full-text search across titles and abstracts
- 🔽 Filter by field (dropdown or sidebar buttons)
- ↕️ Sort by newest, oldest, title A-Z, or priority score
- Click any paper card → modal with full abstract and metadata

**Input:** `logs/master_index.json` (or embedded fallback)  
**Output:** Visual dashboard in browser

---

### `watch_papers.py` — Automatic Folder Monitor

**What it does:** Runs in the background and processes any new PDF you drop into `test_papers/` automatically.

**How it works:**
1. Uses the `watchdog` Python library to set up a filesystem event listener
2. Watches `test_papers/` for `on_created` events
3. When a new `.pdf` appears: waits 3 seconds (lets file finish writing), then calls `process_paper()`
4. `process_paper()` is the same function used in `organize_papers.py` — full AI chain
5. Logs success/failure with timestamps to the console
6. Keeps a `_processed` set to avoid double-processing the same file

**Input:** Any PDF dropped into `test_papers/`  
**Output:** PDF automatically renamed and moved to `output/Field/Subtopic/`

**To run:**
```bash
python watch_papers.py
# Runs until you press Ctrl+C
```

---

### `test_pdf_reader.py` — PDF Extraction Tester

**What it does:** A simple diagnostic script to verify that pdfplumber can read your PDFs correctly before running the full pipeline.

**How it works:**
1. Picks the first PDF from `test_papers/`
2. Opens it with pdfplumber and extracts text from pages 1-3
3. Prints the raw text and character count
4. Shows a pass/fail result

**Input:** First PDF in `test_papers/`  
**Output:** Console printout of extracted text

---

### `demo.py` — Hackathon Demo Script

**What it does:** An interactive 5-step guided demonstration of the entire system for the hackathon presentation video.

**How it works:**
- Step 1: Shows you what PDFs are in `test_papers/`
- Step 2: Displays the organized output folder structure
- Step 3: Runs `build_index.py` live
- Step 4: Opens `output/dashboard.html` in your default browser
- Step 5: Shows summary of generated literature reviews
- Each step pauses for `Enter` so you can narrate while screen-recording

**To use for video:**
```bash
# Start screen recording, then:
python demo.py
# Follow the prompts while narrating
```

---

### `accomplish_skills/research_assistant_skill.py` — Accomplish Skill Descriptor

**What it does:** Documents how the Accomplish desktop agent should understand this project. This file acts as the "vocabulary" for the Accomplish AI.

**How it works:** Accomplish reads skill files to know what a project can do. This file defines:
- What natural language commands this skill understands
- What Python script each command maps to
- A plain-English description of every feature

**Sample commands** the Accomplish app understands when this skill is loaded:
```
"Organize the papers in test_papers folder"  →  python organize_papers.py
"Build the research index"                   →  python build_index.py
"Generate literature reviews"                →  python generate_review.py
"Open the research dashboard"                →  opens dashboard.html in browser
"Run the full pipeline"                      →  runs all scripts in sequence
```

---

### `accomplish_skills/runner.py` — Accomplish Command Runner

**What it does:** The actual execution bridge between the Accomplish agent and the Python scripts.

**How it works:**
1. Defines a `COMMANDS` dict mapping skill names to shell commands
2. The `run_skill(command)` function is called by Accomplish when a user types a command
3. Uses `subprocess.run()` to execute the correct Python script in the project directory
4. Returns success/failure message and last 500 chars of output back to Accomplish
5. Special case for `"dashboard"` → uses `webbrowser.open()` instead of subprocess
6. Special case for `"all"` → chains all steps in sequence

**Input:** Command string from Accomplish agent  
**Output:** Result message shown to user in Accomplish app

---

## 5. Output Files — What Gets Produced

After running the full pipeline, here's everything that exists:

```
output/
├── dashboard.html               ← Open this in browser! Interactive UI
├── RESEARCH_INDEX.md            ← Full library with abstracts (Markdown)
├── LITERATURE_REVIEWS.md        ← AI-generated academic reviews
├── bibliography.bib             ← BibTeX file (16 entries)
│
├── Machine_Learning/
│   ├── Autoencoder/
│   │   └── 2026_Deep_Learning_for_Point_Spread_Function_Modeling_...pdf
│   ├── Random_Forest/
│   │   ├── 2001_Random_Forests_as_Statistical_Procedures_...pdf
│   │   ├── 2023_Human_Centered_Explainable_AI_...pdf
│   │   ├── 2024_Deciphering_Majorana_Zero_Modes_...pdf
│   │   ├── 2026_Mimicking_the_large_scale_structure_...pdf
│   │   └── 2026_Travel_Time_Prediction_from_Sparse_Open_Data_...pdf
│   ├── Randomforest/
│   │   └── 2025_A_new_mixture_model_for_spatiotemporal_...pdf
│   ├── Transformers/
│   │   ├── 2022_Bridging_Day_and_Night_Target_Class_Hallucination_...pdf
│   │   ├── 2023_Detecting_LLM_Hallucinations_via_Embedding_...pdf
│   │   ├── 2023_ToaSt_Token_Channel_Selection_...pdf
│   │   └── 2025_Ground_TruthDepth_in_Vision_Language_Models_...pdf
│   └── XGBoost/
│       └── 2024_Estimating_Human_Muscular_Fatigue_...pdf
│
├── Computer_Vision/
│   └── Transformers/
│       └── 2023_DEEPRED_AN_ARCHITECTURE_FOR_REDSHIFT_ESTIMATION_...pdf
│
└── Natural_Language_Processing/
    ├── BERT/
    │   └── 2023_Named_Entity_Recognition_for_Payment_Data_...pdf
    └── Transformers/
        ├── 2023_CGRA_DeBERTa_Concept_Guided_Residual_Augmentation_...pdf
        └── 2026_Avey_B_Acharya_et_al.pdf

logs/
├── master_index.json            ← Machine-readable library (16 papers)
└── reviews_data.json            ← AI review content backup
```

**Total: 16 papers organized across 3 fields, 8 subtopics**

---

## 6. How Each Component Connects

```
                    ┌─────────────────────────────┐
                    │  Accomplish Desktop Agent    │
                    │  (natural language commands) │
                    └──────────┬──────────────────┘
                               │ calls
                    ┌──────────▼──────────────────┐
                    │  accomplish_skills/runner.py │
                    └──────────┬──────────────────┘
                               │ calls via subprocess
        ┌──────────────────────┼──────────────────────────┐
        │                      │                          │
┌───────▼──────┐    ┌──────────▼────────┐    ┌──────────▼──────────┐
│organize_     │    │build_index.py     │    │generate_review.py   │
│papers.py     │    │                   │    │                     │
│(main pipeline│    │scan output/ →     │    │summarize papers →   │
│extract+rename│    │master_index.json  │    │subtopic reviews →   │
│+organize)    │    │RESEARCH_INDEX.md  │    │field overviews →    │
└──────┬───────┘    └──────────┬────────┘    │cross-topic synth    │
       │                       │              └──────────┬──────────┘
       │            ┌──────────▼────────┐               │
       │            │generate_bibtex.py │               │
       │            │bibliography.bib   │               │
       │            └───────────────────┘               │
       │                                                 │
       ▼                                                 ▼
 output/Field/Subtopic/*.pdf              output/LITERATURE_REVIEWS.md
       │
       ▼
 output/dashboard.html
 (reads master_index.json → shows interactive UI)

 [Background process]
 watch_papers.py → monitors test_papers/ → auto-calls organize_papers.py
```

---

## 7. How to Run Everything (Quick Reference)

```bash
# Prerequisites
pip install pdfplumber requests watchdog python-dotenv
ollama pull llama3.2   # download the free local AI model
ollama serve           # start Ollama (or open the Ollama app)

# Step 1: Put PDFs in test_papers/, then organize
python organize_papers.py

# Step 2: Build the index
python build_index.py

# Step 3: Generate literature reviews (takes ~15-30 min for 16 papers)
python generate_review.py

# Step 4: Generate BibTeX
python generate_bibtex.py

# Step 5: Open dashboard
# Double-click: output/dashboard.html

# Run background auto-watcher
python watch_papers.py

# Run demo (for video recording)
python demo.py
```

---

## 8. Key Design Decisions

| Decision | Reason |
|----------|--------|
| **Ollama instead of OpenAI API** | Free, local, no rate limits, works offline, no data privacy concerns |
| **llama3.2 model** | Best balance of speed and quality for metadata extraction and text generation on local hardware |
| **pdfplumber over PyPDF2** | Better text extraction quality, especially for academic PDFs with complex layouts |
| **Standalone HTML dashboard** | No server needed — works by double-clicking the file; embedded fallback data means it works even without `master_index.json` |
| **4-level review hierarchy** | Mirrors how human researchers write reviews — individual → sub-area → field → cross-disciplinary |
| **watchdog for file monitoring** | Production-grade Python library, cross-platform, uses OS-level file events (not polling) |
| **Accomplish integration** | Required by hackathon rules; the `accomplish_skills/` folder bridges natural language → Python |
