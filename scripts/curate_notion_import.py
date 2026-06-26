#!/usr/bin/env python3
import os
import sys
import re
import shutil
import argparse
import json
import time
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
COURSE_NAME = "Feature Engineering for Machine Learning"
TARGET_KB = "Machine Learning"

NOTION_DIR = VAULT_BASE / "Notion" / COURSE_NAME
ML_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / TARGET_KB
RAW_DIR = ML_DIR / "raw" / COURSE_NAME
WIKI_DIR = ML_DIR / "wiki"
MASTER_PLAN_PATH = ML_DIR / f"Master Plan — {TARGET_KB}.md"

# Models and API
raw_engine = os.environ.get("MODEL_ENGINE", "gemini-2.5-flash")
MODEL_ENGINE = "gemini-2.5-flash" if "gemini-3.1-pro" in raw_engine or not raw_engine else raw_engine
raw_gemini_key = os.environ.get("GEMINI_API_KEY", "")
if not raw_gemini_key or "your-gemini-api-key" in raw_gemini_key:
    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
else:
    GEMINI_API_KEY = raw_gemini_key

# ==============================================================================
# GEMINI API CALLER WITH RETRIES
# ==============================================================================

def call_gemini(prompt: str, max_retries=5, initial_delay=2) -> str:
    import requests
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured or invalid in .env")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 429:
                print(f"[API WARN] Rate limited (429). Retrying in {delay} seconds (attempt {attempt+1}/{max_retries})...")
                time.sleep(delay)
                delay *= 2
                continue
            response.raise_for_status()
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"[API WARN] Error calling Gemini: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2
    return ""

# ==============================================================================
# INDIVIDUAL NOTE PROCESSOR
# ==============================================================================

def clean_section_name(raw_name: str) -> str:
    """Converts 'Section-08-Categorical-Encoding-Basic' to 'Section-08 — Categorical Encoding Basic'."""
    # Pattern to match Section-XX-Topic
    match = re.match(r"^Section-(\d+)-(.*)$", raw_name)
    if match:
        num = match.group(1)
        topic = match.group(2).replace("-", " ")
        return f"Section-{num} — {topic}"
    return raw_name.replace("-", " ")

