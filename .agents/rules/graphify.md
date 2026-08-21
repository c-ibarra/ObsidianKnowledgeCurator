---
trigger: always_on
description: Consult graphify-daemon's live MCP tools for codebase and architecture questions. knowledge_commands.py reads the daemon's on-disk snapshot; okc_doctor.py calls its live MCP tools directly -- both controllable via GRAPHIFY_BACKEND. Legacy graphify-out/ pipeline is the fallback/local option, not a separate system to keep in sync by hand.
---

## graphify

This project's knowledge graph has two independent layers, both derived from the vault but covering different scope and read through different paths. Neither is optional to understand before touching graph-related code.

### Layer 1 — Vault metadata index (`vault_db.py`)

A SQLite index (`graphify-out/vault_index.db`) of vault content: `files` (path, mtime, size, full markdown `content`, `title`, `author`, `pub_date`, `type`, `category`), `links` (wikilink adjacency), `contradictions` (`[!contradiction]` callouts). Built and kept current by `sync_db()` (`scripts/vault_db.py`), driven by `scripts/sync_vault.py`.

Read by `scripts/vault_linter.py` and `scripts/update_master_plan.py` — **always local, no daemon path exists for this layer.** `graphify-daemon`'s own `vault_index.db` is a deliberately different, minimal schema (`path`, `mtime`, `size`, `node_count`, `edge_count` only) — it does not carry `content`/`title`/`author`/`links`/`contradictions`, so these two scripts have nothing to migrate to without extending the daemon itself (evaluated and explicitly deferred — see ADR 0005).

### Layer 2 — Concept/code graph (`graphify_helper.py` graph.json format)

A NetworkX graph (nodes = files/headings/code symbols, edges = contains/references/calls) serialized as `graph.json` (node-link format). Two independent producers write this same JSON shape:

- **Legacy**: `scripts/graphify_helper.py`, invoked by `sync_vault.py`/`okc_doctor.py`. Indexes **both** the vault and this repo's own code (`VAULT_ROOT` + `PROJECT_DIR`), tagging nodes with a `vault://`/`project://` scheme. Writes to `graphify-out/graph.json` + `graphify-out/graph_cache.json` + this repo's own `.agents/skills/obsidian-knowledge-curator/KNOWLEDGE.md`. Only rebuilds when explicitly triggered (`sync_vault.py`, `okc_doctor.py`, or manually).
- **graphify-daemon** (`~/projects/graphify-daemon`): a resident process serving the **vault only** (never this repo's own code) from an in-RAM snapshot over MCP (Streamable HTTP, loopback-only, API-key gated). Republishes on every vault batch — never staler than the last edit. Also periodically flushes to `~/projects/graphify-daemon/out/graph.json`, but only on slow cadence (60s of quiet or 25+ accumulated changes) or graceful shutdown — **that file lags the live in-RAM snapshot**, sometimes by tens of seconds, while a vault edit is actively propagating. Node `source_file` values here carry no scheme prefix at all (bare vault-relative paths) — a real schema difference from the legacy format, not just an addressing convenience.
- The daemon runs continuously as a `launchd` job (`com.carlosibarra.graphify-daemon`, `RunAtLoad`+`KeepAlive`) — check `GET /health` (`127.0.0.1:8787` by default, with the configured `X-API-Key`) if you need to confirm it's actually up before relying on it, but treat "not running" as the exception, not the norm.

### Two read paths into Layer 2, and who uses which

**Agents (this rule)** — always prefer the daemon's MCP tools directly when it's healthy: `query_graph` for broad questions, `shortest_path` for relationships, `get_node`/`get_neighbors` for a specific concept, `get_community`/`god_nodes`/`graph_stats` for structural overviews. These hit the live in-RAM snapshot, not the on-disk file — always current, no refresh step needed. If the daemon is down, fall back to the legacy CLI/file path: `graphify query "<question>"`, `graphify path "<A>" "<B>"`, `graphify explain "<concept>"` against `graphify-out/graph.json` (run `scripts/sync_vault.py` first if it's stale).

**Scripts** — governed by the same `GRAPHIFY_BACKEND` knob, but through two genuinely different mechanisms, not one:

- `scripts/knowledge_commands.py`'s `run_explore()` reads a **file** (`GRAPHIFY_DAEMON_GRAPH_JSON` from disk) — it needs the raw structured JSON for its hand-rolled node/edge traversal, which no MCP tool returns (those return LLM-facing text). This is the path subject to the on-disk-lag caveat in Layer 2 above.
- `scripts/okc_doctor.py`'s dashboard node/edge counts instead call the daemon's **live `graph_stats` MCP tool directly** (`_fetch_daemon_graph_stats()`, an HTTP POST to `/mcp`) — the same conversational tool interface agents use, not a file read at all. Its `daemon`-sourced counts are therefore as fresh as any live MCP query, with no on-disk-lag caveat.

Don't assume these two scripts fail or go stale the same way just because one `GRAPHIFY_BACKEND` value governs both. Config in `.env` (`src/config.py`, `GRAPHIFY_DAEMON_URL`/`GRAPHIFY_DAEMON_API_KEY`/`GRAPHIFY_DAEMON_GRAPH_JSON` alongside it):

| `GRAPHIFY_BACKEND` | Behavior |
|---|---|
| `auto` (default, unset) | Prefer `graphify-daemon`'s `graph.json`; fall back to `graphify-out/graph.json` silently if the daemon's isn't there or fails to parse. |
| `local` | Never touches the daemon's file at all — always reads `graphify-out/graph.json`. Also covers `vault_linter.py`/`update_master_plan.py`'s only mode (Layer 1 has no daemon path, see above). |
| `remote` | Only reads the daemon's `graph.json`; raises (`knowledge_commands.GraphBackendUnavailable` / `okc_doctor.GraphBackendUnavailable` — two distinct classes, one per script, deliberately not shared) instead of silently falling back if it's missing or unreadable. |

`run_explore()`'s legacy path can find concepts from this repo's own code (`project://` scheme); its daemon path cannot — the daemon never indexes this repo, only the vault (see Layer 2 above). This is a real scope loss in `auto`/`remote` mode, accepted because the overwhelming majority of `/explore` usage is vault-content lookups, not code lookups (confirmed with the user before building this). `okc_doctor.py`'s dashboard row shows which source produced its counts (`solo vault, vía graphify-daemon` / `vault + proyecto, legacy` / the remote-unavailable error label) so this is never silently ambiguous when reading a report.

`sync_vault.py`/`okc_doctor.py`'s subprocess trigger of `graphify_helper.py` (the legacy rebuild) runs **unconditionally, regardless of `GRAPHIFY_BACKEND`** — it's still the only thing that keeps Layer 1's `vault_db.db` and this repo's own `KNOWLEDGE.md` current, neither of which the daemon touches.

### Migration status

The daemon and the legacy watcher run on strictly separate output paths while the daemon's output is being validated against the legacy pipeline's over real time (see `~/projects/graphify-daemon/openspec/changes/add-graphify-daemon/` — still active, not yet archived; task group 12 tracks the parallel-run validation, cutover, and consumer-repoint decisions still pending). Layer 1 and this repo's own code-graph coverage are explicitly **not** part of that migration — see ADR 0005.
