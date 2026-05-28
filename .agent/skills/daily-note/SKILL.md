---
name: daily-note
description: Use this skill when the user wants to create, update, or review their daily note. Triggers include "create today's daily note", "update my daily note", "add to today's note", "log this to today", "nota diaria", "agrega al daily", "loguea esto hoy", "qué tengo en el daily de hoy".
---

# Daily Note Skill

## Goal
Create or update the user's daily note using `obsidian daily:*` CLI commands.
The daily note follows the vault's conventions: no YAML, no emojis (except 📌 if needed).

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "abierto" || echo "CERRADO"
# Read obsidian-cli skill before operating
```

## Step 1 — Check today's daily note
```bash
obsidian daily:read
obsidian daily:path
```
- Content returned → note exists → go to Step 3 (update)
- Empty / error → note doesn't exist → go to Step 2 (create)

## Step 2 — Create daily note

Check for templates first:
```bash
obsidian templates
```

If a Daily Note template exists → let Obsidian create it:
```bash
obsidian daily
```

If no template, create with minimal structure (no YAML, no frontmatter):
```bash
obsidian daily:append content="# $(date +%Y-%m-%d)\n\n## Foco del día\n- \n\n## Log\n\n## Ideas\n- \n\n## Notas creadas hoy\n- \n\n## Revisión\n- ¿Qué salió bien?\n- ¿Qué mejorar?"
```

## Step 3 — Handle update requests

| User intent | Command |
|------------|---------|
| Entrada de log | `obsidian daily:append content="**HH:MM** — <contenido>"` |
| Tarea / todo | `obsidian daily:append content="- [ ] <tarea>"` |
| Idea | `obsidian daily:append content="- <idea>"` |
| Nota creada | `obsidian daily:append content="- [[<Título de Nota>]]"` |
| Prioridad al inicio | `obsidian daily:prepend content="## Top Prioridad\n- <item>"` |

## Step 4 — Confirm
After any create/update, confirm what was added.
Offer to open: `obsidian daily` (opens in UI).

## Constraints
- Never overwrite the daily note — always append or prepend
- No YAML frontmatter in daily notes
- Timestamps in 24h format: `14:32`
- If user has Templater configured, use `obsidian daily` to let Obsidian handle template insertion

## Examples

**"Crea el daily note de hoy"**
```bash
obsidian daily:read   # check existence
obsidian daily        # create/open via Obsidian's template
```

**"Loguea: terminé la integración con la API de Claude"**
```bash
obsidian daily:append content="**14:35** — Terminé la integración con la API de Claude"
```

**"Agrega tarea: revisar la nota de LangGraph"**
```bash
obsidian daily:append content="- [ ] Revisar [[MCP 03 — Agentic AI With LangGraph]]"
```
