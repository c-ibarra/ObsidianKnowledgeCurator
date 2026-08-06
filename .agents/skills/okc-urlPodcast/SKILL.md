---
name: okc-urlPodcast
description: Ingests a podcast episode or audio link, transcribes audio using Buzz CLI (Whisper), maps Graphify context, curates raw note, and syncs vault.
argument-hint: <url>
---

# Podcast & Audio Curator Skill

When this skill is invoked via `/okc-urlPodcast <url>`, execute the following steps:

1. **Fetch and Transcribe Podcast Audio:**
   - Execute the following command in the workspace to download and transcribe audio locally:
     ```bash
     uv run python scripts/fetch_podcast_data.py --url "<url>"
     ```
   - Once completed, read the metadata and full transcript from:
     - JSON metadata: `temp/fetched_data.json`
     - Clean text: `temp/fetched_data.txt`

2. **Process Podcast Data & Graphify Context:**
   - Read the pre-calculated `graphify_context` in `temp/fetched_data.json` to get `suggested_category` and `existing_wiki_concepts`.
   - Format the podcast content into a structured markdown note in the designated `raw/` zone following vault conventions (H1, blockquote header, key takeaways, thematic sections, flashcards, glossary, related links).
   - Update or create concept pages in `wiki/` using `existing_wiki_concepts` to avoid duplicates.

3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report progress and display modified notes to the user.
