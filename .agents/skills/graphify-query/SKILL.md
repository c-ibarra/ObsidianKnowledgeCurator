---
name: graphify-query
description: Queries the local Knowledge Graph — via graphify-daemon's MCP tools when it's running, else the graphifyy CLI directly — to search the codebase or vault semantically and explicitly. Use this skill before using grep or searching files when you need to understand relationships, find notes, or explore the codebase structure efficiently.
---

# Graphify Query Skill

This skill allows you to query the local knowledge graph to find connections between notes, files, classes, and concepts without consuming excessive tokens or grepping the entire repository.

## When to use
- When searching for how concepts are connected in the Obsidian Vault.
- When trying to understand the architecture or relationships in the codebase.
- When you want to find "neighbors" of a specific node/concept.

## Usage

**Primary, if `graphify-daemon` is running** (`GET /health` on its configured host/port, default `127.0.0.1:8787`, returns `{"ready": true}`): call its MCP tools directly — `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`. These answer from the daemon's resident, always-current snapshot; there is no separate "update" step, since its own vault watcher republishes on every change.

**Fallback, if the daemon isn't running:** use the `graphifyy` CLI directly:

```bash
graphifyy query "What connects the concepts of Agentic AI and Hexagonal Architecture?"
```

To update the graph on disk after adding new files (only needed in this fallback path — the daemon never needs this):
```bash
graphifyy update
```

> **Note**: Graphifyy must be installed (`uv tool install graphifyy`) and the graph must have been initialized (`graphifyy`) in the current directory for the fallback CLI path to work.
