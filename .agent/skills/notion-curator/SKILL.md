---
name: notion-curator
description: Use this skill when the user wants to curate, import, or migrate folders or files imported from Notion into the structured zones (raw and wiki) of the Obsidian vault. Triggers include "import Notion folder", "curate Notion imported files", "procesar nuevo material de Notion", "migrar carpeta Notion", "curar importación de Notion".
---

# Notion Curator Skill

## Goal
Natively read, reformat, and migrate imported Notion markdown files into the structured vault zones (`raw/` and `wiki/`) completely **keylessly** using native cognitive context and **without triggering authorization prompts** by utilizing native file tools.

## Prerequisites
- **Vault Directory Permissions:** Ensure the agent has read/write permission to the Obsidian folder.
- **Avoid shell commands:** Never use shell commands (`find`, `mkdir`, `mv`, `cat`) since they always trigger manual user approval prompts. Use native `view_file` and `write_to_file` tools.

## Step 1 — Scan source folder
Read the contents of the target Notion directory to locate imported markdown files:
```bash
# Check files inside target Notion directory
# (Use native file listing/view tools if available, or a single non-interactive file-read check)
```

## Step 2 — Process and Curate notes (Zero-YAML Spanish Standard)
For each file in the Notion folder:
1. **Read original note:** Use native `view_file` to read the content keylessly.
2. **Reformat to zero-YAML standard:** Use the cognitive LLM context to convert it:
   - **H1 Title** in Spanish at the top.
   - **Metadata blockquote (Zero-YAML):**
     ```markdown
     > **Fuente:** Curso Notion
     > **Autor:** Carlos Ibarra · **Fecha:** Mayo 2026
     > **Tipo:** nota de curso
     > **Tags:** #no-read-yet
     ```
   - **Key Takeaways section** (`## 📌 Key Takeaways`) in Spanish with bullet points and emojis.
   - **Technical body** in Spanish with structured headers (## 1. Tema, ## 2. ...), preserving code blocks.
   - **Flashcards section** (`## Flashcards`) in Spanish: `1. **P:** [Pregunta]? → **R:** [Respuesta]`.
   - **Glossary section** (`## Glosario`) in Spanish: `- **[Término]**: [Definición]`.
   - **Related section** (`## Relacionado`) with suggested wikilinks.
3. **Write curated note:** Save it under `dataScienceKnowledgeBase/Machine Learning/raw/<Course Name>/<Section>/<Note Name>.md` using native `write_to_file`.

## Step 3 — Compile concepts natively (Wiki)
For each processed note:
1. Extract 3–5 core concepts using your cognitive LLM context.
2. Create or update files under `dataScienceKnowledgeBase/Machine Learning/wiki/<ConceptName>.md` (PascalCase, e.g. `TargetEncoding`) using `write_to_file`.
3. Include deep Spanish synthesis and a `Fuentes` backlink section pointing to the raw note.

## Step 4 — Update Master Plan
1. Parse the metadata of all curated raw notes.
2. Edit `/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian/dataScienceKnowledgeBase/Machine Learning/Master Plan — Machine Learning.md` directly using `replace_file_content` to rebuild its index table.

## Step 5 — Move Original Files
Move the original Notion file to a `processed/` directory:
- Since moving files normally requires a shell command, batch the move operations or perform a native write of the file in the new location and delete the original using native tools, or request a single batch command approval at the end.

## Constraints
- NEVER use YAML frontmatter.
- NEVER use emojis outside of `## 📌 Key Takeaways`.
- Maintain strict Spanish language for course content.
- Use native filesystem tools exclusively to prevent authorization prompts.