def curate_single_file(file_path: Path, dry_run: bool) -> tuple[str, bool, str]:
    try:
        if not file_path.exists():
            return file_path.name, False, f"File {file_path} does not exist"
            
        content = file_path.read_text(encoding="utf-8")
        original_title = file_path.stem
        raw_section = file_path.parent.name
        cleaned_section = clean_section_name(raw_section)
        
        # Define target note path and clean note name
        # Remove "FEML - XX - " prefix for raw zone filenames if present to keep it elegant, or keep it consistent
        # Let's keep the name as is or clean the "FEML - XX - " prefix. Wait, keeping the name clean is great, but let's maintain original for links.
        clean_title = original_title
        dest_filename = f"{clean_title}.md"
        dest_file_path = RAW_DIR / cleaned_section / dest_filename
        
        if dry_run:
            return original_title, True, f"[DRY-RUN] Will process and move to: {dest_file_path.relative_to(VAULT_BASE)}"
            
        # 1. Note Curation Pass
        prompt = f"""
Act as an expert Knowledge Architect in Obsidian and {TARGET_KB} Engineering.
Your goal is to process the following imported Notion note about {COURSE_NAME}, restructure it under the user's strict vault conventions, and return the formatted markdown.

Note Details:
- Original Title: {original_title}
- Original Section: {cleaned_section}

Output Format Requirements:
1. The first line of the output must be the exact category classification of the vault in this format:
CATEGORY: {COURSE_NAME}/{cleaned_section}

2. Starting from the second line, return the structured note exactly like this:
- A unique H1 title in English (you can clean prefixes like "FEML - XX - " from the H1 if appropriate, but keep the thematic title clear).
- A clean metadata blockquote with:
  > **Source:** Notion Course
  > **Author:** Carlos Ibarra · **Date:** May 2026
  > **Type:** course note
  > **Tags:** #no-read-yet
- A "## 📌 Key Takeaways" section with numbered points of the most important concepts. Maximum use of emojis in this section to highlight insights.
- Ordered thematic sections (## 1. Topic, ## 2. Topic) with detailed technical development of the note, preserving python code, advantages, disadvantages, and practical implementations.
- "## Flashcards" section with key questions and answers formatted in English:
  1. **Q:** [Question]? → **A:** [Synthetic and clear answer]
- "## Glossary" section with non-obvious technical terms formatted as:
  - **[Term]**: [Definition]
- "## Related" section with suggested wikilinks to other course notes or concepts.
- CRITICAL RULES:
  - NEVER use YAML frontmatter.
  - NEVER use emojis outside the "## 📌 Key Takeaways" section.
  - Keep the language in English.

Original note content:
\"\"\"
{content}
\"\"\"
"""
        curated_text = call_gemini(prompt)
        if not curated_text:
            return original_title, False, "Curation pass returned empty response"
            
        # Parse Category and Content
        category = f"{COURSE_NAME}/{cleaned_section}"
        note_content = curated_text.strip()
        
        first_line_match = re.match(r"^CATEGORY:\s*(.*)", curated_text.strip())
        if first_line_match:
            category = first_line_match.group(1).strip()
            # Remove the first line
            note_content = "\n".join(curated_text.strip().splitlines()[1:]).strip()
            
        # Ensure directories exist
        dest_file_path.parent.mkdir(parents=True, exist_ok=True)
        dest_file_path.write_text(note_content, encoding="utf-8")
        
        # 2. Concept Compilation Pass (Wiki)
        wiki_prompt = f"""
Act as a Knowledge Compiler. Read the following curated note:

{note_content[:15000]}

Identify 3 to 5 fundamental technical concepts explained in detail in this text.
For each concept, provide a deep, synthesized explanation in English based ONLY on this text.
Format your output strictly as a raw JSON object in English where the keys are the concept names (in Camel Case or Pascal Case with no spaces, e.g. "TargetEncoding", "MeanMedianImputation") and the values are the detailed explanations.
Do not include markdown blocks like ```json, only the raw JSON object.
"""
        wiki_response = call_gemini(wiki_prompt)
        try:
            clean_json = wiki_response.replace("```json", "").replace("```", "").strip()
            concepts = json.loads(clean_json)
            
            WIKI_DIR.mkdir(parents=True, exist_ok=True)
            for concept_name, explanation in concepts.items():
                # Clean concept name to follow PascalCase
                concept_name_clean = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', '', concept_name)
                concept_file = WIKI_DIR / f"{concept_name_clean}.md"
                source_link = dest_filename.replace('.md', '')
                
                if concept_file.exists():
                    existing = concept_file.read_text(encoding="utf-8")
                    if f"[[{source_link}]]" not in existing:
                        new_content = f"{existing}\n\n## Update from [[{source_link}]]\n{explanation}\n"
                        concept_file.write_text(new_content, encoding="utf-8")
                else:
                    new_content = f"# {concept_name_clean}\n\n{explanation}\n\n## Sources\n- [[{source_link}]]\n"
                    concept_file.write_text(new_content, encoding="utf-8")
        except Exception as wiki_err:
            print(f"[WIKI ERR] Failed to extract concepts for {original_title}: {wiki_err}")
            
        # 3. Safe Move of Original Notion File to "processed/" subfolder
        processed_dir = NOTION_DIR / "processed" / raw_section
        processed_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(processed_dir / file_path.name))
        
        return original_title, True, "Successfully curated, concept-compiled, and moved."
        
    except Exception as e:
        return file_path.name, False, str(e)

# ==============================================================================
# MASTER PLAN REBUILDER
# ==============================================================================

