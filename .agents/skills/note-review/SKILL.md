---
name: note-review
description: Use this skill when the user wants to review, improve, audit, or clean up notes in their vault. Triggers include "review this note", "improve my note on", "audit my vault", "find stale notes", "vault health check".
---

# Note Review Skill

## Goal
Audit one or more notes (or the full vault) for quality issues and propose targeted
improvements — using `obsidian` CLI for all operations.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "open" || echo "CLOSED"
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
- [ ] Clear and specific H1 title (not "Untitled")
- [ ] Header blockquote present with all fields
- [ ] `Tags: #no-read-yet` in blockquote (or updated tag)
- [ ] No YAML frontmatter
- [ ] `## 📌 Key Takeaways` section present
- [ ] At least one outgoing `[[wikilink]]`
- [ ] `## Related` section present
- [ ] No emojis outside of `## 📌 Key Takeaways`
- [ ] File name follows naming convention
- [ ] Substantial content (>3 real sentences)

3. Present review report:
```
📋 Review: [[Note Name]]

✅ Good:
- Correct structure and clear title

⚠️ Issues:
- Missing header blockquote
- No outgoing wikilinks — isolated note
- File name doesn't follow naming convention

✏️ Suggested changes:
1. Add header blockquote with Tags: #no-read-yet
2. Add to Related: [[Note X]], [[Note Y]]
3. Rename to: "Channel — Video Title.md"

Apply? [All / Select / Skip]
```

4. If approved, apply:
```bash
obsidian prepend file="<name>" content="> **Author — Title**\n> Source: ...\n> Type: video\n> Tags: #no-read-yet\n"
obsidian append file="<name>" content="\n## Related\n- [[Note X]]"
obsidian rename file="<old name>" name="<new name>"  # preserves backlinks
```

## Mode B — Find stale notes

```bash
obsidian search query="#no-read-yet" limit=30
obsidian recents limit=20
```
Cross-reference: notes with `#no-read-yet` that haven't appeared in recents = likely stale.

Present sorted by estimated age. For each, offer:
- "Expand this note?" → open and expand
- "Archive?" → `obsidian move file="<name>" folder="_archive"`
- "Skip"

## Mode C — Vault health check

Run diagnostics (excluding `dswok`):
```bash
obsidian orphans total        # notes without any links
obsidian unresolved           # broken wikilinks
obsidian deadends             # notes without backlinks
obsidian tags total           # tag taxonomy
obsidian files folder="<RootFolder>" total
```

Report format:
```
🏥 Vault Health Report

📁 Notes in RootFolder: X
🔗 Orphan notes: X (no incoming or outgoing links)
🔴 Broken wikilinks: X
⬛ Notes without backlinks: X
🏷️ Unique tags: X

Recommendations:
1. Review X orphan notes — link or archive
2. Fix X broken wikilinks
3. [if many tags] Consolidate taxonomy
```

Offer to address each category one at a time.

## Constraints
- Never auto-apply bulk edits — always get confirmation
- Never use `obsidian delete` — use `obsidian move folder="_archive"` instead
- Never touch `dataScienceKnowledgeBase/dswok`
- Skip `_archive/` folder in all audits
- Rename with `obsidian rename` (not file system mv) — preserves backlinks

## Examples

**"Review Claude Code CLI note"**
```bash
obsidian read file="Claude Code CLI"
obsidian links file="Claude Code CLI"
obsidian backlinks file="Claude Code CLI" counts
obsidian wordcount file="Claude Code CLI"
# → report → user approves → apply fixes
```

**"Vault health check"**
```bash
obsidian orphans total
obsidian unresolved
obsidian deadends
obsidian tags total
# → present report → offer to fix per category
```
