#!/usr/bin/env python3
import os
import re
from pathlib import Path

import argparse

VAULT_ROOT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian"))

def get_master_plan_title(target_kb: str) -> str:
    kb_name = target_kb.split("/")[-1]
    mappings = {
        "AI Engineer": "AI Engineering",
        "software engineer": "Software Engineering",
        "Machine Learning": "Machine Learning",
        "machine learning": "Machine Learning"
    }
    return mappings.get(kb_name, kb_name.title())

def clean_creator(creator_raw: str) -> str:
    # Remove markdown link formatting e.g. [@channel](url) -> @channel
    creator = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', creator_raw)
    # Remove leading '@' if present, or keep it clean
    creator = creator.replace("**", "").replace("__", "").strip()
    # If it contains an ' — ' split, take the second part (e.g. [@id] — Real Name)
    if " — " in creator:
        creator = creator.split(" — ")[-1].strip()
    return creator

def parse_curated_note(file_path: Path, vault_base_dir: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # Exclude Master Plans and outline files
    if "Master Plan" in file_path.name or "plan" in file_path.name.lower():
        return None

    # Simple checks for a curated note: has title H1 and blockquote
    lines = content.splitlines()
    title = None
    blockquote_lines = []
    in_blockquote = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        elif stripped.startswith(">"):
            in_blockquote = True
            # Extract content after '>'
            blockquote_line = stripped[1:].strip()
            blockquote_lines.append(blockquote_line)
        elif in_blockquote and not stripped.startswith(">") and stripped != "":
            # End of blockquote
            break

    if not title or not blockquote_lines:
        return None

    # Parse metadata from blockquote (supports both English and Spanish keys)
    creator = "Unknown"
    pub_date = "Year 2026"
    content_type = "video"
    
    # Analyze blockquote lines
    for line in blockquote_lines:
        # Check Channel/Author, Canal/Autor, Channel, Canal, Author, Autor
        if match := re.search(r'\b(?:Channel/Author|Canal/Autor)\s*:\s*(.*)', line, re.IGNORECASE):
            creator = clean_creator(match.group(1))
        elif match := re.search(r'\b(?:Channel|Canal)\s*:\s*(.*)', line, re.IGNORECASE):
            creator = clean_creator(match.group(1))
        elif match := re.search(r'\b(?:Author|Autor)\s*:\s*(.*)', line, re.IGNORECASE):
            creator = clean_creator(match.group(1))
        elif line.startswith("**") and " — " in line:
            # Format: **Author — Title**
            creator_raw = line.split(" — ")[0].replace("**", "").replace("__", "").strip()
            creator = clean_creator(creator_raw)
            
        # Check Published, Publicado, Date, Fecha
        if match := re.search(r'\b(?:Published|Publicado)\s*:\s*(.*)', line, re.IGNORECASE):
            pub_date = match.group(1).replace("**", "").replace("~", "").strip()
        elif match := re.search(r'\b(?:Date|Fecha)\s*:\s*(.*)', line, re.IGNORECASE):
            pub_date = match.group(1).replace("**", "").strip()
            
        # Check Type, Tipo
        if match := re.search(r'\b(?:Type|Tipo)\s*:\s*(.*)', line, re.IGNORECASE):
            content_type = match.group(1).replace("**", "").strip()

    # Determine category from parent directory relative to VAULT_BASE_DIR
    rel_path = file_path.parent.relative_to(vault_base_dir)
    category = str(rel_path)
    if category == ".":
        category = "General"
    else:
        # Take the top level folder under AI Engineer
        parts = rel_path.parts
        if parts:
            category = parts[0]

    # Clean note name for internal link
    note_name = file_path.stem
    
    return {
        "note_link": f"[[{note_name}]]",
        "creator": creator,
        "category": category,
        "type": content_type,
        "pub_date": pub_date,
        "path": file_path
    }

def rebuild_master_plan(target_kb: str = "dataScienceKnowledgeBase/AI Engineer"):
    vault_base_dir = VAULT_ROOT / target_kb
    master_plan_title_part = get_master_plan_title(target_kb)
    master_plan_path = vault_base_dir / f"Master Plan — {master_plan_title_part} Curated Series.md"
    
    print(f"Scanning for curated notes in: {vault_base_dir}")
    notes = []
    
    # Recursive search
    for root, dirs, files in os.walk(vault_base_dir):
        # Exclude dswok zone strictly
        if "dswok" in root or "dswok" in dirs:
            if "dswok" in dirs:
                dirs.remove("dswok")
            continue
            
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                note_data = parse_curated_note(file_path, vault_base_dir)
                if note_data:
                    notes.append(note_data)

    # Sort notes by category then note name to keep it structured
    notes.sort(key=lambda x: (x["category"], x["note_link"]))

    # Generate the Markdown Table (in English)
    table_lines = [
        "| Note / Link | Channel / Creator | Vault Category | Content Type | Publication Date |",
        "| --- | --- | --- | --- | --- |"
    ]
    for n in notes:
        table_lines.append(f"| {n['note_link']} | {n['creator']} | {n['category']} | {n['type']} | {n['pub_date']} |")
    
    table_content = "\n".join(table_lines)
    
    if not master_plan_path.exists():
        print(f"Master plan file {master_plan_path} not found. Creating a new one.")
        # Create a new Master Plan in English
        master_plan_template = f"""# Master Plan — {master_plan_title_part} Curated Series

This Master Plan serves as the primary navigation hub for the curated series of {master_plan_title_part} technical videos.

## 🗺️ Series Navigation Map

Below are the notes that make up this Master Plan, classified by their category and recommended logical learning order:

{table_content}

---

## 🎯 Learning Series Objectives

1. **Logical Understanding and Infrastructure**: Understand the limits of AI reasoning and how to equip it with standardized external accessibility via the Model Context Protocol (MCP).
2. **Agent Orchestration and Proactivity**: Evolve from reactive assistants to asynchronous automation using AI routine systems and graph-based flow control.
3. **Evaluation-Driven Development (EDD)**: Replace informal "vibes"-based testing with robust RAG telemetry instrumentation and regression harnesses with an LLM as judge.

## 🔗 Relationship with Other Vault Categories
- **AI Agents**: Complement the understanding of how to orchestrate fault-tolerant architectures and flows.
- **MCP**: Expand the developer's ability to interact dynamically with local databases and remote APIs.
"""
        master_plan_path.write_text(master_plan_template, encoding="utf-8")
        print(f"Created new Master Plan at {master_plan_path}")
        return True
        
    # Read existing Master Plan
    content = master_plan_path.read_text(encoding="utf-8")
    
    # Locate the table between ## 🗺️ Series Navigation Map and --- (or Spanish equivalent ## 🗺️ Mapa de Navegación de la Serie)
    pattern = r"(## 🗺️ (?:Series Navigation Map|Mapa de Navegación de la Serie)\n\n.*?\n\n)(.*?)(?=\n\n---|\n---)"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Translate the section heading too if it was in Spanish
        heading = "## 🗺️ Series Navigation Map\n\nBelow are the notes that make up this Master Plan, classified by their category and recommended logical learning order:\n\n"
        new_content = content[:match.start(1)] + heading + table_content + content[match.end(2):]
        
        # Translate other core parts to English if they were Spanish
        new_content = new_content.replace(f"# Master Plan — {master_plan_title_part} Curated Series", f"# Master Plan — {master_plan_title_part} Curated Series")
        new_content = new_content.replace("## 🎯 Objetivos de la Serie de Aprendizaje", "## 🎯 Learning Series Objectives")
        new_content = new_content.replace("## 🔗 Relación con Otras Categorías del Vault", "## 🔗 Relationship with Other Vault Categories")
        
        master_plan_path.write_text(new_content, encoding="utf-8")
        print(f"Successfully updated and translated Master Plan table at {master_plan_path}")
        return True
    else:
        # Fallback regex search if exact text is slightly different
        pattern_fallback = r"(## 🗺️ (?:Series Navigation Map|Mapa de Navegación de la Serie)\s*\n\s*)(.*?)(?=\n\s*---|\n\s*##)"
        match_fallback = re.search(pattern_fallback, content, re.DOTALL)
        if match_fallback:
            new_content = content[:match_fallback.start(2)] + table_content + "\n" + content[match_fallback.end(2):]
            master_plan_path.write_text(new_content, encoding="utf-8")
            print(f"Successfully updated Master Plan table (fallback match) at {master_plan_path}")
            return True
        else:
            print("Error: Could not locate the navigation map table section in the existing Master Plan. Appending new table at the bottom.")
            content += f"\n\n## 🗺️ Series Navigation Map (Updated)\n\n{table_content}\n"
            master_plan_path.write_text(content, encoding="utf-8")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Master Plan")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root")
    args = parser.parse_args()
    rebuild_master_plan(args.target_kb)
