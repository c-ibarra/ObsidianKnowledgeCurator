---
name: vault-linter
description: Use this skill when the user wants to audit, lint, or check the health of their Obsidian vault, including broken wikilinks, orphan notes, or contradictions. Triggers include "run vault linter", "check vault health", "auditar mi vault", "revisar enlaces rotos", "buscar notas huerfanas", "linter de obsidian".
---

# Vault Linter Skill

## Goal
Natively audit the Obsidian Vault directory (`dataScienceKnowledgeBase/AI Engineer` or `dataScienceKnowledgeBase/Machine Learning`) to verify link integrity, detect orphan notes, identify dead links, and locate contradictions **keylessly** and **silently** without manual prompt popups.

## Prerequisites
- **Obsidian Vault Directory Permissions:** Recursively granted for native tools.
- **Strictly use native tools:** Never shell out to terminal commands. Use native file tools to read files and directories.

## Step 1 — Walk Vault Directories
Search for and list all markdown (`.md`) files in the vault zone recursively (excluding `dswok/` and hidden folders):
- Identify files and read their contents.

## Step 2 — Parse Note Content
For each note:
1. **Read note content:** Use `view_file` to inspect the contents.
2. **Extract outgoing wikilinks:** Scan the text for `[[link]]` or `[[link|alias]]` patterns.
   - Clean the link target by stripping aliases (e.g. `link|alias` -> `link`) and section anchors (e.g. `link#header` -> `link`).
3. **Detect contradictions:** Scan for the `> [!contradiction]` blockquote callout. If found, record the file name, line number, and the contradiction text.

## Step 3 — Analyze Link Integrity (Graph)
Map the complete backlinks graph:
1. **Dead Links:** Identify targets in your outgoing links list that do not exist as actual markdown files in the vault.
2. **Orphan Notes:** Locate notes that have **0 incoming links** and **0 outgoing links** (excluding the Category Master Plan files which act as index hubs).

## Step 4 — Generate Health Check Report
Synthesize the audit results into a beautiful, concise markdown report in Spanish:
```markdown
# Reporte de Auditoría del Vault — <Fecha>

## 📊 Resumen de Salud
- **Total de Notas Analizadas:** <Count>
- **Enlaces Rotos Detectados:** <Count>
- **Notas Huérfanas Identificadas:** <Count>
- **Contradicciones Encontradas:** <Count>

---

## ⚠️ Enlaces Rotos (Dead Links)
- **[[Enlace Roto]]** (referenciado en: [[Nota Origen A]], [[Nota Origen B]])

---

## 🗺️ Notas Huérfanas (Orphans)
- [[Nota Huérfana A]]
- [[Nota Huérfana B]]

---

## 🚫 Contradicciones Detectadas
- En **[[Nota X]]** (Línea <Línea>): <Texto de la contradicción>
```

Present this report directly to the user and suggest specific refactoring actions (fixing dead links, linking orphans, or resolving contradictions).
