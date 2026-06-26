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
   - Read the raw transcript from `temp/fetched_data.txt` and metadata from `temp/fetched_data.json`.
   - Generate a structured curated note in the `raw/` zone following the vault naming conventions and structure guidelines.
   - Extract 3-7 core concepts from the video and update or create their pages in the `wiki/` zone.
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report the results and updated notes to the user.
