---
name: knowledge-link
description: Use this skill when the user wants to find connections between notes, add wikilinks, discover orphaned notes, build a Map of Content (MOC), update a Master Plan, or strengthen the vault link graph. Triggers include "link these notes", "find related notes", "find orphan notes", "build an index", "create a MOC", "update Master Plan", "conecta notas", "notas huérfanas", "crea un MOC", "actualiza el Master Plan".
---

# Knowledge Link Skill

## Goal
Identify and create meaningful connections between notes — strengthening the link graph
and keeping Master Plans up to date. Uses `obsidian` CLI for all operations.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "abierto" || echo "CERRADO"
# Read obsidian-cli skill before operating
```

**⚠️ Never touch**: `dataScienceKnowledgeBase/dswok`

## Mode A — Link a specific note to others

1. Read the target note and its existing links:
```bash
obsidian read file="<note name>"
obsidian links file="<note name>"
obsidian backlinks file="<note name>" counts
```

2. Extract 3–5 core concepts. Search for each:
```bash
obsidian search query="<concept>" limit=5
```

3. Propose new links (always state the reason):
```
Suggested links for [[Target Note]]:
- [[Related Note A]] — same concept: X
- [[Related Note B]] — continuation of idea: Y
```

4. If confirmed, append to the note's `## Relacionado` section:
```bash
obsidian append file="<note name>" content="\n## Relacionado\n- [[Related Note A]]\n- [[Related Note B]]"
```

## Mode B — Find orphan notes

```bash
obsidian orphans total    # count first
obsidian orphans          # full list
obsidian deadends         # notes with no backlinks
obsidian unresolved       # broken wikilinks
```

For each orphan, read and propose connections:
```bash
obsidian read file="<orphan name>"
obsidian search query="<core concept from orphan>" limit=5
```

Never include results from `dswok` in the orphan list.

## Mode C — Create or Update Master Plan

Master Plans are index notes for a series or category. They live at:
`dataScienceKnowledgeBase/AI Engineer/<Categoría>/Master Plan — <Serie>.md`

**Check if one exists first**:
```bash
obsidian search query="Master Plan <categoría>" limit=3
```

**If updating**, append the new note entry:
```bash
obsidian append file="Master Plan — <Serie>" \
  content="\n- [[<Nombre Nota>]] · Tipo · Fecha"
```

**If creating**, use this structure (no YAML):
```markdown
# Master Plan — <Serie o Categoría>

> **Índice de la serie/categoría**
> Tipo: master-plan
> Tags: #index

## Descripción
<2-3 líneas describiendo la serie o categoría>

## Notas

### <Subsección si aplica>
- [[Nota 01 — Título]] · video · Mes Año
- [[Nota 02 — Título]] · artículo · Mes Año

## Relacionado
- [[Master Plan — Categoría Relacionada]]
```

```bash
obsidian create path="dataScienceKnowledgeBase/AI Engineer/<Categoría>/Master Plan — <Serie>.md" \
  content="<estructura de arriba>" silent
```

## Constraints
- Never add links without user confirmation when modifying existing notes
- Always justify each proposed connection
- Do not create wikilinks to non-existent notes
- Never touch `dswok`
- Bulk operations (>5 notes): confirm scope first

## Examples

**"Actualiza el Master Plan de Claude Code"**
```bash
obsidian search query="Master Plan Claude Code" limit=3
obsidian files folder="dataScienceKnowledgeBase/AI Engineer/Claude Code" total
# append new entries to Master Plan
```

**"¿Tengo notas huérfanas?"**
```bash
obsidian orphans total
obsidian deadends
obsidian unresolved
```
