---
name: note-capture
description: Use this skill when the user wants to capture a new idea, article, quote, meeting note, or any raw content into the Obsidian vault. Triggers include "capture this", "save this to my vault", "add a note about", "turn this into a note", "guarda esto", "captura esta idea", "crea una nota sobre".
---

# Note Capture Skill

## Goal
Transform raw input into a structured Obsidian note that follows the vault's conventions
exactly — no YAML, blockquote header, correct naming, correct sections — and save it to
the right folder under `dataScienceKnowledgeBase/AI Engineer/`.

## Prerequisites
```bash
# 1. Obsidian must be open
pgrep -x Obsidian > /dev/null && echo "abierto" || echo "CERRADO"

# 2. Read obsidian-cli skill before operating
```

## Step 1 — Analyze vault before acting
```bash
# Check existing folder structure
obsidian folders
obsidian files folder="dataScienceKnowledgeBase/AI Engineer" total

# Search for duplicates
obsidian search query="<core topic>" limit=5
```
If a note on the same topic already exists → update it, don't create a new one.

**⚠️ Never touch**: `dataScienceKnowledgeBase/dswok`

## Step 2 — Determine note type and target path

| Input type | Naming pattern | Target folder |
|-----------|---------------|--------------|
| YouTube video (series) | `Serie ## — Título.md` | `AI Engineer/<Categoría>/` |
| YouTube video (standalone) | `Canal — Título del Video.md` | `AI Engineer/<Categoría>/` |
| Article / web | `Publicación — Título.md` | `AI Engineer/<Categoría>/` |
| Raw idea / concept | `Concept — Título descriptivo.md` | `AI Engineer/<Categoría>/` |
| Master plan | `Master Plan — Nombre Serie.md` | `AI Engineer/<Categoría>/` |

## Step 3 — Build note structure (no YAML, ever)

```markdown
# Título Descriptivo

> **Autor — Título Descriptivo**
> Fuente: Descripción de la fuente
> Canal/Autor: Nombre · Fecha: Mes Año
> Tipo: artículo | video | análisis
> Tags: #no-read-yet

## 📌 Key Takeaways
1. ...
2. ...
3. ...

## 1. Sección Temática
...

## 2. Sección Temática
...

## Flashcards
P: Pregunta
R: Respuesta

## Glosario
**Término**: Definición (solo técnicos no obvios)

## Relacionado
- [[Nota existente en el vault]]
```

## Step 4 — Validate with `superpowers` before writing
- [ ] Sin YAML frontmatter
- [ ] Blockquote de cabecera con `Tags: #no-read-yet`
- [ ] Nombre de archivo sigue el naming convention
- [ ] `[[enlaces]]` en Relacionado existen en el vault
- [ ] Sin contenido inventado
- [ ] Categoría coherente con el vault

## Step 5 — Write to vault
```bash
# Create new note
obsidian create path="dataScienceKnowledgeBase/AI Engineer/<Categoría>/<Nombre Nota>.md" \
  content="<contenido>" silent

# Verify
obsidian read file="<Nombre Nota>"
```

After saving, update or create the category's Master Plan:
```bash
obsidian search query="Master Plan <Categoría>" limit=3
# append note link to existing Master Plan, or create one
```

## Constraints
- Never use YAML frontmatter
- Never use emojis outside of `## 📌 Key Takeaways`
- Never touch `dataScienceKnowledgeBase/dswok`
- Never invent content — mark unavailable info as `[NO DISPONIBLE]`
- Always check for duplicates before creating

## Example

**Input**: "Captura esta idea: los agentes de IA son mejores con memoria externa"

1. Search: `obsidian search query="agentes IA memoria" limit=5`
2. No duplicates found → create new note
3. Target: `dataScienceKnowledgeBase/AI Engineer/Agentes/Concept — Agentes IA Memoria Externa.md`
4. Validate → write → verify → update Master Plan if exists
