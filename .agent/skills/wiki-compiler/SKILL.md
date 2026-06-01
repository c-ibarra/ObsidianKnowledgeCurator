---
name: wiki-compiler
description: Use this skill when the user wants to compile, extract, or batch-process technical concepts from raw curated notes and write/update them in the central wiki of the Obsidian vault. Triggers include "compile vault wiki", "run wiki extractor", "extraer conceptos de notas", "compilar wiki de obsidian", "batch extract concepts".
---

# Wiki Compiler Skill

## Goal
Natively scan raw curated notes, extract their fundamental technical concepts using cognitive reasoning, compile and write/update them as individual atomic notes in the central `wiki/` directory **keylessly** and **prompt-free** using native file tools, maintaining a progress cache.

## Prerequisites
- **Obsidian Vault Directory Permissions:** Recursively authorized.
- **Strictly use native tools:** Never shell out to terminal commands. Use native file tools.

## Step 1 — Load Progress Cache
Natively check for the existence of `temp/wiki_extraction_cache.json`:
1. **If file exists:** Read its contents using `view_file` to determine which raw notes have already been successfully compiled.
2. **If file does not exist:** Initialize an empty cache mapping.

## Step 2 — Scan Raw Notes
Recursively search and list all `.md` files in the `raw/` folders of your vault categories (e.g. `dataScienceKnowledgeBase/AI Engineer/raw` or `dataScienceKnowledgeBase/Machine Learning/raw`):
- Filter out any files that have already been compiled according to the progress cache.
- Display a summary of pending files to process.

## Step 3 — Compile Concepts Natively
For each pending raw note:
1. **Read note content:** Use `view_file` to inspect the note's text.
2. **Extract Technical Concepts:** Use your cognitive LLM context to identify 3–5 core concepts. For each, synthesize a deep, high-quality explanation in Spanish based ONLY on the text.
3. **Format Concept Mapping:** Structure the concepts in Spanish with their respective technical names (PascalCase, e.g., `TargetEncoding`, `MiceImputation`).

## Step 4 — Write and Update Wiki Pages
For each extracted concept:
1. **Define target path:** `dataScienceKnowledgeBase/Machine Learning/wiki/<ConceptName>.md` (or AI Engineer equivalent).
2. **If concept file exists:** Read its contents. If the source note is not yet listed, append the new explanation under a clean header:
   ```markdown
   ## Actualización desde [[<Source Note Name>]]
   <Explanation>
   ```
3. **If concept file does not exist:** Create a fresh concept page:
   ```markdown
   # <ConceptName>
   
   <Explanation>
   
   ## Fuentes
   - [[<Source Note Name>]]
   ```
   Save the note using `write_to_file`.

## Step 5 — Update Cache
After successfully processing a raw note, add its file name to `temp/wiki_extraction_cache.json` and save the cache file using `write_to_file` to ensure incremental safety.
