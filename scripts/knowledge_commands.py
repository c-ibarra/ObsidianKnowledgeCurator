#!/usr/bin/env python3
import os
import argparse
import subprocess
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian"))
AI_ENGINEER_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / "AI Engineer"

# Assume curate_workflow has call_gemini
try:
    from curate_workflow import call_gemini
except ImportError:
    # Fallback to importing dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location("curate_workflow", str(PROJECT_DIR / "scripts" / "curate_workflow.py"))
    curate_workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(curate_workflow)
    call_gemini = curate_workflow.call_gemini

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Knowledge Commands for Obsidian LLM Wiki")
    parser.add_argument("--trace", type=str, help="Run /trace on a specific topic")
    parser.add_argument("--emerge", action="store_true", help="Run /emerge to find implied ideas")
    parser.add_argument("--drift", action="store_true", help="Run /drift to compare intentions vs actions")
    
    args = parser.parse_args()
    
    if args.trace:
        run_trace(args.trace)
    elif args.emerge:
        run_emerge()
    elif args.drift:
        run_drift()
    else:
        parser.print_help()
