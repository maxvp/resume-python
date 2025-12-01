#!/usr/bin/env python3
"""
Resume Watcher - Auto-regenerate PDF when YAML changes
Usage: python watch_resume.py
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generate_resume import generate_resume

class ResumeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
    
    def on_modified(self, event):
        # Debounce: ignore rapid successive saves
        if time.time() - self.last_modified < 0.5:
            return
        
        if event.src_path.endswith('resume.yaml'):
            self.last_modified = time.time()
            print(f"\n[{time.strftime('%H:%M:%S')}] Detected change in resume.yaml")
            try:
                generate_resume()
                print("✓ PDF updated successfully")
            except Exception as e:
                print(f"✗ Error generating PDF: {e}")

if __name__ == "__main__":
    print("Resume Watcher")
    print("=" * 50)
    print("Watching resume.yaml for changes...")
    print("Press Ctrl+C to stop\n")
    
    # Generate initial version
    try:
        generate_resume()
        print()
    except Exception as e:
        print(f"Initial generation failed: {e}\n")
    
    event_handler = ResumeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    observer.join()
    print("Goodbye!")