# Obsidian Knowledge Curator — Antigravity 2.0 Migration Architecture

> **Status**: Ready for implementation  
> **Date**: 2025-05-28  
> **Platform**: Google Antigravity 2.0 (Gemini 3)  
> **Source**: Claude Project "obsidianKnowledgeCurator"

---

## 1. Agent Architecture

### Agent Purpose
The Obsidian Knowledge Curator is a **vault-native knowledge management agent** that
operates directly on the user's Obsidian vault via the `obsidian-mcp-tools` MCP server.
It handles the full knowledge lifecycle: capture → organize → link → search → synthesize → review.

### Core Responsibilities

| Responsibility | Description | Trigger Pattern |
|----------------|-------------|-----------------|
| Capture | Convert raw input into structured vault notes | "save this", "capture", "remember" |
| Search | Retrieve notes by topic, keyword, or concept | "find", "search", "what do I have on" |
| Daily Note | Create/update the daily log | "daily note", "log this", "today's note" |
| Link | Build connections between notes | "link", "connect", "MOC", "orphans" |
| Synthesize | Merge multiple notes into coherent summaries | "synthesize", "combine", "overview" |
| Review | Audit notes for quality and staleness | "review", "improve", "audit", "clean" |

### Context Management Strategy

```
User Prompt
    ↓
GEMINI.md (always loaded — ~600 tokens)
    ↓
Semantic Router (Antigravity built-in)
    ↓
    ├── Simple action? → MCP Tool directly
    │     (get_vault_file, search_vault, etc.)
    │
    └── Complex workflow? → Load matching Skill (~300-500 tokens)
              ↓
          Skill executes → calls MCP tools → returns result
```

**Key principle**: Skills are loaded on-demand only. GEMINI.md stays lean (~600 tokens)
so the router has maximum context budget for actual vault content.

### Tool Orchestration Flow

```
note-capture ──────→ create_vault_file
                   → search_vault_smart (pre-save dedup check)
                   → show_file_in_obsidian (optional)

vault-search ──────→ search_vault_smart OR search_vault_simple
                   → get_vault_file (read top results)
                   → show_file_in_obsidian (optional)

daily-note ────────→ get_vault_file (check exists)
                   → create_vault_file OR patch_vault_file
                   → execute_template (if user has Templater)
                   → show_file_in_obsidian

knowledge-link ────→ list_vault_files (orphan scan)
                   → get_vault_file (read candidates)
                   → search_vault_smart (per concept)
                   → patch_vault_file (add links)

knowledge-synthesis → search_vault_smart (gather sources)
                    → get_vault_file (read each)
                    → create_vault_file (save synthesis)

note-review ───────→ get_active_file OR get_vault_file
                   → patch_vault_file (apply fixes)
                   → list_vault_files (vault-wide audit)
```

---

## 2. Instruction Migration

### From Claude Project → Antigravity

| Claude Construct | Antigravity Equivalent | Location |
|-----------------|----------------------|----------|
| Project Instructions | `GEMINI.md` system prompt | `<workspace-root>/GEMINI.md` |
| Project Knowledge (static docs) | `references/` folders inside skills | `.agent/skills/<skill>/references/` |
| Claude Skills (`obsidian-cli`) | Antigravity `SKILL.md` packages | `.agent/skills/` |
| Tool use (MCP) | MCP server config | `.agent/settings.json` |
| Memory/context files | `references/` + GEMINI.md preamble | Per-skill references |

### System Prompt → GEMINI.md
The Claude Project's brief instruction ("Crear Obsidian Knowledge Curator para ejecutar con Antigravity")
has been expanded into a full `GEMINI.md` covering:

- **Identity & Purpose** — what the agent is and is not
- **Vault Configuration** — naming conventions, folder structure, date format
- **Core Responsibilities** — 6 explicit capabilities
- **Operational Rules** — safety guardrails (no silent deletes, confirm bulk ops)
- **MCP Tool Reference** — quick lookup table for all 11 obsidian-mcp-tools
- **Context Strategy** — when to use tools directly vs. skills
- **Safety & Fallback** — error handling and ambiguity resolution
- **Tone** — response style

### Operational Rules (migrated)

