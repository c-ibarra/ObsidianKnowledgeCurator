#!/usr/bin/env python3
import os
import re
import json
import argparse
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

import sys
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT, PROJECT_ROOT, TEMP_DIR

VAULT_BASE = VAULT_ROOT

def scan_contradictions(target_kb: str = "dataScienceKnowledgeBase/AI Engineer"):
    target_kb_dir = VAULT_BASE / target_kb
    print(f"Scanning for contradictions in Target KB: {target_kb}...")
    
    if not target_kb_dir.exists():
        print(f"Error: Target directory does not exist: {target_kb_dir}")
        return

    # 1. Build a global catalog of all note paths
    global_note_paths = {}
    for root, dirs, files in os.walk(VAULT_BASE):
        if any(ignored in root for ignored in ["dswok", ".git", ".obsidian", ".agents"]):
            continue
        for file in files:
            if file.endswith(".md"):
                name = file[:-3]
                global_note_paths[name] = Path(root) / file

    # 2. Find contradicting notes in the target KB
    contradictions = []
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    for root, dirs, files in os.walk(target_kb_dir):
        if any(ignored in root for ignored in ["dswok", ".git", ".obsidian", ".agents"]):
            continue
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if "[!contradiction]" in content:
                        note_name = file[:-3]
                        
                        # Find linked notes for source context
                        links = link_pattern.findall(content)
                        sources = []
                        
                        for link in links:
                            src_name = link.split('|')[0].split('#')[0].strip()
                            if src_name and src_name != note_name and src_name in global_note_paths:
                                src_path = global_note_paths[src_name]
                                try:
                                    src_content = src_path.read_text(encoding="utf-8")
                                    sources.append({
                                        "source_name": src_name,
                                        "source_content": src_content[:4000] # Limit to prevent LLM context bloat
                                    })
                                except:
                                    pass
                                    
                        contradictions.append({
                            "note_name": note_name,
                            "abs_path": str(file_path),
                            "content": content,
                            "sources": sources
                        })
                except Exception as e:
                    print(f"Error reading file {file}: {e}")

    # 3. Output results to temp/contradictions.json
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TEMP_DIR / "contradictions.json"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(contradictions, f, indent=2, ensure_ascii=False)
        print(f"Successfully generated contradictions report: {output_path} ({len(contradictions)} items found)")
    except Exception as e:
        print(f"Error writing contradictions report: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan and report vault contradictions")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root")
    args = parser.parse_args()
    scan_contradictions(args.target_kb)
