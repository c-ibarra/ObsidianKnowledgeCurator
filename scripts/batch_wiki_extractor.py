#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
# CONFIGURATION & .ENV LOADING
# ==============================================================================

PROJECT_DIR = Path(__file__).parent.parent
ENV_PATH = PROJECT_DIR / ".env"

def load_env():
    env_vars = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip('"').strip("'")
                env_vars[key.strip()] = val
                os.environ[key.strip()] = val
    return env_vars

env = load_env()

# Vault Directories
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian"))
AI_ENGINEER_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / "AI Engineer"
RAW_DIR = AI_ENGINEER_DIR / "raw"
WIKI_DIR = AI_ENGINEER_DIR / "wiki"
CACHE_FILE = PROJECT_DIR / "temp" / "wiki_extraction_cache.json"

# Models and API
MODEL_ENGINE = os.environ.get("MODEL_ENGINE", "gemini-2.5-pro")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ==============================================================================
# GEMINI API CALLER
# ==============================================================================

def call_gemini(prompt: str) -> str:
    import requests
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in .env")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    res_json = response.json()
    return res_json["candidates"][0]["content"]["parts"][0]["text"]

# ==============================================================================
# EXTRACTION LOGIC
# ==============================================================================

def process_file(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        filename_no_ext = file_path.stem
        
        prompt = f"""
Act as a Knowledge Compiler for an Obsidian vault. Read the following curated note:

{content[:15000]}

Identify 3 to 7 core concepts. For each concept, provide a brief synthesized explanation based ONLY on this text.
Format your output as a JSON object where keys are concept names (in Camel Case or Pascal Case, e.g., "AgenticWorkflows") and values are the synthesized explanations.
Do not include markdown blocks, just the raw JSON object.
"""
        response = call_gemini(prompt)
        clean_json = response.replace("```json", "").replace("```", "").strip()
        concepts = json.loads(clean_json)
        
        WIKI_DIR.mkdir(parents=True, exist_ok=True)
        
        for concept_name, explanation in concepts.items():
            concept_file = WIKI_DIR / f"{concept_name}.md"
            if concept_file.exists():
                existing = concept_file.read_text(encoding="utf-8")
                if f"[[{filename_no_ext}]]" not in existing:
                    new_content = f"{existing}\n\n## Update from [[{filename_no_ext}]]\n{explanation}\n"
                    concept_file.write_text(new_content, encoding="utf-8")
            else:
                new_content = f"# {concept_name}\n\n{explanation}\n\n## Sources\n- [[{filename_no_ext}]]\n"
                concept_file.write_text(new_content, encoding="utf-8")
                
        return file_path.name, True, "Success"
    except Exception as e:
        return file_path.name, False, str(e)

# ==============================================================================
# MAIN BATCH PROCESSING
# ==============================================================================

def main():
    print("=" * 80)
    print("STARTING BATCH WIKI EXTRACTION")
    print("=" * 80)
    
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured. Exiting.")
        sys.exit(1)
        
    if not RAW_DIR.exists():
        print(f"Error: Raw directory not found at {RAW_DIR}")
        sys.exit(1)
        
    # Load cache
    cache = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        
    all_md_files = list(RAW_DIR.rglob("*.md"))
    pending_files = [f for f in all_md_files if f.name not in cache]
    
    print(f"Total raw files: {len(all_md_files)}")
    print(f"Already processed: {len(cache)}")
    print(f"Pending to process: {len(pending_files)}")
    
    if not pending_files:
        print("All files processed.")
        return

    success_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, f): f for f in pending_files}
        for future in as_completed(futures):
            name, success, msg = future.result()
            if success:
                print(f"[OK] {name}")
                cache[name] = True
                success_count += 1
                # Save cache progressively
                CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
                CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            else:
                print(f"[ERROR] {name}: {msg}")
                # Rate limit protection
                if "429" in msg or "quota" in msg.lower():
                    print("Rate limit reached. Pausing for 60 seconds...")
                    time.sleep(60)
                    
    print("=" * 80)
    print(f"Batch completed. Processed {success_count} files successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
