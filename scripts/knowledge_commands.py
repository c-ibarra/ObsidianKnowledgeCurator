#!/usr/bin/env python3
import os
import argparse
import subprocess
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))
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
    notes = []
    # Collect notes in AI Engineer dir
    if AI_ENGINEER_DIR.exists():
        count = 0
        for root, dirs, files in os.walk(AI_ENGINEER_DIR):
            if "dswok" in root:
                continue
            for file in files:
                if file.endswith(".md"):
                    if count >= limit:
                        break
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        notes.append(f"--- Note: {file} ---\n{content[:2000]}\n")
                        count += 1
                    except:
                        pass
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
    query_lower = query.lower()
    matches = []
    
    if VAULT_BASE.exists():
        for root, dirs, files in os.walk(VAULT_BASE):
            if any(p in root for p in ["dswok", ".obsidian", ".git", ".trash", ".smart-env"]):
                continue
            for file in files:
                if file.endswith(".md"):
                    file_name_no_ext = file[:-3]
                    if query_lower in file_name_no_ext.lower():
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(VAULT_BASE)
                        matches.append((file_name_no_ext, rel_path))
                        
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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Knowledge Commands for Obsidian LLM Wiki")
    parser.add_argument("--trace", type=str, help="Run /trace on a specific topic")
    parser.add_argument("--emerge", action="store_true", help="Run /emerge to find implied ideas")
    parser.add_argument("--drift", action="store_true", help="Run /drift to compare intentions vs actions")
    parser.add_argument("--find", type=str, help="Search the vault for matching note names")
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
    elif args.tokens:
        run_tokens()
    else:
        parser.print_help()