```yaml
rules:
  - id: no-silent-delete
    policy: Never delete a note without explicit user confirmation. Archive to _archive/ instead.
  - id: preserve-frontmatter
    policy: When editing a note, preserve existing YAML frontmatter. Only add new fields.
  - id: atomic-notes
    policy: One concept per note. Target 250-500 words.
  - id: confirm-bulk
    policy: Before modifying >5 notes, state exact scope and get confirmation.
  - id: skill-first
    policy: For multi-step workflows, load the matching skill. Do not improvise.
  - id: ambiguity-check
    policy: If intent is ambiguous (create vs. edit?), ask before acting.
```

### Safety & Fallback Logic

```
MCP tool fails → report error + suggest manual Obsidian action
Vault unreachable → explain MCP server requirement + link to setup
Intent ambiguous → ask clarifying question before any write operation
Destructive op → echo exact scope → wait for explicit confirmation
Skill not found → fall back to direct MCP tool use + explain limitation
```

---

## 3. Skills Mapping

| Claude Skill / Capability | Antigravity Skill | Scope | Notes |
|--------------------------|-------------------|-------|-------|
| `obsidian-cli` (full vault ops) | `note-capture` | workspace | Focused on creation flow |
| `obsidian-cli` (search) | `vault-search` | workspace | Multi-strategy search |
| `obsidian-cli` (daily notes) | `daily-note` | global* | Template-aware |
| `obsidian-cli` (linking) | `knowledge-link` | workspace | + MOC generation |
| Manual synthesis workflow | `knowledge-synthesis` | workspace | New — not in original |
| Manual review workflow | `note-review` | workspace | New — not in original |

*`daily-note` can be promoted to global scope (`~/.gemini/antigravity/skills/`) since it
applies across all projects.

### Skill Architecture Levels Used

| Skill | Level | Pattern | Has Scripts? | Has References? |
|-------|-------|---------|-------------|-----------------|
| `note-capture` | 1–2 | Router + Asset | No | No |
| `vault-search` | 1 | Router | No | No |
| `daily-note` | 2 | Router + Template | No | Yes* |
| `knowledge-link` | 1–3 | Router + Example | No | No |
| `knowledge-synthesis` | 1–3 | Router + Few-shot | No | No |
| `note-review` | 4 | Tool Use | Yes** | No |

*Add `references/daily-note-template.md` for user's custom template  
**Can add `scripts/vault_audit.py` for programmatic orphan/stale detection

---

## 4. Integration: Obsidian CLI (no MCP required)

### Why CLI instead of MCP

The `obsidian` native CLI (`/usr/local/bin/obsidian`) replaces the `obsidian-mcp-tools`
MCP server entirely. Benefits:
- No MCP server process to run or maintain
- No API key management
- Direct access to Obsidian's live indexes (search, backlinks, tags)
- `rename` and `move` preserve backlinks automatically — MCP tools cannot do this

### Prerequisites

1. **Obsidian must be open and running** — the CLI queries the live app process
2. **CLI available** at `/usr/local/bin/obsidian` (also at `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli`)
3. **Vault name**: `Obsidian` | **Path**: `/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian/`

### Verify setup
```bash
pgrep -x Obsidian && echo "running" || echo "open Obsidian first"
obsidian vault
obsidian version
```

### CLI → MCP Tool Equivalence

| Old (obsidian-mcp-tools) | New (obsidian CLI) |
|--------------------------|-------------------|
| `search_vault_smart(q)` | `obsidian search:context query="<q>" limit=10` |
| `search_vault_simple(q)` | `obsidian search query="<q>" limit=10` |
| `get_vault_file(path)` | `obsidian read file="<name>"` |
| `list_vault_files(folder)` | `obsidian files folder="<folder>" total` |
| `create_vault_file(path, content)` | `obsidian create name="<name>" content="..." folder="<f>" silent` |
| `append_to_vault_file(path, content)` | `obsidian append file="<name>" content="..."` |
| `patch_vault_file(path, content)` | `obsidian property:set` or `obsidian append` |
| `get_active_file()` | `obsidian recents limit=1` |
| `show_file_in_obsidian(path)` | `obsidian open file="<name>"` |
| `execute_template(template)` | `obsidian template:insert name="<template>"` |
| `delete_vault_file(path)` | ❌ Use `obsidian move file="<n>" folder="_archive"` instead |

### `.agent/settings.json`
No MCP server configuration needed:
```json
{
  "mcpServers": {},
  "_notes": {
    "obsidian": "CLI at /usr/local/bin/obsidian — Obsidian must be running",
    "vault": "Obsidian",
    "vaultPath": "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian/"
  }
}
```

### Search fallback (if CLI times out)
```bash
find "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian" \
  -name "*.md" -exec grep -il "<query>" {} \; 2>/dev/null | head -10
```

