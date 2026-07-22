#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from datetime import datetime

VAULT_ROOT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))

def migrate(execute=False):
    notes_to_change = []
    
    print(f"Scanning vault for curated raw notes under: {VAULT_ROOT}")
    
    for root, dirs, files in os.walk(VAULT_ROOT):
        # Exclude protected zone strictly
        if "dswok" in root or "dswok" in dirs:
            if "dswok" in dirs:
                dirs.remove("dswok")
            continue
            
        # Ensure we are inside a 'raw' directory hierarchy
        path_parts = Path(root).parts
        if "raw" not in path_parts:
            continue
            
        for file in files:
            if file.endswith(".md"):
                # Exclude master plans
                if "Master Plan" in file or "plan" in file.lower():
                    continue
                    
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8")
                    stat = file_path.stat()
                    
                    # On macOS, st_birthtime returns file creation time
                    birth_time = getattr(stat, 'st_birthtime', stat.st_mtime)
                    creation_date = datetime.fromtimestamp(birth_time).strftime("%d-%m-%Y")
                    
                    lines = content.splitlines()
                    blockquote_start = -1
                    blockquote_end = -1
                    is_spanish = False
                    already_has_processed = False
                    tags_index = -1
                    
                    # Inspect the first 15 lines for metadata blockquote
                    for i, line in enumerate(lines[:15]):
                        stripped = line.strip()
                        if stripped.startswith(">"):
                            if blockquote_start == -1:
                                blockquote_start = i
                            blockquote_end = i
                            
                            # Language detection
                            if any(k in stripped for k in ["Canal/Autor:", "Fecha:", "Tipo:", "Fuente:"]):
                                is_spanish = True
                            if "Processed:" in stripped or "Procesado:" in stripped:
                                already_has_processed = True
                            if "Tags:" in stripped or "Tag:" in stripped:
                                tags_index = i
                    
                    if blockquote_start != -1 and not already_has_processed:
                        prefix = "Procesado:" if is_spanish else "Processed:"
                        new_line = f"> {prefix} {creation_date}"
                        
                        new_lines = list(lines)
                        if tags_index != -1:
                            new_lines.insert(tags_index, new_line)
                        else:
                            new_lines.insert(blockquote_end + 1, new_line)
                            
                        notes_to_change.append({
                            "path": file_path,
                            "name": file,
                            "new_content": "\n".join(new_lines)
                        })
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    
    print(f"Total curated notes that require migration: {len(notes_to_change)}")
    
    if execute:
        print("Writing changes to files...")
        count = 0
        for note in notes_to_change:
            try:
                note["path"].write_text(note["new_content"], encoding="utf-8")
                count += 1
            except Exception as e:
                print(f"Error writing to {note['path']}: {e}")
        print(f"Successfully migrated {count} notes.")
    else:
        print("DRY-RUN mode enabled. No files were modified.")
        # Print a sample of changes
        if notes_to_change:
            print("\nSample change:")
            sample = notes_to_change[0]
            print(f"File: {sample['name']}")
            print("New header preview:")
            preview_lines = sample["new_content"].splitlines()[:15]
            for pl in preview_lines:
                if pl.strip().startswith(">"):
                    print(pl)

def main():
    parser = argparse.ArgumentParser(description="Migrate curated notes to include processing date metadata")
    parser.add_argument("--execute", action="store_true", help="Apply modifications to files in the vault")
    args = parser.parse_args()
    
    migrate(execute=args.execute)

if __name__ == "__main__":
    main()
