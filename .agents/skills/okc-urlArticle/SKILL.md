---
name: okc-urlArticle
description: Fetches content from an article or web page, curates it, and syncs the vault.
argument-hint: <url>
---

# Web Article Curator Skill

When this skill is invoked via `/urlArticle <url>`, execute the following steps:

1. **Fetch Article Content:**
   - Execute the following command in the workspace to fetch the article content dynamically or statically:
     ```bash
     uv run python scripts/fetch_article_data.py --url "<url>"
     ```
   - Once completed, read the metadata and full clean transcript from:
     - JSON metadata: `temp/fetched_data.json`
     - Clean text: `temp/fetched_data.txt`
2. **Process Article Data:**
   - **Quality Grading (Pre-Fetch Checklist)**:
     - Read `MIN_TECHNICAL_SCORE` from `.env` (default: `60`).
     - Read the first 3,000 characters of `temp/fetched_data.txt`.
     - Grade the text (0-100 score) on **Information Density**, **Provenance/References**, and **Technical Level** using your LLM.
     - If the score is below the threshold, output a detailed scorecard (Score, Criteria failed, Brief Content Summary) and ask the user: *"Do you want to proceed with curation anyway? (y/n)"*. If the user declines, abort execution.
   - Summarize and format the content into a structured markdown note in the `raw/` zone following the vault conventions (no YAML, with H1, author blockquote, and adding the `Processed: DD-MM-YYYY` metadata line using today's date).
   - **Mandatory Image Preservation & Local Downloading**: You MUST preserve ALL images, diagrams, flowcharts, and graphics present in the source article. Download every image into `<VAULT_ROOT>/assets/images/<slug>-img-<idx>.<ext>` and embed it locally in the note using native Obsidian wikilink syntax: `![[assets/images/<slug>-img-<idx>.<ext>]]`. Never omit source images or rely on fragile external URLs.
   - Identify 3-7 core concepts, check if they exist, and update/create their wiki files in the `wiki/` zone.
   - For every file created or modified in `raw/` or `wiki/`, run:
     ```bash
     uv tool run --from graphifyy python -c "import sys; from pathlib import Path; sys.path.append(str(Path.cwd())); from scripts.graphify_helper import update_note_in_graph; update_note_in_graph(Path('/absolute/path/to/note.md'))"
     ```
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report progress and show the modified notes to the user.

