"""
Generate BibTeX Bibliography — Autonomous Research Assistant (Phase 4)
Converts master_index.json into a proper BibTeX .bib file.
"""

import json, re, os

def clean_key(text, maxlen=30):
    return re.sub(r'[^\w]', '', text)[:maxlen]

def make_bibtex_key(paper):
    parts = paper["filename"].replace(".pdf","").split("_")
    year  = parts[0] if parts and parts[0].isdigit() else "0000"
    # Try to get last author name from filename
    author_part = parts[-2] if len(parts) > 2 else parts[-1]
    if author_part.lower() in ("al", "et"):
        author_part = parts[-3] if len(parts) > 3 else "Unknown"
    short_title = parts[1] if len(parts) > 1 else "paper"
    return f"{clean_key(author_part)}{year}_{clean_key(short_title, 15)}"

def paper_to_bibtex(paper, field, subtopic):
    key        = make_bibtex_key(paper)
    fname      = paper["filename"].replace(".pdf","").replace("_"," ")
    year       = paper.get("year", "Unknown")
    abstract   = paper.get("abstract_snippet", "")[:400].replace("{","").replace("}","").replace('"',"'")
    keywords   = f"{field.replace('_',' ')}, {subtopic.replace('_',' ')}"

    return f"""@article{{{key},
  title     = {{{fname}}},
  year      = {{{year}}},
  journal   = {{arXiv preprint}},
  keywords  = {{{keywords}}},
  abstract  = {{{abstract}...}},
  note      = {{Organized by Autonomous Research Assistant}}
}}"""

def generate_bibtex(index_path="logs/master_index.json", output_path="output/bibliography.bib"):
    with open(index_path, encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    total   = 0
    lib     = data.get("library", {})

    for field, subtopics in lib.items():
        entries.append(f"\n%% ════════════════════════════════════")
        entries.append(f"%% Field: {field.replace('_',' ')}")
        entries.append(f"%% ════════════════════════════════════\n")
        for subtopic, papers in subtopics.items():
            entries.append(f"% --- {subtopic.replace('_',' ')} ---")
            for p in papers:
                entries.append(paper_to_bibtex(p, field, subtopic))
                total += 1

    header = f"""% ╔══════════════════════════════════════════════════════╗
% ║  Autonomous Research Assistant — BibTeX Bibliography  ║
% ║  Generated automatically from master_index.json       ║
% ║  Total entries: {total:<37}║
% ╚══════════════════════════════════════════════════════╝
"""
    bib_content = header + "\n".join(entries)

    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(bib_content)

    print(f"✅ BibTeX bibliography generated: {output_path}")
    print(f"   {total} entries written")
    return total

if __name__ == "__main__":
    generate_bibtex()