def parse_curated_note_metadata(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    if "Master Plan" in file_path.name or "plan" in file_path.name.lower():
        return None

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
            blockquote_line = stripped[1:].strip()
            blockquote_lines.append(blockquote_line)
        elif in_blockquote and not stripped.startswith(">") and stripped != "":
            break

    if not title or not blockquote_lines:
        return None

    author = "Carlos Ibarra"
    date = "May 2026"
    content_type = "course note"

    for line in blockquote_lines:
        if match := re.search(r'\b(?:Author|Autor)\s*:\s*(.*)', line, re.IGNORECASE):
            author = match.group(1).replace("**", "").split("·")[0].split("•")[0].strip()
        if match := re.search(r'\b(?:Published|Publicado|Fecha|Date)\s*:\s*(.*)', line, re.IGNORECASE):
            date = match.group(1).replace("**", "").split("·")[0].split("•")[0].strip()
        if match := re.search(r'\b(?:Type|Tipo)\s*:\s*(.*)', line, re.IGNORECASE):
            content_type = match.group(1).replace("**", "").strip()

    # Determine category relative to ML_DIR
    try:
        rel_path = file_path.parent.relative_to(ML_DIR)
        category = str(rel_path)
    except Exception:
        category = "General"

    if category == ".":
        category = "General"

    note_name = file_path.stem
    return {
        "note_link": f"[[{note_name}]]",
        "author": author,
        "date": date,
        "type": content_type,
        "category": category,
        "name": note_name
    }

def rebuild_ml_master_plan():
    print(f"Rebuilding {TARGET_KB} Master Plan at: {MASTER_PLAN_PATH}")
    notes = []
    
    # Recursive scan of raw/ and other folders inside ML_DIR
    for root, dirs, files in os.walk(ML_DIR):
        if "wiki" in root or "wiki" in dirs:
            if "wiki" in dirs:
                dirs.remove("wiki")
            continue
            
        for file in files:
            if file.endswith(".md"):
                note_data = parse_curated_note_metadata(Path(root) / file)
                if note_data:
                    notes.append(note_data)
                    
    # Sort notes by category, then name
    notes.sort(key=lambda x: (x["category"], x["name"]))
    
    # Build Markdown table
    table_lines = [
        "| Note / Link | Author | Date | Type | Section / Category |",
        "| --- | --- | --- | --- | --- |"
    ]
    for n in notes:
        table_lines.append(f"| {n['note_link']} | {n['author']} | {n['date']} | {n['type']} | {n['category']} |")
        
    table_content = "\n".join(table_lines)
    
    category_name = ML_DIR.name
    if category_name == "Machine Learning":
        description = """Collection of resources on Machine Learning: algorithms, model tuning, evaluation, feature engineering, and best practices. Covers both classic ML (boosting, decision trees, regression) and advanced optimization and data preprocessing techniques."""
        themes_section = """- Feature analysis of variables (cardinality, distributions, outliers)
- Univariate and multivariate imputation (KNN, MICE, missForest)
- Categorical variable encoding (One-Hot, Ordinal, Target Encoding with smoothing, WoE)
- Variable transformations for normality (Log, Box-Cox, Yeo-Johnson)
- Basic and advanced discretization (Equal-Width, Equal-Frequency, Decision Tree binning)
- Feature scaling (Standardization, Min-Max, Robust Scaling)"""
    else:
        description = f"Collection of resources, notes, and guides on {category_name} automatically curated by the Knowledge Curator."
        themes_section = f"- Technical notes and guides for {category_name}\n- Practical concepts and implementations"
    
    # Let's read the existing Master Plan to preserve other sections if it exists
    original_content = ""
    if MASTER_PLAN_PATH.exists():
        original_content = MASTER_PLAN_PATH.read_text(encoding="utf-8")
        
    # Check if we can replace the table section
    pattern = r"(## (?:Notas en esta categoría|Notes in this category)\n\n)(.*?)(?=\n\n---|\n---|\Z)"
    if original_content and re.search(pattern, original_content, re.DOTALL):
        new_content = re.sub(pattern, f"\\1{table_content}", original_content, flags=re.DOTALL)
        # Update last modified date
        new_content = re.sub(r'> \*\*(?:Última actualización|Last update):\*\* .*', '> **Last update:** May 2026', new_content)
        MASTER_PLAN_PATH.write_text(new_content, encoding="utf-8")
        print("Updated existing Master Plan successfully.")
    else:
        # Create a fresh new Master Plan
        master_plan_template = f"""# Master Plan — {category_name}

> **Type:** Resource Index
> **Path:** `{category_name}/`
> **Last update:** May 2026

---

## Description

{description}

---

## Notes in this category

{table_content}

---

## Themes covered

{themes_section}

---

## Related

- [[Master Plan — Learn Harness Engineering]]
"""
        MASTER_PLAN_PATH.write_text(master_plan_template, encoding="utf-8")
        print("Created new Master Plan.")

# ==============================================================================
# MAIN RUNNER
# ==============================================================================

def main():
    global NOTION_DIR, ML_DIR, RAW_DIR, WIKI_DIR, MASTER_PLAN_PATH, COURSE_NAME, TARGET_KB
    
    parser = argparse.ArgumentParser(description="Process Notion notes into Obsidian structured zones generically.")
    parser.add_argument("--dry-run", action="store_true", help="Scan files and display what would be done, without making API calls or modifications.")
    parser.add_argument("--file", help="Specify a single file (relative to Notion dir) to process for testing.")
    parser.add_argument("--execute", action="store_true", help="Actually perform the curation, concept compilation, and moving.")
    
    # Generic parameterization arguments
    parser.add_argument("--notion-dir", default="Feature Engineering for Machine Learning", help="Source Notion folder name or absolute path.")
    parser.add_argument("--target-kb", default="Machine Learning", help="Target category folder name or absolute path.")
    parser.add_argument("--course-name", help="Course/resource name used inside raw/ and metadata (default: folder name of --notion-dir).")
    
    args = parser.parse_args()
    
    if not args.execute and not args.dry_run:
        print("Error: You must specify either --dry-run or --execute.")
        sys.exit(1)
        
    # 1. Resolve --notion-dir path
    notion_path_arg = Path(args.notion_dir)
    if notion_path_arg.is_absolute():
        NOTION_DIR = notion_path_arg
    else:
        NOTION_DIR = VAULT_BASE / "Notion" / notion_path_arg
        
    # 2. Resolve --target-kb path
    target_kb_arg = Path(args.target_kb)
    if target_kb_arg.is_absolute():
        ML_DIR = target_kb_arg
    else:
        ML_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / target_kb_arg
        
    # 3. Resolve TARGET_KB name
    TARGET_KB = ML_DIR.name
    
    # 4. Resolve COURSE_NAME
    if args.course_name:
        COURSE_NAME = args.course_name
    else:
        COURSE_NAME = NOTION_DIR.name
        
    # 5. Reconstruct other paths
    RAW_DIR = ML_DIR / "raw" / COURSE_NAME
    WIKI_DIR = ML_DIR / "wiki"
    MASTER_PLAN_PATH = ML_DIR / f"Master Plan — {TARGET_KB}.md"
        
    print("=" * 80)
    print(f"NOTION MIGRATION WORKFLOW — {'DRY RUN' if args.dry_run else 'EXECUTION MODE'}")
    print(f"Notion Src:   {NOTION_DIR}")
    print(f"KB Target:    {ML_DIR}")
    print(f"Raw Target:   {RAW_DIR}")
    print(f"Wiki Target:  {WIKI_DIR}")
    print(f"Master Plan:  {MASTER_PLAN_PATH}")
    print(f"Course Name:  {COURSE_NAME}")
    print("=" * 80)
    
    if not NOTION_DIR.exists():
        print(f"Error: Notion import folder not found at: {NOTION_DIR}")
        sys.exit(1)
        
    # Scan for markdown files
    md_files = []
    for root, dirs, files in os.walk(NOTION_DIR):
        # Ignore processed/ folder and any hidden directories
        if "processed" in root or "processed" in dirs:
            if "processed" in dirs:
                dirs.remove("processed")
            continue
            
        for f in files:
            if f.endswith(".md") and "MOC" not in f:
                md_files.append(Path(root) / f)
                
    # Filter for single file if specified
    if args.file:
        single_path = NOTION_DIR / args.file
        if single_path.exists():
            md_files = [single_path]
            print(f"Targeting single file for processing: {args.file}")
        else:
            print(f"Error: Specified file not found at: {single_path}")
            sys.exit(1)
            
    print(f"Found {len(md_files)} markdown files to process.")
    
    if args.dry_run:
        print("\n--- File Mapping Simulation ---")
        for f in md_files:
            rel_path = f.relative_to(NOTION_DIR)
            raw_section = f.parent.name
            cleaned_section = clean_section_name(raw_section)
            dest = RAW_DIR / cleaned_section / f.name
            print(f"Source: [Notion] {rel_path}\nTarget: {dest.relative_to(VAULT_BASE)}\n")
        print("Dry run completed. No files were modified.")
        return
        
    # Execute batch processing
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not configured in your .env file or environment.")
        sys.exit(1)
        
    print("\nStarting batch processing (using max 4 parallel workers)...")
    success_count = 0
    fail_count = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(curate_single_file, f, False): f for f in md_files}
        for future in as_completed(futures):
            name, success, msg = future.result()
            if success:
                print(f"[OK] {name}: {msg}")
                success_count += 1
            else:
                print(f"[FAIL] {name}: {msg}")
                fail_count += 1
                
    print("\n" + "=" * 80)
    print(f"BATCH PROCESS COMPLETED: {success_count} succeeded, {fail_count} failed.")
    print("=" * 80)
    
    # Rebuild Master Plan
    if success_count > 0:
        rebuild_ml_master_plan()
        
if __name__ == "__main__":
    main()
