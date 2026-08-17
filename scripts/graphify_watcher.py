#!/usr/bin/env python3
import os
import sys
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the parent directory of this script to the Python path
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR / "scripts"))

from src.config import VAULT_ROOT, PROJECT_ROOT
from graphify_helper import update_note_in_graph, remove_note_from_graph
from vault_db import get_vault_db_connection, upsert_file_in_db, delete_file_from_db

VAULT_BASE = VAULT_ROOT

# Ignored vault directory names
IGNORED_DIR_NAMES = {".git", ".obsidian", ".agents"}

class VaultWatchEventHandler(FileSystemEventHandler):
    def __init__(self, debounce_interval=0.3, check_interval=0.1):
        super().__init__()
        self.debounce_interval = debounce_interval
        self.check_interval = check_interval
        self.pending_updates = set()
        self.pending_deletions = set()
        self.last_event_time = 0
        self.lock = threading.Lock()
        self.is_running = True
        
        # Start background consumer thread
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _should_ignore(self, path_str: str) -> bool:
        """Check if path should be ignored (not markdown or inside ignored directories)."""
        path = Path(path_str)
        if path.suffix.lower() != ".md":
            return True
        # Check if any parent parts are ignored
        parts = path.parts
        if any(part in IGNORED_DIR_NAMES for part in parts):
            return True
        return False

    def on_created(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        with self.lock:
            path = Path(event.src_path)
            self.pending_updates.add(path)
            self.pending_deletions.discard(path)
            self.last_event_time = time.time()
            print(f"[Watcher] File created: {path.name}")

    def on_modified(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        with self.lock:
            path = Path(event.src_path)
            self.pending_updates.add(path)
            self.pending_deletions.discard(path)
            self.last_event_time = time.time()
            print(f"[Watcher] File modified: {path.name}")

    def on_deleted(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        with self.lock:
            path = Path(event.src_path)
            self.pending_deletions.add(path)
            self.pending_updates.discard(path)
            self.last_event_time = time.time()
            print(f"[Watcher] File deleted: {path.name}")

    def on_moved(self, event):
        if event.is_directory:
            return
        # Handle src_path deletion if it wasn't ignored
        if not self._should_ignore(event.src_path):
            with self.lock:
                path = Path(event.src_path)
                self.pending_deletions.add(path)
                self.pending_updates.discard(path)
                self.last_event_time = time.time()
                print(f"[Watcher] File moved from: {path.name}")
        # Handle dest_path update if it is not ignored
        if not self._should_ignore(event.dest_path):
            with self.lock:
                path = Path(event.dest_path)
                self.pending_updates.add(path)
                self.pending_deletions.discard(path)
                self.last_event_time = time.time()
                print(f"[Watcher] File moved to: {path.name}")

    def _process_queue(self):
        while self.is_running:
            time.sleep(self.check_interval)
            
            updates = set()
            deletions = set()
            
            with self.lock:
                if not self.pending_updates and not self.pending_deletions:
                    continue
                
                # Check if debounce interval has elapsed
                if time.time() - self.last_event_time < self.debounce_interval:
                    continue
                
                # Take snapshots of current queue
                updates = self.pending_updates.copy()
                deletions = self.pending_deletions.copy()
                self.pending_updates.clear()
                self.pending_deletions.clear()

            # Execute actions outside lock to prevent locking up file events
            if deletions:
                try:
                    conn = get_vault_db_connection()
                    for file_path in deletions:
                        try:
                            print(f"[Watcher] Incrementally removing from graph: {file_path.name}")
                            remove_note_from_graph(file_path)
                            delete_file_from_db(file_path, VAULT_BASE, conn)
                        except Exception as e:
                            print(f"[Watcher] Error removing {file_path.name}: {e}")
                    conn.close()
                except Exception as db_err:
                    print(f"[Watcher] SQLite connection error during deletion: {db_err}")
                        
            if updates:
                try:
                    conn = get_vault_db_connection()
                    for file_path in updates:
                        try:
                            if file_path.exists():
                                print(f"[Watcher] Incrementally updating graph for: {file_path.name}")
                                update_note_in_graph(file_path)
                                upsert_file_in_db(file_path, VAULT_BASE, conn)
                            else:
                                print(f"[Watcher] Warning: File vanished before update: {file_path.name}")
                        except Exception as e:
                            print(f"[Watcher] Error updating {file_path.name}: {e}")
                    conn.close()
                except Exception as db_err:
                    print(f"[Watcher] SQLite connection error during update: {db_err}")

    def stop(self):
        self.is_running = False

def main():
    if not VAULT_BASE.exists():
        print(f"Error: Obsidian vault path does not exist: {VAULT_BASE}")
        sys.exit(1)
        
    print("================================================================================")
    print("GRAPHIFY VAULT WATCHER DAEMON")
    print("================================================================================")
    print(f"Watching Vault Root: {VAULT_BASE}")
    print("Updates will be applied incrementally after 300ms of inactivity.")
    print("Press Ctrl+C to stop.")
    print("================================================================================")

    event_handler = VaultWatchEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(VAULT_BASE), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping vault watcher...")
        event_handler.stop()
        observer.stop()
    observer.join()
    print("Watcher daemon stopped successfully.")

if __name__ == "__main__":
    main()
