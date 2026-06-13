---
name: knowledge-synthesis
description: Use this skill when the user wants to synthesize, summarize, or combine knowledge from multiple notes into a single coherent output. Triggers include "synthesize my notes on", "combine these notes", "create an overview of", "qué dicen mis notas sobre", "sintetiza mis notas sobre", "combina estas notas", "resumen de todo lo que tengo sobre".
---

# Knowledge Synthesis Skill

## Goal
Read multiple related notes from the vault and produce a coherent synthesis that follows
the vault's conventions (no YAML, blockquote header, standard sections) — using
`summary-generator` for processing and `obsidian` CLI for vault operations.

## Prerequisites
```bash
pgrep -x Obsidian > /dev/null && echo "open" || echo "CLOSED"
# Read obsidian-cli skill before operating
```

**⚠️ Never read or include content from**: `dataScienceKnowledgeBase/dswok`

## Step 1 — Gather source notes

**Path A — user provides specific notes**:
```bash
obsidian read file="<note 1>"
obsidian read file="<note 2>"
```

**Path B — user provides a topic**:
```bash
obsidian search query="<topic>" limit=10
obsidian search:context query="<topic>" limit=5
obsidian tag name="<related-tag>"
```
Read top 5–8 results. Confirm the source list with the user before proceeding.

Also check for existing backlinks that might add context:
```bash
obsidian backlinks file="<key note>" counts
```

## Step 2 — Process with `summary-generator`
Use `summary-generator` to extract from each note:
- Central claim (1 sentence)
- Supporting evidence or examples
- Open questions or tensions

Then identify cross-note patterns:
- **Agreements** → high-confidence insights
- **Tensions** → surface explicitly, don't pick sides
- **Progressions** → sequence logically
- **Gaps** → mark as open threads

## Step 3 — Validate with `superpowers`
Before writing:
- [ ] No hallucinated content
- [ ] No YAML frontmatter
- [ ] `[[links]]` in Related exist in the vault
- [ ] File name follows the naming convention
- [ ] Correct header blockquote

## Step 4 — Write synthesis (vault conventions)

```markdown
# Synthesis — <Topic>

> **Synthesis — <Topic>**
> Source: Multiple vault notes
> Date: Month Year
> Type: analysis
> Tags: #no-read-yet

## 📌 Key Takeaways
1. <most important insight>
2. ...
3. ...

## 1. <Main Topic>
<Paragraph synthesizing multiple notes, citing as [[Note A]], [[Note B]]>

## 2. <Tensions and Open Questions>
- [[Note A]] argues X, but [[Note C]] suggests Y — unresolved
- Why does Z happen? No note answers this yet

## Flashcards
Q: <key question>
A: <synthesized answer>

## Glossary
**Term**: Definition

## Related
- [[Note A]]
- [[Note B]]
- [[Note C]]
```

## Step 5 — Save to vault
```bash
obsidian create path="<RootFolder>/<Category>/Synthesis — <Topic>.md" \
  content="<content>" silent

obsidian read file="Synthesis — <Topic>"   # verify
```

Optionally add backlink in source notes:
```bash
obsidian append file="<source note>" content="\n→ Synthesized in: [[Synthesis — <Topic>]]"
```

## Constraints
- Never invent claims not present in source notes
- Surface tensions — never silently pick one side
- Synthesis: 300–800 words; split if longer
- Always attribute insights to source notes with wikilinks
- No YAML, no emojis outside of `## 📌 Key Takeaways`

## Examples

**"Synthesize my notes on MCP"**
```bash
obsidian search query="MCP Model Context Protocol" limit=10
obsidian files folder="dataScienceKnowledgeBase/AI Engineer/MCP" total
# read → summary-generator → validate → write to Syntheses or MCP folder
```

**"Combine my notes on LangGraph and LangChain"**
```bash
obsidian search query="LangGraph" limit=5
obsidian search query="LangChain" limit=5
# compare → structure as comparison synthesis
```
