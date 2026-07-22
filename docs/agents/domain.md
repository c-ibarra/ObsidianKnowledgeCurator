# Domain Documentation Layout: Single Context

This repository uses a single-context domain documentation structure.

## Layout

- **Root Context File:** `GEMINI.md` (and `CONTEXT.md` if present) at the repository root defines the system architecture, vault rules, and core workflow.
- **Architecture Decision Records (ADRs):** Stored under `docs/adr/` using sequential numbering (`0001-migration-to-antigravity.md`, `0002-unified-sync-and-fast-search.md`).

## Agent Rules

1. Before designing new components or refactoring core architecture, check `docs/adr/` for existing decision records.
2. Respect protected zones (`dataScienceKnowledgeBase/dswok`) and vault zone architecture (`raw/`, `wiki/`, `dev/`).
