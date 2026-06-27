---
name: okc-urlArticle
description: Fetches content from an article or web page, curates it, and syncs the vault.
argument-hint: <url>
---

# Web Article Curator Skill

When this skill is invoked via `/urlArticle <url>`, execute the following steps:

1. **Fetch Article Content:**
   - Attempt to read the page content using `read_url_content`.
   - If that fails or is blocked (e.g., by robots.txt), launch the browser subagent (`browser_subagent`) to fetch the main text of the article securely.
2. **Process Article Data:**
   - Summarize and format the content into a structured markdown note in the `raw/` zone following the vault conventions (no YAML, with H1, author blockquote, and adding the `Processed: DD-MM-YYYY` or `Procesado: DD-MM-YYYY` metadata line using today's date).
   - Identify 3-7 core concepts, check if they exist using search tools, and update/create their wiki files in the `wiki/` zone.
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report progress and show the modified notes to the user.
