---
name: okc-normalize
description: Audits, deduplicates, removes stubs, and injects canonical Obsidian headers into notes.
---

# OKC Note Normalizer & Import Sanitizer Skill

Use this skill when the user wants to audit, sanitize, deduplicate, or normalize imported notes, book chapters, or categories in their Obsidian vault.

Triggers include:
- `/okc-normalize`
- "normalize notes"
- "sanitize imported notes"
- "check for duplicate notes"
- "fix missing headers"

## Workflow

1. **Audit / Dry-Run Mode:**
   To check for missing headers, duplicate notes (by content hash), and empty stubs without modifying files:
   ```bash
   uv run python scripts/normalize_notes.py --target "<relative_or_absolute_folder_path>" --dry-run
   ```

2. **Execute Fixes & Safe Archiving:**
   To apply canonical headers, move exact duplicates and stubs into `_archive/`, and atomically sync the database:
   ```bash
   uv run python scripts/normalize_notes.py --target "<relative_or_absolute_folder_path>" --fix --sync
   ```

3. **Report to User:**
   - Summarize canonical notes, normalized notes, archived duplicates, and cleaned stubs.
   - Confirm that SQLite index and category Master Plans were atomically updated.
