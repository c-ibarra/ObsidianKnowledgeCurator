---
name: okc-emerge
description: Scans recent notes to find implicit conclusions or recurring patterns.
---

# Concept Emergence Skill

When this skill is invoked via `/emerge`, execute the following steps:

1. **Run Emerge Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/knowledge_commands.py --emerge
   ```
2. **Present Results:**
   - Present the emerging concepts and patterns to the user.
