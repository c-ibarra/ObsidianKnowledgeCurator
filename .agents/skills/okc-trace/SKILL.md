---
name: okc-trace
description: Reconstructs the chronological evolution of an idea across your vault notes.
argument-hint: <topic>
---

# Idea Trace Skill

When this skill is invoked via `/trace <topic>`, execute the following steps:

1. **Run Trace Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/knowledge_commands.py --trace "<topic>"
   ```
2. **Present Results:**
   - Format the chronological trace output nicely inside a clean markdown block.
   - Present the links of any referenced notes as clickable links to the user.
