---
name: okc-urlYoutube
description: Downloads transcript, curates source note, compiles concepts, and syncs vault.
argument-hint: <url>
---

# Youtube Video Curator Skill

When this skill is invoked via `/urlYoutube <url>`, execute the following steps:

1. **Download Video Transcript:**
   Run the terminal command:
   ```bash
   uv run python scripts/fetch_youtube_data.py --url "<url>"
   ```
2. **Process Fetched Data:**
   - **Quality Grading (Pre-Fetch Checklist)**:
     - Read `MIN_TECHNICAL_SCORE` from `.env` (default: `60`).
     - Read the first 3,000 characters of `temp/fetched_data.txt`.
     - Grade the text (0-100 score) on **Information Density**, **Provenance/References**, and **Technical Level** using your LLM.
     - If the score is below the threshold, output a detailed scorecard (Score, Criteria failed, Brief Content Summary) and ask the user: *"Do you want to proceed with curation anyway? (y/n)"*. If the user declines, abort execution.
   - Read the raw transcript from `temp/fetched_data.txt` and metadata from `temp/fetched_data.json`.
   - Generate a structured curated note in the `raw/` zone following the vault naming conventions and structure guidelines (including adding the `Processed: DD-MM-YYYY` metadata line using today's date).
   - Extract 3-7 core concepts from the video and update or create their pages in the `wiki/` zone.
   - For every file created or modified in `raw/` or `wiki/`, run:
     ```bash
     uv tool run --from graphifyy python -c "import sys; from pathlib import Path; sys.path.append(str(Path.cwd())); from scripts.graphify_helper import update_note_in_graph; update_note_in_graph(Path('/absolute/path/to/note.md'))"
     ```
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report the results and updated notes to the user.

