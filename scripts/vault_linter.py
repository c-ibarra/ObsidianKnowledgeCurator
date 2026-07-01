#!/usr/bin/env python3
import os
import re
from pathlib import Path
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================

import argparse

PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian"))

# ==============================================================================
# LINTER LOGIC
# ==============================================================================

def run_linter(target_kb: str = "dataScienceKnowledgeBase/AI Engineer"):
    if target_kb.lower() == "all":
        target_kb_dir = VAULT_BASE
        target_kb_name = "Entire Vault"
    else:
        target_kb_dir = VAULT_BASE / target_kb
        target_kb_name = target_kb
        
    print("=" * 80)
    print(f"VAULT HEALTH CHECK & LINTER ({target_kb_name})")
    print("=" * 80)
    
    if not target_kb_dir.exists():
        print(f"Error: Directory not found {target_kb_dir}")
        return

    all_notes = {}
    all_links = set()
    link_graph = {}
    contradictions = []
    
    # 1. Build a global catalog of all notes/files in the vault for link resolution
    global_note_names = set()
    for root, dirs, files in os.walk(VAULT_BASE):
        if "dswok" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                global_note_names.add(file[:-3])
            elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.svg')):
                global_note_names.add(file)

    # 2. Gather all files in the target KB and their contents
    for root, dirs, files in os.walk(target_kb_dir):
        if "dswok" in root:
            continue
            
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                try:
                    rel_path = file_path.relative_to(target_kb_dir)
                except ValueError:
                    rel_path = file_path.relative_to(VAULT_BASE)
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

    # 3. Extract links and contradictions
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
            # Clean link (remove alias if exists [[file|alias]])
            target = link.split('|')[0].strip()
            # Remove header hash if exists [[file#header]]
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

    # 4. Analyze Health
    dead_links = []
    for target in all_links:
        # Resolve target links globally against all notes and assets in the entire vault
        if target not in all_notes and target not in global_note_names:
            dead_links.append(target)
            
    orphans = []
    for note_name, data in all_notes.items():
        if not data["incoming"] and not data["outgoing"] and "Master Plan" not in note_name:
            orphans.append(note_name)

    # 5. Report
    print(f"Total Notes Analyzed: {len(all_notes)}")
    
    print("\n[!] CONTRADICTIONS FOUND:")
    if contradictions:
        for c in contradictions:
            print(f"  - In '{c['note']}' (Line {c['line_num']}): {c['text']}")
    else:
        print("  None detected.")

    print(f"\n[!] ORPHAN NOTES ({len(orphans)}):")
    if orphans:
        for o in orphans[:10]:
            print(f"  - {o}")
        if len(orphans) > 10:
            print(f"  ... and {len(orphans)-10} more.")
    else:
        print("  None detected.")

    print(f"\n[!] DEAD LINKS ({len(dead_links)}):")
    if dead_links:
        for d in dead_links[:10]:
            sources = link_graph.get(d, [])
            print(f"  - '{d}' (referenced in: {', '.join(sources[:3])})")
        if len(dead_links) > 10:
            print(f"  ... and {len(dead_links)-10} more.")
    else:
        print("  None detected.")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vault Health Check and Linter")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root")
    args = parser.parse_args()
    run_linter(args.target_kb)
