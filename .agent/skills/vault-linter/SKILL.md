---
name: vault-linter
description: Use this skill when the user wants to audit, lint, or check the health of their Obsidian vault, including broken wikilinks, orphan notes, or contradictions. Triggers include "run vault linter", "check vault health", "auditar mi vault", "revisar enlaces rotos", "buscar notas huerfanas", "linter de obsidian".
---

# Vault Linter Skill

## Goal
Natively audit the Obsidian Vault directory (e.g. `dataScienceKnowledgeBase/AI Engineer` or `software engineer`) to verify link integrity, detect orphan notes, identify dead links, and locate contradictions **keylessly** and **silently** without manual prompt popups.

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
Synthesize the audit results into a beautiful, concise markdown report:
```markdown
# Vault Audit Report — <Date>

## 📊 Health Summary
- **Total Notes Analyzed:** <Count>
- **Broken Links Detected:** <Count>
- **Orphan Notes Identified:** <Count>
- **Contradictions Found:** <Count>

---

## ⚠️ Dead Links
- **[[Broken Link]]** (referenced in: [[Source Note A]], [[Source Note B]])

---

## 🗺️ Orphan Notes
- [[Orphan Note A]]
- [[Orphan Note B]]

---

## 🚫 Contradictions Detected
- In **[[Note X]]** (Line <Line>): <Contradiction text>
```

Present this report directly to the user and suggest specific refactoring actions (fixing dead links, linking orphans, or resolving contradictions).
