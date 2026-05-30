#!/usr/bin/env python3
import os
import sys
import re
import argparse
import subprocess
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

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

# Models and API
MODEL_ENGINE = os.environ.get("MODEL_ENGINE", "gemini-2.5-pro")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ==============================================================================
# YOUTUBE & INGESTION HELPERS
# ==============================================================================

def get_video_id(url_or_id: str) -> str:
    """Extracts the 11-character video ID from a YouTube URL or ID."""
    if len(url_or_id) == 11:
        return url_or_id
    # Attempt with regex
    patterns = [
        r'(?:v=|\/v\/|embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id

def get_video_details(video_id: str):
    """Retrieves basic metadata of the video using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Retrieving metadata for video ID: {video_id} using yt-dlp...")
    try:
        # Get title
        title_proc = subprocess.run(
            ["yt-dlp", "--get-title", "--no-warnings", "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=30
        )
        title = title_proc.stdout.strip() if title_proc.returncode == 0 else f"YouTube Video {video_id}"

        # Get channel
        channel_proc = subprocess.run(
            ["yt-dlp", "--print", "uploader", "--no-warnings", "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=30
        )
        channel = channel_proc.stdout.strip() if channel_proc.returncode == 0 else "Uploader"

        # Get upload date
        date_proc = subprocess.run(
            ["yt-dlp", "--print", "upload_date", "--no-warnings", "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=30
        )
        upload_date = date_proc.stdout.strip() if date_proc.returncode == 0 else ""
        
        # Format the date to 'Month Year'
        date_str = "Year 2026"
        if len(upload_date) == 8:
            months = {
                "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June",
                "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"
            }
            year = upload_date[:4]
            month = months.get(upload_date[4:6], "January")
            date_str = f"{month} {year}"

        return {
            "title": title,
            "channel": channel,
            "date": date_str,
            "url": url
        }
    except Exception as e:
        print(f"Warning: Could not retrieve all metadata from yt-dlp: {e}")
        return {
            "title": f"YouTube Video {video_id}",
            "channel": "Unknown",
            "date": "Year 2026",
            "url": url
        }

def get_transcript(video_id: str) -> str:
    """Downloads the transcript using youtube-transcript-api (with fallback to yt-dlp)."""
    print(f"Downloading YouTube transcript for ID: {video_id}...")
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=['en', 'es'])
        text = " ".join([snippet.text for snippet in fetched.snippets])
        return text
    except Exception as e:
        print(f"youtube-transcript-api failed: {e}. Trying fallback with yt-dlp...")
        
    # Fallback with yt-dlp
    try:
        import tempfile
        import shutil
        tmp_dir = Path(tempfile.mkdtemp(prefix="yt_curate_"))
        
        subprocess.run(
            [
                "yt-dlp",
                "--write-subs", "--write-auto-subs",
                "--sub-lang", "en,es",
                "--sub-format", "vtt",
                "--skip-download", "--no-warnings",
                "--cookies-from-browser", "chrome",
                "--output", str(tmp_dir / "transcript"),
                f"https://www.youtube.com/watch?v={video_id}"
            ],
            capture_output=True, timeout=60
        )
        
        # Search for .vtt
        vtt_files = list(tmp_dir.glob("*.vtt"))
        if not vtt_files:
            raise RuntimeError("No subtitle file (.vtt) was downloaded")
            
        # Prioritize en over es
        en_vtt = list(tmp_dir.glob("*.en.vtt"))
        vtt_file = en_vtt[0] if en_vtt else vtt_files[0]
        vtt_text = vtt_file.read_text(encoding="utf-8")
        
        # Clean
        lines = vtt_text.splitlines()
        deduped = []
        prev = None
        for line in lines:
            if re.match(r"^(WEBVTT|Kind:|Language:|Style:)", line.strip()):
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*", line):
                continue
            if re.match(r"^\d+$", line.strip()):
                continue
            line = re.sub(r"<[^>]+>", "", line).strip()
            if not line:
                continue
            if line != prev:
                deduped.append(line)
            prev = line
            
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return " ".join(deduped)
    except Exception as e:
        print(f"Critical error obtaining transcript: {e}")
        return ""

# ==============================================================================
# NOTE GENERATION WITH GEMINI API
# ==============================================================================

def call_gemini(prompt: str) -> str:
    """Calls the Gemini API directly via REST requests without external libraries."""
    import requests
    
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured in the .env file or environment.")
        return ""
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        res_json = response.json()
        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except Exception as e:
        print(f"Error calling the Gemini API: {e}")
        return ""

def generate_curated_note(details: dict, transcript: str, category_list: list) -> tuple[str, str]:
    """Uses the Gemini API to classify the video and generate the structured note in English."""
    
    prompt = f"""
Act as an expert Knowledge Architect in Obsidian and AI Engineering.
Process the following transcript of the video titled "{details['title']}" from the channel "{details['channel']}".

Video Details:
- Title: {details['title']}
- Channel: {details['channel']}
- Published: {details['date']}
- URL: {details['url']}

The transcript to process:
\"\"\"
{transcript[:45000]}
\"\"\"

Output Requirements:
1. You must choose a CATEGORY of the vault among the following existing ones:
{json.dumps(category_list, ensure_ascii=False)}
If it does not fit perfectly in any of them, suggest a new short and clean category (in Camel Case or Pascal Case, e.g. "RAG", "Agentic RAG", "Evaluation"). Return the exact name of the selected category on the FIRST LINE of the output in this format:
CATEGORY: <Chosen Category>

2. Starting from the SECOND LINE, return the note in Markdown format strictly structured in English following the vault conventions:
- A unique H1 title.
- A blockquote with exact descriptive metadata (Author, Channel/Author, Date, Playlist, Type, Tags). It must include `Tags: #no-read-yet`.
- Section `## 📌 Key Takeaways` with numbered key points.
- Detailed thematic sections explaining the content of the video in depth (e.g. `## 1. Concept`, `## 2. Architecture`).
- Section `## Flashcards` in short Q&A format (Q: Question, A: Answer).
- Section `## Glossary` with definitions of key technical terms.
- Section `## Related` with suggested internal wikilinks based on the topic.
- NEVER use YAML frontmatter.
- NEVER use emojis outside the `## 📌 Key Takeaways` section.
"""
    
    print("Sending transcript to Gemini for curation...")
    response_text = call_gemini(prompt)
    if not response_text:
        return "", ""
        
    # Extract the chosen category from the first line
    category = "General"
    note_content = response_text
    
    first_line_match = re.match(r"^CATEGORY:\s*(.*)", response_text.strip())
    if first_line_match:
        category = first_line_match.group(1).strip()
        # Remove the first line
        note_content = "\n".join(response_text.strip().splitlines()[1:]).strip()
        
    return category, note_content

# ==============================================================================
# MAIN CURATION PIPELINE
# ==============================================================================

def curate_video(url_or_id: str, manual_category: str = None):
    print("=" * 80)
    print("STARTING END-TO-END AUTOMATED CURATION WORKFLOW")
    print("=" * 80)
    
    video_id = get_video_id(url_or_id)
    print(f"Detected Video ID: {video_id}")
    
    # 1. Retrieve metadata
    details = get_video_details(video_id)
    print(f"Title: {details['title']}")
    print(f"Channel/Creator: {details['channel']}")
    print(f"Date: {details['date']}")
    
    # 2. Download transcript
    transcript = get_transcript(video_id)
    if not transcript:
        print("Error: Could not retrieve transcript. Aborting workflow.")
        sys.exit(1)
    print(f"Transcript downloaded successfully. Length: {len(transcript)} characters.")
    
    # 3. Retrieve folders of existing categories in the vault
    categories = []
    if AI_ENGINEER_DIR.exists():
        raw_dir = AI_ENGINEER_DIR / "raw"
        if raw_dir.exists():
            categories = [p.name for p in raw_dir.iterdir() if p.is_dir() and p.name != "dswok"]
        
    # 4. Generate note and classify
    if manual_category:
        category = manual_category
        print(f"Manually assigned category: {category}")
        # Only call Gemini to draft the note
        prompt = f"""
Act as an expert Knowledge Architect in Obsidian and AI Engineering.
Process the following transcript of the video titled "{details['title']}" from the channel "{details['channel']}". Generate the structured note in English following the vault conventions:
- A unique H1 title.
- A blockquote with exact descriptive metadata (Author, Channel/Author, Date, Playlist, Type, Tags). It must include `Tags: #no-read-yet`.
- Section `## 📌 Key Takeaways`.
- Detailed thematic sections.
- Section `## Flashcards` (Q: Question, A: Answer).
- Section `## Glossary` (**Term**: Definition).
- Section `## Related` with suggested internal wikilinks.
- NEVER use YAML frontmatter or emojis outside Key Takeaways.

Transcript:
{transcript[:45000]}
"""
        note_content = call_gemini(prompt)
    else:
        category, note_content = generate_curated_note(details, transcript, categories)
        
    if not note_content:
        print("Error: Could not generate curated content via Gemini.")
        sys.exit(1)
        
    category = category.replace("/", "_").replace("\\", "_").strip()
    raw_folder = AI_ENGINEER_DIR / "raw" / category
    raw_folder.mkdir(parents=True, exist_ok=True)
    
    # Naming convention: Channel — Video Title
    # Clean invalid characters for filenames
    clean_title = re.sub(r'[\\/*?:"<>|]', "", details['title']).strip()
    clean_channel = re.sub(r'[\\/*?:"<>|]', "", details['channel']).strip()
    filename = f"{clean_channel} — {clean_title}.md"
    dest_file = raw_folder / filename
    
    # Write note to raw zone
    print(f"Saving curated note in the raw zone at: {dest_file}")
    dest_file.write_text(note_content, encoding="utf-8")
    
    # Extract concepts and update Wiki zone
    print("Extracting concepts for Wiki zone...")
    wiki_prompt = f"""
Act as a Knowledge Compiler. Read the following curated note:

{note_content[:15000]}

Identify 3 to 7 core concepts. For each concept, provide a brief synthesized explanation based ONLY on this text.
Format your output as a JSON object where keys are concept names (in Camel Case or Pascal Case, e.g., "AgenticWorkflows") and values are the synthesized explanations.
Do not include markdown blocks, just the raw JSON object.
"""
    wiki_response = call_gemini(wiki_prompt)
    try:
        clean_json = wiki_response.replace("```json", "").replace("```", "").strip()
        concepts = json.loads(clean_json)
        
        wiki_folder = AI_ENGINEER_DIR / "wiki"
        wiki_folder.mkdir(parents=True, exist_ok=True)
        
        for concept_name, explanation in concepts.items():
            concept_file = wiki_folder / f"{concept_name}.md"
            if concept_file.exists():
                print(f"Updating existing concept page: {concept_name}")
                existing = concept_file.read_text(encoding="utf-8")
                new_content = f"{existing}\n\n## Update from [[{filename.replace('.md', '')}]]\n{explanation}\n"
                concept_file.write_text(new_content, encoding="utf-8")
            else:
                print(f"Creating new concept page: {concept_name}")
                new_content = f"# {concept_name}\n\n{explanation}\n\n## Sources\n- [[{filename.replace('.md', '')}]]\n"
                concept_file.write_text(new_content, encoding="utf-8")
    except Exception as e:
        print(f"Failed to process concepts for wiki zone: {e}")
    
    # 5. Execute Master Plan update
    print("Updating Master Plan...")
    try:
        script_dir = Path(__file__).parent
        subprocess.run([sys.executable, str(script_dir / "update_master_plan.py")], check=True)
    except Exception as e:
        print(f"Error executing Master Plan update: {e}")
        
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print(f"Note Created: {filename}")
    print(f"Absolute Path: {dest_file}")
    print(f"Category: {category}")
    print("=" * 80)
    
    # Print a JSON to facilitate chat reporting
    report = {
        "success": True,
        "filename": filename,
        "absolute_path": str(dest_file),
        "category": category,
        "creator": details['channel'],
        "date": details['date']
    }
    print(f"REPORT_JSON: {json.dumps(report)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Headless YouTube Video Curation Workflow")
    parser.add_argument("--url", required=True, help="YouTube video URL or ID")
    parser.add_argument("--category", help="Manual category (optional)")
    args = parser.parse_args()
    
    curate_video(args.url, args.category)
