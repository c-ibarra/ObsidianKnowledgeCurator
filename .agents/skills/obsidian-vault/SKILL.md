---
name: obsidian-vault
description: Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.
---

# Obsidian Vault

## Vault location

`/mnt/d/Obsidian Vault/AI Research/`

Mostly flat at root level.

## Naming conventions

- **Index notes**: aggregate related topics (e.g., `Ralph Wiggum Index.md`, `Skills Index.md`, `RAG Index.md`)
- **Title case** for all note names
- No folders for organization - use links and index notes instead

## Linking

- Use Obsidian `[[wikilinks]]` syntax: `[[Note Title]]`
- Notes link to dependencies/related notes at the bottom
- Index notes are just lists of `[[wikilinks]]`

## Workflows

### Search for notes

```bash
# Search by filename
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "keyword"

# Search by content
grep -rl "keyword" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```

Or use Grep/Glob tools directly on the vault path.

### Create a new note

1. Use **Title Case** for filename
2. Write content as a unit of learning (per vault rules)
3. Add `[[wikilinks]]` to related notes at the bottom
4. If part of a numbered sequence, use the hierarchical numbering scheme

### Update an existing note (Safe-Merge)

If you need to update a note that already exists in the vault (e.g. to append new takeaways, flashcards, glossary terms, or paragraphs of text), do NOT overwrite the file completely. Instead:
1. Parse the existing file's text and your new update content.
2. Natively merge the sections (Key Takeaways, Flashcards, Glossary, Related, and Thematic headers) using the Python `safe_merge` helper library or by running:
   ```bash
   uv run python scripts/safe_merge.py --existing <old_path> --new <new_path> --output <output_path>
   ```
3. This ensures that user edits, highlights, and formatting are semantically preserved while new elements are cleanly appended under the correct H2 headers.

### Evaluate technical density (Technical Density Grader)

Before importing or writing a new curated note, evaluate its technical density to ensure it meets our advanced standards and doesn't introduce marketing fluff.
1. Run the technical density grader over the content snippet (first 4000 characters):
   ```bash
   uv run python scripts/density_grader.py --text "<snippet>"
   ```
2. If the score is below the threshold (e.g. `0.5`):
   - Tag the note with `#low-density` in the metadata tags block.
   - Prepend a callout block to warn the user:
     `> [!WARNING] Low Technical Density (Score: X.X/1.0)`
     `> **Grader feedback:** <explanation of the score>`
   - If `--skip-low-density` is requested, skip saving the note entirely.

### Find related notes

Search for `[[Note Title]]` across the vault to find backlinks:

```bash
grep -rl "\\[\\[Note Title\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```

### Find index notes

```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```
