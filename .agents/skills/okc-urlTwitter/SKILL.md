---
name: okc-urlTwitter
description: Ingests a Twitter/X post or video, extracts audio/text via yt-dlp & Buzz CLI Whisper, curates source note, compiles concepts, and syncs vault.
argument-hint: <url>
---

# Twitter/X Post & Video Curator Skill

When this skill is invoked via `/urlTwitter <url>` or `/okc-urlTwitter <url>`, execute the following steps:

1. **Download Twitter/X Content & Audio Transcription:**
   Run the terminal command:
   ```bash
   uv run python scripts/fetch_twitter_data.py --url "<url>"
   ```
2. **Process Fetched Data:**
   - **Quality Grading (Pre-Fetch Checklist)**:
     - Read `MIN_TECHNICAL_SCORE` from `.env` (default: `60`).
     - Read the first 3,000 characters of `temp/fetched_data.txt`.
     - Grade the text (0-100 score) on **Information Density**, **Provenance/References**, and **Technical Level** using your LLM.
     - If the score is below the threshold, output a detailed scorecard (Score, Criteria failed, Brief Content Summary) and ask the user: *"Do you want to proceed with curation anyway? (y/n)"*. If the user declines, abort execution.
   - Read the metadata from `temp/fetched_data.json` and clean text / transcript from `temp/fetched_data.txt`.
   - Generate a structured curated note in the `raw/` zone following vault conventions (no YAML, H1 title, author blockquote, `Processed: DD-MM-YYYY` metadata line using today's date). Include a `mermaid` sequence or architecture diagram if the post/video covers multi-step workflows.
   - Extract 3-7 core concepts, verify if they exist using search tools, and update/create their pages in `wiki/`.
   - For every file created or modified in `raw/` or `wiki/`, run:
     ```bash
     uv tool run --from graphifyy python -c "import sys; from pathlib import Path; sys.path.append(str(Path.cwd())); from scripts.graphify_helper import update_note_in_graph; update_note_in_graph(Path('/absolute/path/to/note.md'))"
     ```
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report results and list updated notes to the user.

