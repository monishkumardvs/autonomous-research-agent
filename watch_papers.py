"""
Folder Watcher — Autonomous Research Assistant (Phase 5)
Monitors test_papers/ for new PDFs and auto-processes them.
Uses watchdog library. Run in background while working.
"""

import time, os, sys, logging
from watchdog.observers import Observer
from watchdog.events    import FileSystemEventHandler

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from organize_papers import process_paper, configure_gemini, check_ollama

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt = "%H:%M:%S"
)
log = logging.getLogger("watcher")

WATCH_DIR  = "test_papers"
OUTPUT_DIR = "output"
COOLDOWN   = 3   # seconds to wait after file appears (let it finish writing)

class PDFHandler(FileSystemEventHandler):
    def __init__(self):
        self._processed = set()

    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path
        if not path.lower().endswith(".pdf"):
            return
        if path in self._processed:
            return

        log.info(f"📥 New PDF detected: {os.path.basename(path)}")
        time.sleep(COOLDOWN)   # wait for file to finish writing

        try:
            result = process_paper(path, OUTPUT_DIR)
            if result["success"]:
                log.info(f"✅ Organized → {result.get('field','?')}/{result.get('subtopic','?')}")
                log.info(f"   New name: {os.path.basename(result['final_path'])}")
                self._processed.add(path)
            else:
                log.warning(f"⚠️  Failed: {result.get('error','unknown error')}")
        except Exception as e:
            log.error(f"❌ Error processing {os.path.basename(path)}: {e}")


def main():
    if not check_ollama():
        log.error("Ollama is not running. Start Ollama first.")
        sys.exit(1)

    os.makedirs(WATCH_DIR, exist_ok=True)
    log.info("🦙 Autonomous Research Assistant — Folder Watcher")
    log.info(f"👁️  Watching: {os.path.abspath(WATCH_DIR)}")
    log.info("   Drop any PDF into test_papers/ and it will be auto-organized!")
    log.info("   Press Ctrl+C to stop.\n")

    handler  = PDFHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Stopping watcher...")
        observer.stop()
    observer.join()
    log.info("Watcher stopped.")

if __name__ == "__main__":
    main()
