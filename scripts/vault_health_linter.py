#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path

import sys
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT

VAULT_BASE = VAULT_ROOT
DEFAULT_KB_DIR = VAULT_BASE / "dataScienceKnowledgeBase"

def run_linter(target_dir_name: str):
    target_dir = DEFAULT_KB_DIR / target_dir_name
    
    print("=" * 80)
    print(f"VAULT HEALTH CHECK & LINTER: {target_dir_name}")
    print("=" * 80)
    
    if not target_dir.exists():
        print(f"Error: Directory not found at {target_dir}")
        return
        
    all_notes = {}
    all_links = set()
    link_graph = {}
    contradictions = []
    
    # 1. Gather all files and their contents recursively
    for root, dirs, files in os.walk(target_dir):
        # Ignore protected directories
        if "dswok" in root or "dswok" in dirs:
            if "dswok" in dirs:
                dirs.remove("dswok")
            continue
            
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(target_dir)
                file_name_no_ext = file[:-3]
                
                try:
                    content = file_path.read_text(encoding="utf-8")
                except Exception as e:
                    print(f"Could not read {file}: {e}")
                    continue
                    
                all_notes[file_name_no_ext] = {
                    "path": rel_path,
                    "content": content,
                    "incoming": [],
                    "outgoing": []
                }

    # 2. Extract links and contradictions
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    for note_name, data in all_notes.items():
        content = data["content"]
        
        # Check for contradictions
        for line_num, line in enumerate(content.splitlines(), 1):
            if "[!contradiction]" in line:
                contradictions.append({
                    "note": note_name,
                    "line_num": line_num,
                    "text": line.strip()
                })
                
        # Extract wikilinks
        links = link_pattern.findall(content)
        for link in links:
            # Clean link (remove alias [[file|alias]])
            target = link.split('|')[0].strip()
            # Remove header hash [[file#header]]
            target = target.split('#')[0].strip()
            
            if not target:
                continue
                
            data["outgoing"].append(target)
            all_links.add(target)
            
            if target in link_graph:
                link_graph[target].append(note_name)
            else:
                link_graph[target] = [note_name]

    # Map incoming links
    for target, sources in link_graph.items():
        if target in all_notes:
            all_notes[target]["incoming"].extend(sources)

    # 3. Analyze Health
    dead_links = []
    for target in all_links:
        # Check if target exists in our notes dictionary
        if target not in all_notes:
            # Sometimes a link points to a note in another category (e.g. cross-KB link),
            # let's verify if the file exists globally in dataScienceKnowledgeBase/
            # by checking if a file <target>.md exists under VAULT_BASE recursively.
            # This is a very smart check to avoid false positives!
            global_found = False
            # Quick check: does <target>.md exist globally?
            for root, _, files in os.walk(DEFAULT_KB_DIR):
                if f"{target}.md" in files:
                    global_found = True
                    break
            if not global_found:
                dead_links.append(target)
            
    orphans = []
    for note_name, data in all_notes.items():
        # A note is an orphan if it has 0 incoming links and 0 outgoing links (excluding Master Plans)
        if not data["incoming"] and not data["outgoing"] and "Master Plan" not in note_name and "plan" not in note_name.lower():
            orphans.append(note_name)

    # 4. Report
    print(f"Total Notes Analyzed: {len(all_notes)}")
    
    print("\n[!] CONTRADICTIONS FOUND:")
    if contradictions:
        for c in contradictions:
            print(f"  - In '{c['note']}' (Line {c['line_num']}): {c['text']}")
    else:
        print("  None detected.")

    print(f"\n[!] ORPHAN NOTES ({len(orphans)}):")
    if orphans:
        for o in orphans[:15]:
            print(f"  - [[{o}]]")
        if len(orphans) > 15:
            print(f"  ... and {len(orphans)-15} more.")
    else:
        print("  None detected.")

    print(f"\n[!] DEAD LINKS ({len(dead_links)}):")
    if dead_links:
        for d in dead_links[:15]:
            sources = link_graph.get(d, [])
            print(f"  - '{d}' (referenced in: {', '.join(f'[[{s}]]' for s in sources[:3])})")
        if len(dead_links) > 15:
            print(f"  ... and {len(dead_links)-15} more.")
    else:
        print("  None detected.")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic Obsidian KB Vault Health Linter.")
    parser.add_argument("--dir", default="Machine Learning", help="Directory name under dataScienceKnowledgeBase/ to audit.")
    args = parser.parse_args()
    
    run_linter(args.dir)
