---
name: okc-sync
description: Rebuilds vault Master Plans and runs the vault health check.
---

# Vault Synchronization Skill

When this skill is invoked via `/sync`, execute the following steps:

1. **Run Sync Script:**
   Run the terminal command:
   ```bash
   uv run python scripts/sync_vault.py
   ```
2. **Present Results:**
   - Present the summary of synchronizations, contradictions found, dead links, and orphans to the user.
