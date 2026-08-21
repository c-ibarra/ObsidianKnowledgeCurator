---
name: okc-doctor
description: "Comprehensive diagnostics, integrity audit, and full synchronization suite for the Obsidian vault (/okc-doctor). Audits SQLite index, category Master Plans, broken wikilinks, contradictions, Unicode/ZWSP hygiene, orphaned assets in assets/images/, protected zones, and rebuilds Graphify knowledge graph and KNOWLEDGE.md index. Supports --fix to auto-repair issues."
---

# OKC Doctor (`/okc-doctor`) — Full Diagnostics & Vault Synchronization

Runs a comprehensive health check, integrity audit, and full synchronization across the entire Obsidian vault.

## Execution

To run a diagnostic audit (read-only mode):
```bash
uv run python scripts/okc_doctor.py
```

To run diagnostics with automatic sanitization (clean ZWSP artifacts and fix issues):
```bash
uv run python scripts/okc_doctor.py --fix
```

## Checks Executed
1. **SQLite Database Index**: Differential synchronization of all vault files.
2. **Category Master Plans**: Dynamic regeneration of all navigation maps across vault categories.
3. **Vault Integrity Linter**: Broken wikilinks, orphaned notes, and explicit contradictions (`[!contradiction]`).
4. **Unicode / ZWSP Hygiene**: Detection and cleaning of invisible zero-width spaces.
5. **Visual Assets Audit**: Inspection of unreferenced images in `assets/images/`.
6. **Protected Zones Audit**: Read-only verification of protected engineering zones.
7. **Graphify Knowledge Graph**: Update of `graph.json`, `graph_cache.json`, and `KNOWLEDGE.md`.
