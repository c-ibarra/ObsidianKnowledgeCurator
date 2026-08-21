#!/usr/bin/env python3
import os
import argparse
import subprocess
import json
import urllib.parse
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

import sys
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR / "scripts"))

from src.config import (
    VAULT_ROOT,
    PROJECT_ROOT,
    GRAPHIFY_DAEMON_GRAPH_JSON,
    GRAPHIFY_BACKEND,
    normalize_graphify_backend,
)

VAULT_BASE = VAULT_ROOT
AI_ENGINEER_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / "AI Engineer"

# Assume curate_notion_import has call_gemini
try:
    from curate_notion_import import call_gemini
except ImportError:
    # Fallback to importing dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location("curate_notion_import", str(PROJECT_DIR / "scripts" / "curate_notion_import.py"))
    curate_notion_import = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(curate_notion_import)
    call_gemini = curate_notion_import.call_gemini

# ==============================================================================
# COMMANDS LOGIC
# ==============================================================================

def gather_vault_context(limit=100):
    """Gather text from recent/relevant notes to serve as context."""
    from vault_db import get_vault_db_connection
    notes = []
    try:
        conn = get_vault_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, content FROM files 
            WHERE is_document = 1 
              AND path LIKE 'dataScienceKnowledgeBase/AI Engineer/%'
              AND path NOT LIKE '%dswok%'
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        for name, content in rows:
            if content:
                notes.append(f"--- Note: {name}.md ---\n{content[:2000]}\n")
        conn.close()
    except Exception as e:
        print(f"Error gathering context from database: {e}")
    return "\n".join(notes)

def run_trace(topic: str):
    print(f"Running /trace for topic: {topic}...")
    context = gather_vault_context()
    
    prompt = f"""
Act as a Knowledge Synthesizer. Read the following vault notes:

{context}

Command: /trace
Topic: {topic}

Build a chronological timeline of how this idea developed across these notes:
- When it first appeared
- How the language and framing shifted over time
- Key turning points
- What other topics it connects to
Quote directly where relevant. Do not hallucinate. If the topic is not found, state that clearly.
"""
    result = call_gemini(prompt)
    print("\n=== TRACE RESULT ===")
    print(result)

def run_emerge():
    print("Running /emerge to find implied ideas...")
    context = gather_vault_context(limit=150) # Read more notes
    
    prompt = f"""
Act as a Knowledge Synthesizer. Read the following vault notes:

{context}

Command: /emerge

Look for:
- Recurring themes that appear 3+ times but don't seem to have a standalone concept
- Conclusions my notes point toward without stating directly
- Questions I keep circling without answering

Separate what my notes actually say from what you're inferring.
"""
    result = call_gemini(prompt)
    print("\n=== EMERGE RESULT ===")
    print(result)

def run_drift():
    print("Running /drift to check stated intentions vs behavior...")
    context = gather_vault_context()
    
    prompt = f"""
Act as a Knowledge Synthesizer. Read the following vault notes:

{context}

Command: /drift

Find notes where I stated intentions, goals, or plans. Then look at what I actually wrote about doing in other notes.
Identify:
- Things I said I'd focus on but didn't
- Things I didn't plan to focus on but kept returning to
Be blunt. Catch self-deception.
"""
    result = call_gemini(prompt)
    print("\n=== DRIFT RESULT ===")
    print(result)
