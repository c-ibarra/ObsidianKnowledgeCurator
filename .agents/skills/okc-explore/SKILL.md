---
name: okc-explore
description: Explore a concept in the local graph index and view its direct relationships.
argument-hint: <concept>
---

# Explore Concept Skill

When this skill is invoked via `/okc-explore <concept>`, execute the following steps:

1. **Run Explore Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/knowledge_commands.py --explore "<concept>"
   ```
2. **Present Results:**
   - Present the concept summary, its direct neighbors/relationships, and clickable Obsidian URIs.
