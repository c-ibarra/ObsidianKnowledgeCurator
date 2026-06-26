---
name: okc-linter
description: Audits the knowledge graph for broken links, orphans, and contradictions.
---

# Vault Linter Command Skill

When this skill is invoked via `/linter`, execute the following steps:

1. **Run Linter Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/vault_linter.py
   ```
2. **Present Results:**
   - Present the detected broken links, orphans, and contradictions to the user.
