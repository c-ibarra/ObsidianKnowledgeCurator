---
name: knowledge-link
description: Use this skill when the user wants to find connections between notes, add wikilinks, discover orphaned notes, build a Map of Content (MOC), update a Master Plan, or strengthen the vault link graph. Triggers include "link these notes", "find related notes", "find orphan notes", "build an index", "create a MOC", "update Master Plan".
---

# Knowledge Link Skill

## Goal
Identify and create meaningful connections between notes — strengthening the link graph
and keeping Master Plans up to date. Uses `obsidian` CLI for all operations.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "open" || echo "CLOSED"
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

4. If confirmed, append to the note's `## Related` section:
```bash
obsidian append file="<note name>" content="\n## Related\n- [[Related Note A]]\n- [[Related Note B]]"
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
`<RootFolder>/<Category>/Master Plan — <Series>.md`

**Check if one exists first**:
```bash
obsidian search query="Master Plan <category>" limit=3
```

**If updating**, append the new note entry:
```bash
obsidian append file="Master Plan — <Series>" \
  content="\n- [[<Note Name>]] · Type · Date"
```

**If creating**, use this structure (no YAML):
```markdown
# Master Plan — <Series or Category>

> **Series/Category Index**
> Type: master-plan
> Tags: #index

## Description
<2-3 lines describing the series or category>

## Notes

### <Subsection if applicable>
- [[Note 01 — Title]] · video · Month Year
- [[Note 02 — Title]] · article · Month Year

## Related
- [[Master Plan — Related Category]]
```

```bash
obsidian create path="<RootFolder>/<Category>/Master Plan — <Series>.md" \
  content="<above structure>" silent
```

## Constraints
- Never add links without user confirmation when modifying existing notes
- Always justify each proposed connection
- Do not create wikilinks to non-existent notes
- Never touch `dswok`
- Bulk operations (>5 notes): confirm scope first

## Examples

**"Update the Claude Code Master Plan"**
```bash
obsidian search query="Master Plan Claude Code" limit=3
obsidian files folder="dataScienceKnowledgeBase/AI Engineer/Claude Code" total
# append new entries to Master Plan
```

**"Do I have orphan notes?"**
```bash
obsidian orphans total
obsidian deadends
obsidian unresolved
```
