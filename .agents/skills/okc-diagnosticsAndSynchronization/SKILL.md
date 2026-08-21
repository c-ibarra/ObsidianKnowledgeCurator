---
name: okc-diagnosticsAndSynchronization
description: "Alias for /okc-doctor. Comprehensive diagnostics, integrity audit, and full synchronization suite for the Obsidian vault (/okc-diagnosticsAndSynchronization)."
---

# OKC Diagnostics & Synchronization (`/okc-diagnosticsAndSynchronization`)

Alias for [[okc-doctor]]. Runs a comprehensive health check, integrity audit, and full synchronization across the entire Obsidian vault.

## Execution

```bash
uv run python scripts/okc_doctor.py
```

With auto-repair:
```bash
uv run python scripts/okc_doctor.py --fix
```
