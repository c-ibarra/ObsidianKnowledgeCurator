---
name: okc-find
description: Performs a fast, case-insensitive note-name substring search.
argument-hint: <query>
---

# Fast Find Skill

When this skill is invoked via `/find <query>`, execute the following steps:

1. **Run Find Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/knowledge_commands.py --find "<query>"
   ```
2. **Present Results:**
   - Present the matching note names as clickable Obsidian wikilinks.
