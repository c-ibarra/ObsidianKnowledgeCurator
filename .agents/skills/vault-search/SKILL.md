---
name: vault-search
description: Use this skill when the user wants to find, retrieve, or locate notes in their Obsidian vault. Triggers include "find notes about", "search my vault for", "what do I have on", "do I have anything on".
---

# Vault Search Skill

## Goal
Locate the most relevant notes in the vault using the `obsidian` CLI, rank them by
relevance, and present actionable results with excerpts.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "open" || echo "CLOSED"
# Read obsidian-cli skill before operating
```

**⚠️ Never read or surface content from**: `dataScienceKnowledgeBase/dswok`

## Step 1 — Choose search strategy

| Query type | Command |
|-----------|---------|
| Keyword / exact phrase | `obsidian search query="<term>" limit=10` |
| Concept with context | `obsidian search:context query="<term>" limit=5` |
| By tag | `obsidian tag name="<tag>"` |
| Recent notes | `obsidian recents limit=10` |
| Folder-scoped | `obsidian files folder="<folder>" total` |
| Notes with no links | `obsidian orphans` |

For vague queries: run `search:context` first; if thin results, try `search` with synonyms.

## Step 2 — Execute search
```bash
obsidian search query="<query>" limit=10
```

**If empty results**:
1. Try a broader synonym
2. Remove qualifiers
3. If still empty: "No notes found about X. Do you want me to create one?"

**Fallback** (if search times out — Obsidian in background):
```bash
find "/Users/carlosibarra/projects/obsidianKnowledgeCurator/obsidianKnowledgeCurator" \
  -name "*.md" ! -path "*/dswok/*" \
  -exec grep -il "<query>" {} \; 2>/dev/null | head -10
```

## Step 3 — Read and rank top results
```bash
obsidian read file="<note name>"
```
Read top 3–5. Rank by: title match → recency → note type (analysis > video > article).

## Step 4 — Present results

```
📄 [[Note Title]]
Path: <RootFolder>/<folder>/<file>.md
Tags: #tag1 #tag2
Excerpt: "…relevant sentence from the note…"
```

Max 7 results. After listing, offer:
- Open in Obsidian: `obsidian open file="<name>"`
- Synthesize the found results → skill `knowledge-synthesis`
- Capture something new about this topic → skill `note-capture`

## Constraints
- Excerpts only in initial results — full content only if user asks
- Never surface results from `dswok`
- If >20 results, ask for refinement before reading all
- Prefer `obsidian search` over `grep/find`

## Examples

**"What do I have on LangGraph?"**
```bash
obsidian search query="LangGraph" limit=10
obsidian search:context query="LangGraph agents" limit=5
```

**"Show me everything tagged #no-read-yet"**
```bash
obsidian tag name="no-read-yet"
```

**"Do I have notes on Claude Code?"**
```bash
obsidian search query="Claude Code" limit=10
obsidian files folder="dataScienceKnowledgeBase/AI Engineer/Claude Code" total
```
