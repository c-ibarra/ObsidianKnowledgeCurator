---
name: obsidian-knowledge-curator
description: Use this skill to query, search, trace, and reference the user's compiled knowledge vault across all folders (IA, PKM, etc.). Triggers on questions like "What do I know about X?", "Tell me about Y", or general requests to read or review vault concept notes.
---

# Obsidian Knowledge Curator Skill

## Goal
To act as a vault-aware personal memory and research assistant, answering queries and referencing technical concepts from any knowledge area in the vault using a structured and unified index.

## Behavior Rules
1. **Separation of Concerns**: Do not mix your system prompt/behavioral guidelines with technical definitions. All technical knowledge and concept cards are compiled separately in [KNOWLEDGE.md](KNOWLEDGE.md).
2. **Context Retrieval**:
   - When the user asks a technical or conceptual question, your first step is to open [KNOWLEDGE.md](KNOWLEDGE.md) and search for matching keywords or concepts.
   - If the concept is found, read the note path cited, and read the note file directly using the `view_file` tool to obtain high-fidelity details.
3. **Wikilinking**:
   - Always reference vault notes using `[[wikilinks]]`. Never use standard Markdown links `[text](file.md)` inside vault contexts.
4. **Accuracy & Citing**:
   - Quote notes directly when referencing facts.
   - If the requested topic is not present in [KNOWLEDGE.md](KNOWLEDGE.md) or the vault notes, state that it is not available in the vault instead of fabricating details.

## Graph Verification
If `graphify-daemon` is running (`GET /health` on its configured host/port returns `{"ready": true}`), use its `query_graph`/`shortest_path` MCP tools to trace shortest paths and locate relevant nodes quickly — its snapshot is always current, no separate update step needed. Otherwise, if the local Graphify index exists (`graphify-out/graph.json`), fall back to running `graphify query "<question>"`.
