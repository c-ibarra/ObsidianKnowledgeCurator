---
name: graphify-query
description: Queries the local Knowledge Graph using Graphify to search the codebase or vault semantically and explicitly. Use this skill before using grep or searching files when you need to understand relationships, find notes, or explore the codebase structure efficiently.
---

# Graphify Query Skill

This skill allows you to query the local Graphify knowledge graph to find connections between notes, files, classes, and concepts without consuming excessive tokens or grepping the entire repository.

## When to use
- When searching for how concepts are connected in the Obsidian Vault.
- When trying to understand the architecture or relationships in the codebase.
- When you want to find "neighbors" of a specific node/concept.

## Usage
Graphify provides a CLI command to query the graph. You should run this command using the `run_command` tool.

```bash
graphifyy query "What connects the concepts of Agentic AI and Hexagonal Architecture?"
```

## Options
- To update the graph after adding new files, use:
  ```bash
  graphifyy update
  ```

> **Note**: Graphifyy must be installed (`uv tool install graphifyy`) and the graph must have been initialized (`graphifyy`) in the current directory for this to work.
