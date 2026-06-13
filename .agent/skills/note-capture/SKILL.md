---
name: note-capture
description: Use this skill when the user wants to capture a new idea, article, quote, meeting note, or any raw content into the Obsidian vault. Triggers include "capture this", "save this to my vault", "add a note about", "turn this into a note", "guarda esto", "captura esta idea", "crea una nota sobre".
---

# Note Capture Skill

## Goal
Transform raw input into a structured Obsidian note that follows the vault's conventions
exactly — no YAML, blockquote header, correct naming, correct sections — and save it to
the right folder under the appropriate `<RootFolder>`.

## Prerequisites
```bash
# 1. Obsidian must be open
pgrep -x Obsidian > /dev/null && echo "open" || echo "CLOSED"

# 2. Read obsidian-cli skill before operating
```

## Step 1 — Analyze vault before acting
```bash
# Check existing folder structure
obsidian folders
obsidian files folder="<RootFolder>" total

# Search for duplicates
obsidian search query="<core topic>" limit=5
```
If a note on the same topic already exists → update it, don't create a new one.

**⚠️ Never touch**: `dataScienceKnowledgeBase/dswok`

## Step 2 — Determine note type and target path

| Input type | Naming pattern | Target folder |
|-----------|---------------|--------------|
| YouTube video (series) | `Series ## — Title.md` | `<RootFolder>/<Category>/` |
| YouTube video (standalone) | `Channel — Video Title.md` | `<RootFolder>/<Category>/` |
| Article / web | `Publication — Title.md` | `<RootFolder>/<Category>/` |
| Raw idea / concept | `Concept — Descriptive Title.md` | `<RootFolder>/<Category>/` |
| Master plan | `Master Plan — Series Name.md` | `<RootFolder>/<Category>/` |

## Step 3 — Build note structure (no YAML, ever)

```markdown
# Descriptive Title

> **Author — Descriptive Title**
> Source: Source description
> Channel/Author: Name · Date: Month Year
> Type: article | video | analysis
> Tags: #no-read-yet

## 📌 Key Takeaways
1. ...
2. ...
3. ...

## 1. Thematic Section
...

## 2. Thematic Section
...

## Flashcards
Q: Question
A: Answer

## Glossary
**Term**: Definition (only non-obvious technical terms)

## Related
- [[Existing note in the vault]]
```

## Step 4 — Validate with `superpowers` before writing
- [ ] No YAML frontmatter
- [ ] Header blockquote with `Tags: #no-read-yet`
- [ ] File name follows the naming convention
- [ ] `[[links]]` in Related exist in the vault
- [ ] No hallucinated content
- [ ] Category is consistent with the vault

## Step 5 — Write to vault
```bash
# Create new note
obsidian create path="<RootFolder>/<Category>/<Note Name>.md" \
  content="<content>" silent

# Verify
obsidian read file="<Note Name>"
```

After saving, update or create the category's Master Plan:
```bash
obsidian search query="Master Plan <Category>" limit=3
# append note link to existing Master Plan, or create one
```

## Constraints
- Never use YAML frontmatter
- Never use emojis outside of `## 📌 Key Takeaways`
- Never touch `dataScienceKnowledgeBase/dswok`
- Never invent content — mark unavailable info as `[NOT AVAILABLE]`
- Always check for duplicates before creating

## Example

**Input**: "Capture this idea: AI agents are better with external memory"

1. Search: `obsidian search query="AI agents memory" limit=5`
2. No duplicates found → create new note
3. Target: `dataScienceKnowledgeBase/AI Engineer/Agents/Concept — AI Agents External Memory.md`
4. Validate → write → verify → update Master Plan if exists