---

## 5. Recommended Folder Structure

```
obsidianKnowledgeCurator/         ← Antigravity workspace root
│
├── GEMINI.md                     ← Core agent config (always loaded)
├── MIGRATION_ARCHITECTURE.md     ← This document
│
├── .agent/
│   ├── settings.json             ← MCP server configuration
│   └── skills/                   ← Workspace-scoped skills
│       ├── note-capture/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── note-templates.md     ← (optional) custom templates
│       ├── vault-search/
│       │   └── SKILL.md
│       ├── daily-note/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── daily-note-template.md ← (optional) user's template
│       ├── knowledge-link/
│       │   ├── SKILL.md
│       │   └── examples/
│       │       └── moc-example.md        ← (optional) MOC reference
│       ├── knowledge-synthesis/
│       │   ├── SKILL.md
│       │   └── examples/
│       │       └── synthesis-example.md  ← (optional) output example
│       └── note-review/
│           ├── SKILL.md
│           └── scripts/
│               └── vault_audit.py        ← (optional) programmatic audit
│
└── antigravity_urls.md           ← Reference documentation URLs
```

**Global skills** (available across all Antigravity workspaces):
```
~/.gemini/antigravity/skills/
└── daily-note/                   ← Promote here for cross-project use
    └── SKILL.md
```

---

## 6. Implementation Steps

### Phase 1 — Environment Setup (Day 1)

- [ ] Download and install Google Antigravity from `antigravity.google/download`
- [ ] Install the **Obsidian Local REST API** community plugin in Obsidian
- [ ] Copy the API key from Obsidian → Settings → Local REST API
- [ ] Create `.agent/settings.json` in this workspace with the MCP config (see Section 4)
- [ ] Open this workspace in Antigravity's Agent Manager
- [ ] Verify: type "list my vault files" → confirm `list_vault_files` returns results

### Phase 2 — Skills Validation (Day 1–2)

Test each skill with a sample prompt:

| Skill | Test Prompt |
|-------|------------|
| `note-capture` | "Capture this idea: knowledge compounds over time" |
| `vault-search` | "Find my notes on productivity" |
| `daily-note` | "Create today's daily note" |
| `knowledge-link` | "Find orphan notes in my vault" |
| `knowledge-synthesis` | "Synthesize my notes on learning" |
| `note-review` | "Review the active note" |

### Phase 3 — Customization (Day 2–3)

- [ ] Add your vault's custom folder paths to relevant skills if different from defaults
- [ ] Copy your Obsidian Daily Note template into `daily-note/references/daily-note-template.md`
- [ ] Add example notes to `knowledge-synthesis/examples/` to guide synthesis style
- [ ] Adjust tag taxonomy in `note-capture/references/note-templates.md`
- [ ] (Optional) Write `note-review/scripts/vault_audit.py` for automated auditing

### Phase 4 — Global Skill Promotion (Day 3)

- [ ] Copy `daily-note/` to `~/.gemini/antigravity/skills/daily-note/` for cross-project use
- [ ] Consider promoting `vault-search/` to global scope if you use Obsidian across projects

### Phase 5 — Iteration (Ongoing)

- After each session, note which skill descriptions need tuning (the `description:` field in
  YAML frontmatter is the trigger — if a skill isn't auto-selected, the description needs
  to be more specific or include more trigger phrases).
- Add `references/` documentation as your vault conventions solidify.
- Add `scripts/` for automations that require deterministic logic (not LLM guessing).

---

## Key Architectural Decisions

### Why workspace scope (not global) for most skills?
The Obsidian vault path, folder structure, and naming conventions are project-specific.
Workspace-scoped skills can reference these conventions in their instructions without
needing the user to configure them per-project. Only `daily-note` is promoted to global
because the date-based structure is universal.

### Why no scripts/ yet?
Scripts add determinism for rule-based checks (e.g., the database validator pattern from
the Antigravity codelab). For the Obsidian Curator, most logic is semantic and benefits
from LLM reasoning. Scripts are recommended only for `note-review` (vault_audit.py)
where counting orphans and checking dates is better done programmatically.

### Why 6 skills instead of 1 mega-skill?
Following the Antigravity "Progressive Disclosure" principle: loading a 2000-token
monolithic skill for every vault operation wastes context. A user asking to "find a note"
should only load the ~300-token `vault-search` skill, not synthesis or review logic.
Each skill is focused, fast to load, and semantically distinct so the router selects correctly.
