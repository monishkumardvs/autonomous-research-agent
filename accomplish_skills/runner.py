"""
Accomplish Integration — Run any Research Assistant command
Used by the Accomplish desktop agent to execute the pipeline.
"""

import subprocess, sys, os, webbrowser

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR  = os.path.dirname(PROJECT_DIR)

COMMANDS = {
    "organize":   ["python", os.path.join(PARENT_DIR, "organize_papers.py")],
    "index":      ["python", os.path.join(PARENT_DIR, "build_index.py")],
    "review":     ["python", os.path.join(PARENT_DIR, "generate_review.py")],
    "bibtex":     ["python", os.path.join(PARENT_DIR, "generate_bibtex.py")],
    "watch":      ["python", os.path.join(PARENT_DIR, "watch_papers.py")],
    "dashboard":  None,  # opens browser
    "all":        ["organize", "index", "review", "bibtex"],
}

def run_skill(command: str):
    """
    Called by Accomplish when user types a command.
    command: one of 'organize', 'index', 'review', 'bibtex', 'watch', 'dashboard', 'all'
    """
    command = command.strip().lower()

    if command == "dashboard":
        dashboard_path = os.path.join(PARENT_DIR, "output", "dashboard.html")
        webbrowser.open(f"file://{dashboard_path}")
        return "✅ Dashboard opened in browser"

    if command == "all":
        results = []
        for step in ["organize", "index", "review", "bibtex"]:
            result = run_skill(step)
            results.append(result)
        return "\n".join(results)

    cmd = COMMANDS.get(command)
    if not cmd:
        return f"❌ Unknown command: {command}. Use: {', '.join(COMMANDS.keys())}"

    try:
        result = subprocess.run(cmd, cwd=PARENT_DIR, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            return f"✅ {command} completed successfully\n{result.stdout[-500:]}"
        else:
            return f"❌ {command} failed:\n{result.stderr[-300:]}"
    except subprocess.TimeoutExpired:
        return f"⏳ {command} timed out (>10 min)"
    except Exception as e:
        return f"❌ Error: {e}"


if __name__ == "__main__":
    # Allow running from command line: python runner.py organize
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(run_skill(cmd))
