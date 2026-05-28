---
name: note-review
description: Use this skill when the user wants to review, improve, audit, or clean up notes in their vault. Triggers include "review this note", "improve my note on", "audit my vault", "find stale notes", "vault health check", "revisa esta nota", "mejora mis notas", "audita el vault", "health check del vault", "notas desactualizadas".
---

# Note Review Skill

## Goal
Audit one or more notes (or the full vault) for quality issues and propose targeted
improvements — using `obsidian` CLI for all operations.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "abierto" || echo "CERRADO"
# Read obsidian-cli skill before operating
```

**⚠️ Always exclude from any audit**: `dataScienceKnowledgeBase/dswok`

## Mode A — Review a single note

1. Gather all info:
```bash
obsidian read file="<note name>"
obsidian links file="<note name>"
obsidian backlinks file="<note name>" counts
obsidian wordcount file="<note name>"
```

2. Evaluate against vault quality checklist:
- [ ] Título H1 claro y específico (no "Untitled")
- [ ] Blockquote de cabecera presente con todos los campos
- [ ] `Tags: #no-read-yet` en el blockquote (o tag actualizado)
- [ ] Sin YAML frontmatter
- [ ] Sección `## 📌 Key Takeaways` presente
- [ ] Al menos un `[[wikilink]]` saliente
- [ ] Sección `## Relacionado` presente
- [ ] Sin emojis fuera de `## 📌 Key Takeaways`
- [ ] Nombre de archivo sigue la naming convention
- [ ] Contenido sustancial (>3 oraciones reales)

3. Present review report:
```
📋 Revisión: [[Nombre de la Nota]]

✅ Bien:
- Estructura correcta y título claro

⚠️ Issues:
- Sin blockquote de cabecera
- Sin wikilinks salientes — nota aislada
- Nombre de archivo no sigue el naming convention

✏️ Cambios sugeridos:
1. Agregar blockquote de cabecera con Tags: #no-read-yet
2. Agregar en Relacionado: [[Nota X]], [[Nota Y]]
3. Renombrar a: "Canal — Título del Video.md"

¿Aplicar? [Todo / Seleccionar / Omitir]
```

4. If approved, apply:
```bash
obsidian prepend file="<name>" content="> **Autor — Título**\n> Fuente: ...\n> Tipo: video\n> Tags: #no-read-yet\n"
obsidian append file="<name>" content="\n## Relacionado\n- [[Nota X]]"
obsidian rename file="<old name>" name="<new name>"  # preserves backlinks
```

## Mode B — Find stale notes

```bash
obsidian search query="#no-read-yet" limit=30
obsidian recents limit=20
```
Cross-reference: notes with `#no-read-yet` that haven't appeared in recents = likely stale.

Present sorted by estimated age. For each, offer:
- "¿Desarrollar esta nota?" → open and expand
- "¿Archivar?" → `obsidian move file="<name>" folder="_archive"`
- "Omitir"

## Mode C — Vault health check

Run diagnostics (excluding `dswok`):
```bash
obsidian orphans total        # notas sin ningún enlace
obsidian unresolved           # wikilinks rotos
obsidian deadends             # notas sin backlinks
obsidian tags total           # taxonomía de tags
obsidian files folder="dataScienceKnowledgeBase/AI Engineer" total
```

Report format:
```
🏥 Vault Health Report

📁 Notas en AI Engineer: X
🔗 Notas huérfanas: X (sin enlaces entrantes ni salientes)
🔴 Wikilinks rotos: X
⬛ Notas sin backlinks: X
🏷️ Tags únicos: X

Recomendaciones:
1. Revisar X notas huérfanas — enlazar o archivar
2. Corregir X wikilinks rotos
3. [si hay muchos tags] Consolidar taxonomía
```

Offer to address each category one at a time.

## Constraints
- Never auto-apply bulk edits — always get confirmation
- Never use `obsidian delete` — use `obsidian move folder="_archive"` instead
- Never touch `dataScienceKnowledgeBase/dswok`
- Skip `_archive/` folder in all audits
- Rename with `obsidian rename` (not file system mv) — preserves backlinks

## Examples

**"Revisa la nota de Claude Code CLI"**
```bash
obsidian read file="Claude Code CLI"
obsidian links file="Claude Code CLI"
obsidian backlinks file="Claude Code CLI" counts
obsidian wordcount file="Claude Code CLI"
# → report → user approves → apply fixes
```

**"Health check del vault"**
```bash
obsidian orphans total
obsidian unresolved
obsidian deadends
obsidian tags total
# → present report → offer to fix per category
```
