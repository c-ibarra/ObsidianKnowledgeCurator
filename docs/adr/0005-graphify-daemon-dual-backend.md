# ADR 0005: Configurable Local/Remote Graphify Backend

*   **Status**: Approved
*   **Date**: 2026-08-21
*   **Deciders**: Carlos Ibarra, Claude

---

## Context and Problem Statement

`~/projects/graphify-daemon` is a new, separately-maintained resident process that serves this vault's concept graph over MCP from an in-RAM snapshot, always current — a strict freshness improvement over the legacy pipeline (`scripts/graphify_helper.py`), whose `graphify-out/graph.json` only updates when explicitly triggered (`sync_vault.py`, `okc_doctor.py`, or manually).

Two scripts in this repo need this concept graph outside of a live agent conversation — `scripts/knowledge_commands.py`'s `run_explore()` and `scripts/okc_doctor.py`'s dashboard node/edge counts — but they reach it through genuinely different mechanisms. `run_explore()` reads the daemon's `graph.json` **as a file**, because it needs raw structured JSON for its hand-rolled traversal (source_file, file_type, node id) that no MCP tool returns — MCP tools return LLM-facing text, not structured data. `okc_doctor.py` instead calls the daemon's live `graph_stats` **MCP tool directly** (an HTTP `tools/call`, the same mechanism an agent uses) since it only needs two integers, not a traversable structure — so unlike `run_explore()`, its daemon-sourced counts carry no on-disk-lag caveat; they're as fresh as any live MCP query. `run_explore()`'s file-based path is the one the schema/scope mismatches below actually apply to:

1. **Schema mismatch is real, not cosmetic**. The daemon's `graph.json` tags `source_file` with no scheme at all (bare vault-relative paths); the legacy pipeline's uses `vault://`/`project://` prefixes. `run_explore()`'s Obsidian-deep-link and disambiguation logic depends on that addressing scheme.
2. **Scope mismatch is real, not cosmetic**. The daemon indexes only the vault; the legacy pipeline also indexes this repo's own code (`PROJECT_DIR`) into the same graph, under the `project://` scheme. Concepts backed by this repo's own scripts/skills (confirmed via a live count: 1,181 `project://` nodes in the legacy graph) simply don't exist in the daemon's output.
3. **A third layer — vault metadata (`vault_db.py`'s SQLite index: file content, title, author, wikilinks, `[!contradiction]` callouts)** — has no daemon equivalent at all. The daemon's own `vault_index.db` is a deliberately minimal, different schema (path/mtime/size/node_count/edge_count only). `scripts/vault_linter.py` and `scripts/update_master_plan.py` read this layer exclusively.

Simply repointing both scripts unconditionally at the daemon's output would silently degrade `run_explore()` (losing code-lookup capability and needing a compatibility shim for the addressing-scheme difference) with no way to opt back out, and would leave no path forward at all for `vault_linter.py`/`update_master_plan.py`.

## Decision Drivers

*   **No unconditional migration**: confirmed with the user that `/explore`'s real-world usage is overwhelmingly vault-content lookups, not this repo's own code — the scope loss is acceptable, but only as a chosen default, not a forced one.
*   **Reversibility without a code change**: a user who hits the scope loss, or who wants to force a specific source for debugging, needs a config knob, not a patch.
*   **No silent degradation when forced**: if a user explicitly asks for the daemon-only path, a daemon failure must be visible, not quietly masked by an unrequested fallback to stale or narrower legacy data.
*   **Don't extend the daemon's scope to force a clean migration**: extending `graphify-daemon`'s schema/tools to cover vault metadata (title/author/links/contradictions) or this repo's own code was evaluated and explicitly rejected as out of scope for this change — a decision for `vault_linter.py`/`update_master_plan.py`'s owners to make separately if ever needed.

## Considered Options

1.  **Option A (Unconditional migration)**: Repoint `run_explore()` and `okc_doctor.py`'s counts at the daemon's output permanently, accept the scope/addressing differences as final.
2.  **Option B (Leave everything on the legacy pipeline)**: Don't adopt the daemon in these two scripts at all; keep depending on `sync_vault.py`'s manual/triggered freshness.
3.  **Option C (Extend the daemon)**: Add the missing vault-metadata and this-repo's-own-code coverage to `graphify-daemon` itself, then migrate all five scripts (including `vault_linter.py`/`update_master_plan.py`) cleanly.
4.  **Option D (Configurable dual backend, automatic by default)**: Both scripts try the daemon's output first and fall back to the legacy pipeline silently (`GRAPHIFY_BACKEND=auto`, the default); a `GRAPHIFY_BACKEND` env var can force `local` (never touch the daemon) or `remote` (only the daemon, fail loudly instead of falling back) on top of that default. `vault_linter.py`/`update_master_plan.py` are untouched — Layer 1 has no daemon path under any option short of C.

## Decision Outcome

We selected **Option D**. It captures Option A's freshness win as the default behavior without losing Option B's full-scope capability — that capability just requires an explicit `GRAPHIFY_BACKEND=local` instead of being the default. Option C was rejected for this change specifically because it's a materially larger scope (new daemon schema/tools, a decision for a different codebase's own owners) than what motivated this change (two scripts' read path).

---

## Consequences

*   **Positive**:
    *   `run_explore()`/`okc_doctor.py` get the daemon's freshness by default with zero configuration.
    *   The scope/addressing differences are never a silent trap — `okc_doctor.py`'s dashboard row states which source produced its numbers; `run_explore()`'s "not found" case is one config value away from being explained (`GRAPHIFY_BACKEND=local` recovers the lost scope, at the cost of losing the freshness win).
    *   `GRAPHIFY_BACKEND=remote` gives a clean way to verify "is the daemon actually the source of truth right now" without guessing from a script's output alone.
*   **Neutral**:
    *   Two distinct `GraphBackendUnavailable` exception classes exist (`knowledge_commands.py`, `okc_doctor.py`) rather than one shared one — the two scripts don't otherwise import from each other, and introducing a shared module for one marker class was judged not worth the added coupling.
    *   `vault_linter.py`/`update_master_plan.py` remain entirely local with no config-driven alternative; extending the daemon to cover that layer (Option C) is deferred, not ruled out.
