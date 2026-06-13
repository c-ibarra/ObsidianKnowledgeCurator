---
name: master-plan-builder
description: Use this skill when the user wants to compile, rebuild, or update the logical Master Plan index files of their Obsidian vault categories (such as AI Engineer or Machine Learning). Triggers include "update master plan", "rebuild master plan", "actualizar master plan", "regenerar mapa de navegacion", "reconstruir indice de notas".
---

# Master Plan Builder Skill

## Goal
Natively read curated notes in the `raw/` directories, extract their metadata (Author, Date, Type, Category), and dynamically rebuild or update the navigation index table inside the respective `Master Plan — <Category>.md` file **keylessly** and **prompt-free** using native file tools.

## Prerequisites
- **Vault Directory Permissions:** Recursively authorized.
- **Strictly use native tools:** Never shell out to terminal commands. Use native file tools.

## Step 1 — Scan Curated Raw Notes
Search and list all `.md` files in the `raw/` folder of the target category recursively (e.g. `dataScienceKnowledgeBase/AI Engineer/raw` or `software engineer/raw`):
- Ignore other Master Plans, outlines, or temporary files.

## Step 2 — Parse Note Metadata (Zero-YAML Blockquotes)
For each note:
1. **Read note content:** Use `view_file` to inspect the contents.
2. **Parse Title:** Extract the unique H1 title from the first line.
3. **Parse Blockquote Metadata:** Locate the blockquote directly under the H1 title and extract:
   - **Channel/Author:** From fields like `Channel/Author`, `Canal/Autor`, `Author`, `Autor`. Clean up formatting.
   - **Date/Published:** From `Published`, `Publicado`, `Date`, `Fecha`.
   - **Content Type:** From `Type`, `Tipo`.
   - **Category:** Determined from the relative path under the `raw/` zone (e.g. `raw/Feature Engineering for Machine Learning/Section-08`).

## Step 3 — Generate Index Table
Format the note metadata into a beautifully structured Markdown table.
For example, for Machine Learning:
```markdown
| Note / Link | Author | Date | Type | Section / Category |
| --- | --- | --- | --- | --- |
| [[FEML - 25 - Categorical Encoding Introduction]] | Carlos Ibarra | May 2026 | course note | raw/Feature Engineering for Machine Learning/Section-08 — Categorical Encoding Basic |
```

## Step 4 — Write to Master Plan File
Locate the Master Plan file (e.g., `dataScienceKnowledgeBase/Machine Learning/Master Plan — Machine Learning.md`):
1. **If file does not exist:** Create a fresh Master Plan note using the vault's standard template (H1, Description, Notes table, Themes covered, and Related links).
2. **If file exists:** Read its contents and replace the table section dynamically between the `## Notes in this category` header and the next section separator `---`. Use `replace_file_content` to execute this update silently.

## Step 5 — Verify Changes
Natively read the updated Master Plan file to verify that all links are clickable, format is clean, and indices are aligned.
