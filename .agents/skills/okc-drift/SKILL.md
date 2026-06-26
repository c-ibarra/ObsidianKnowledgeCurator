---
name: okc-drift
description: Compares stated intentions in older notes with actual recorded behavior in recent notes.
---

# Concept Drift Analysis Skill

When this skill is invoked via `/drift`, execute the following steps:

1. **Run Drift Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/knowledge_commands.py --drift
   ```
2. **Present Results:**
   - Present the drift analysis details and recommendations to the user.