def run_find(query: str):
    print(f"Searching vault for notes matching: '{query}'...")
    from vault_db import get_vault_db_connection
    matches = []
    try:
        conn = get_vault_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, path FROM files 
            WHERE is_document = 1 
              AND name LIKE ? 
              AND path NOT LIKE '%dswok%'
        """, (f"%{query}%",))
        matches = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error searching database: {e}")
        return
        
    if not matches:
        print("No matching notes found.")
        return
        
    print(f"\nFound {len(matches)} matching note(s):")
    print("--------------------------------------------------------------------------------")
    for name, rel_path in matches:
        print(f"- [[{name}]] -> {rel_path}")
    print("--------------------------------------------------------------------------------")

def run_tokens():
    brain_dir = Path(os.path.expanduser("~/.gemini/antigravity/brain"))
    if not brain_dir.exists():
        print("Antigravity brain directory not found.")
        return
    
    # Find most recent transcript log
    jsonl_files = list(brain_dir.glob("*/.system_generated/logs/transcript.jsonl"))
    if not jsonl_files:
        print("No conversation transcript log found.")
        return
        
    latest_log = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    size_bytes = latest_log.stat().st_size
    content = latest_log.read_text(encoding="utf-8", errors="ignore")
    char_count = len(content)
    words = len(content.split())
    est_tokens = int(char_count / 3.8)
    percent_1m = (est_tokens / 1_000_000) * 100
    
    print("\n=== ANTIGRAVITY CONTEXT WINDOW STATUS ===")
    print(f"Transcript Log: {latest_log}")
    print(f"Tokens Estimados: ~{est_tokens:,} tokens ({percent_1m:.1f}% de 1M)")
    print(f"Caracteres: {char_count:,}")
    print(f"Palabras: {words:,}")
    print(f"Tamaño Log: {size_bytes / (1024*1024):.2f} MB ({size_bytes:,} bytes)")
    print(f"USO DE CONTEXTO: {percent_1m:.1f}% del límite (1,000,000 tokens)")
    print("=========================================\n")



def get_note_summary(file_path: Path) -> str:
    if not file_path.exists():
        return "[File not found]"
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        # Check if there is a Key Takeaways section
        takeaways = []
        in_takeaways = False
        for line in lines:
            if line.startswith("## 📌 Key Takeaways"):
                in_takeaways = True
                continue
            elif line.startswith("## ") and in_takeaways:
                break
            if in_takeaways:
                if line.strip():
                    takeaways.append(line.strip())
        
        if takeaways:
            return "\n".join(takeaways[:5]) # limit to 5 lines
            
        # Fallback: extract the first blockquote description or first paragraph
        fallback_lines = []
        for line in lines:
            if line.startswith("# "):
                continue
            if line.startswith(">"):
                # source/metadata blockquote
                continue
            if line.strip():
                fallback_lines.append(line.strip())
                if len(fallback_lines) >= 3:
                    break
        return "\n".join(fallback_lines)
    except Exception as e:
        return f"[Error reading summary: {e}]"

def get_note_summary_from_db_or_file(rel_path_str: str, fs_path: Path) -> str:
    from vault_db import get_vault_db_connection
    try:
        conn = get_vault_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM files WHERE path = ?", (rel_path_str,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            content = row[0]
            lines = content.splitlines()
            takeaways = []
            in_takeaways = False
            for line in lines:
                if line.startswith("## 📌 Key Takeaways"):
                    in_takeaways = True
                    continue
                elif line.startswith("## ") and in_takeaways:
                    break
                if in_takeaways:
                    if line.strip():
                        takeaways.append(line.strip())
            
            if takeaways:
                return "\n".join(takeaways[:5])
                
            fallback_lines = []
            for line in lines:
                if line.startswith("# "):
                    continue
                if line.startswith(">"):
                    continue
                if line.strip():
                    fallback_lines.append(line.strip())
                    if len(fallback_lines) >= 3:
                        break
            return "\n".join(fallback_lines)
    except Exception:
        pass
    return get_note_summary(fs_path)

class GraphBackendUnavailable(RuntimeError):
    """Raised when GRAPHIFY_BACKEND=remote is forced but the daemon's
    graph.json isn't there or fails to parse -- the whole point of forcing
    a backend is to know for sure, not to silently fall back."""


def _load_graph_data():
    """Load the concept graph. GRAPHIFY_BACKEND controls the source:

    - "local": only ever reads the legacy graphify_helper.py pipeline's
      graph.json.
    - "remote": only ever reads graphify-daemon's output; raises
      GraphBackendUnavailable instead of falling back if it's not there
      or fails to parse.
    - anything else ("auto", unset, or an unrecognized value): today's
      default -- prefer the daemon's output (live, republishes on every
      vault batch), fall back to legacy silently.

    Returns (data, path), or (None, None) in local/auto mode when nothing
    was found.
    """
    legacy_path = PROJECT_DIR / "graphify-out" / "graph.json"
    mode = normalize_graphify_backend(GRAPHIFY_BACKEND)

    if mode == "local":
        candidates = (legacy_path,)
    elif mode == "remote":
        candidates = (GRAPHIFY_DAEMON_GRAPH_JSON,)
    else:
        candidates = (GRAPHIFY_DAEMON_GRAPH_JSON, legacy_path)

    for path in candidates:
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f), path
        except Exception:
            continue

    if mode == "remote":
        raise GraphBackendUnavailable(
            f"GRAPHIFY_BACKEND=remote but graphify-daemon's graph.json was not "
            f"found or unreadable at {GRAPHIFY_DAEMON_GRAPH_JSON}."
        )
    return None, None


def _resolve_source_file(source_file: str):
    """Build (fs_path, obsidian_uri, rel_path_str) for a node's source_file.

    The legacy graph.json (graphify_helper.py, indexes both the vault and
    this repo's own code) tags nodes with a `vault://`/`project://` scheme.
    graphify-daemon's graph.json (vault-only) omits the scheme entirely --
    every source_file it emits is already vault-relative, so "no scheme"
    is treated the same as `vault://`.
    """
    if source_file.startswith("project://"):
        rel_path = source_file[len("project://"):]
        fs_path = PROJECT_DIR / rel_path
        return fs_path, f"file://{fs_path}", rel_path

    rel_path = source_file[len("vault://"):] if source_file.startswith("vault://") else source_file
    fs_path = VAULT_BASE / rel_path
    obsidian_uri = f"obsidian://open?vault={urllib.parse.quote(VAULT_BASE.name)}&file={urllib.parse.quote(rel_path)}"
    return fs_path, obsidian_uri, rel_path


def run_explore(concept: str):
    try:
        data, graph_path = _load_graph_data()
    except GraphBackendUnavailable as e:
        print(f"Error: {e}")
        return
    if data is None:
        legacy_path = PROJECT_DIR / "graphify-out" / "graph.json"
        print(
            f"Error: No graphify index found (checked {GRAPHIFY_DAEMON_GRAPH_JSON} "
            f"and {legacy_path}). Run /okc-sync or python scripts/graphify_helper.py first."
        )
        return

    nodes = data.get("nodes", [])
    links = data.get("links", [])
    
    concept_lower = concept.lower()
    matched_node = None
    
    # Try exact match (case-insensitive) on label
    for n in nodes:
        label = n.get("label", "")
        if label.lower() == concept_lower or n.get("id", "").lower() == concept_lower:
            matched_node = n
            break
            
    # If no exact match, try substring match on label
    if not matched_node:
        substring_matches = []
        for n in nodes:
            label = n.get("label", "")
            if concept_lower in label.lower():
                substring_matches.append(n)
        
        if not substring_matches:
            print(f"No concept found matching '{concept}'.")
            return
            
        if len(substring_matches) == 1:
            matched_node = substring_matches[0]
        else:
            print(f"Ambiguous query '{concept}'. Did you mean one of these?")
            for match in substring_matches[:10]:
                print(f"- {match.get('label')} ({match.get('file_type')})")
            if len(substring_matches) > 10:
                print(f"... and {len(substring_matches) - 10} more.")
            return

    # Process matched node
    node_id = matched_node.get("id")
    label = matched_node.get("label")
    file_type = matched_node.get("file_type", "unknown")
    source_file = matched_node.get("source_file", "")
    
    fs_path = None
    obsidian_uri = None
    rel_path_str = ""

    if source_file:
        fs_path, obsidian_uri, rel_path_str = _resolve_source_file(source_file)

    print(f"\n================================================================================")
    print(f"EXPLORE CONCEPT: {label}")
    print(f"================================================================================")
    print(f"Type: {file_type.upper()}")
    if source_file:
        print(f"Source: {source_file}")
    if obsidian_uri:
        print(f"Open Link: {obsidian_uri}")
    print("--------------------------------------------------------------------------------")
    
    if fs_path:
        summary = get_note_summary_from_db_or_file(rel_path_str, fs_path)
        print("Summary / Key Takeaways:")
        print(summary)
    else:
        print("Summary / Key Takeaways: [File not found or no source location]")
        
    print("--------------------------------------------------------------------------------")
    
    incoming = []
    outgoing = []
    
    id_to_node = {n.get("id"): n for n in nodes}
    
    for link in links:
        src_id = link.get("source")
        tgt_id = link.get("target")
        rel = link.get("relation", "linked_to")
        
        if src_id == node_id:
            nbr_node = id_to_node.get(tgt_id)
            if nbr_node:
                outgoing.append((rel, nbr_node))
        elif tgt_id == node_id:
            nbr_node = id_to_node.get(src_id)
            if nbr_node:
                incoming.append((rel, nbr_node))
                
    print("Direct Neighbors / Relationships:")
    
    def format_rel(rel_type: str, nbr: dict, is_outgoing: bool) -> str:
        nbr_label = nbr.get("label", "[Unknown]")
        nbr_type = nbr.get("file_type", "unknown")
        nbr_sf = nbr.get("source_file", "")
        
        if is_outgoing:
            rel_label = f"--> ({rel_type}) -->"
        else:
            if rel_type == "contains":
                rel_label = "<-- (contained_in) <--"
            elif rel_type == "calls":
                rel_label = "<-- (called_by) <--"
            elif rel_type == "references":
                rel_label = "<-- (referenced_by) <--"
            elif rel_type == "rationale_for":
                rel_label = "<-- (has_rationale) <--"
            else:
                rel_label = f"<-- ({rel_type}_of) <--"
                
        nbr_uri = ""
        if nbr_sf:
            if nbr_sf.startswith("vault://"):
                nrp = nbr_sf[len("vault://"):]
                nbr_uri = f"obsidian://open?vault={urllib.parse.quote(VAULT_BASE.name)}&file={urllib.parse.quote(nrp)}"
            elif nbr_sf.startswith("project://"):
                nrp = nbr_sf[len("project://"):]
                nbr_uri = f"file://{PROJECT_DIR / nrp}"
                
        uri_str = f" | [Open Link]({nbr_uri})" if nbr_uri else ""
        return f"- {rel_label} [[{nbr_label}]] ({nbr_type}){uri_str}"

    if not incoming and not outgoing:
        print("  (No direct connections found in the graphify index)")
    else:
        outgoing_sorted = sorted(outgoing, key=lambda x: x[1].get("label", "").lower())
        incoming_sorted = sorted(incoming, key=lambda x: x[1].get("label", "").lower())
        
        for rel_type, nbr in outgoing_sorted:
            print(format_rel(rel_type, nbr, is_outgoing=True))
        for rel_type, nbr in incoming_sorted:
            print(format_rel(rel_type, nbr, is_outgoing=False))
            
    print("================================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Knowledge Commands for Obsidian LLM Wiki")
    parser.add_argument("--trace", type=str, help="Run /trace on a specific topic")
    parser.add_argument("--emerge", action="store_true", help="Run /emerge to find implied ideas")
    parser.add_argument("--drift", action="store_true", help="Run /drift to compare intentions vs actions")
    parser.add_argument("--find", type=str, help="Search the vault for matching note names")
    parser.add_argument("--explore", type=str, help="Explore a concept in the local graph index")
    parser.add_argument("--tokens", action="store_true", help="Show current context window size and token count")
    
    args = parser.parse_args()
    
    if args.trace:
        run_trace(args.trace)
    elif args.emerge:
        run_emerge()
    elif args.drift:
        run_drift()
    elif args.find:
        run_find(args.find)
    elif args.explore:
        run_explore(args.explore)
    elif args.tokens:
        run_tokens()
    else:
        parser.print_help()

