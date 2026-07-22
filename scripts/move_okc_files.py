#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))
SOURCE_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Portfolio ideas"
DEST_DIR = SOURCE_DIR / "ObsidianKnowledgeCurator"

FILES_TO_MOVE = [
    "ObsidianKnowledgeCurator - Comparative Analysis — Hyper-Extract vs ObsidianKnowledgeCurator.md",
    "ObsidianKnowledgeCurator - Comparative Analysis — OpenKB vs ObsidianKnowledgeCurator.md",
    "ObsidianKnowledgeCurator - Comparative Analysis — Wiki LLM vs ObsidianKnowledgeCurator.md"
]

def main():
    print(f"Target destination folder: {DEST_DIR}")
    
    # Create destination directory if it doesn't exist
    if not DEST_DIR.exists():
        print(f"Creating directory: {DEST_DIR}")
        DEST_DIR.mkdir(parents=True, exist_ok=True)
        
    moved_count = 0
    for filename in FILES_TO_MOVE:
        src_path = SOURCE_DIR / filename
        dest_path = DEST_DIR / filename
        
        if src_path.exists():
            print(f"Moving: {filename} -> ObsidianKnowledgeCurator/")
            try:
                shutil.move(str(src_path), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            if dest_path.exists():
                print(f"File already at destination: {filename}")
                moved_count += 1
            else:
                print(f"Warning: File not found: {src_path}")
                
    print(f"Relocation completed: {moved_count} of {len(FILES_TO_MOVE)} files processed.")

if __name__ == "__main__":
    main()
