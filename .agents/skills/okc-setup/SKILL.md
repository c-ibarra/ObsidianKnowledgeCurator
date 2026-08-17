---
name: okc-setup
description: Interactive and automated setup wizard for Obsidian Knowledge Curator. Configures local Obsidian vault paths, CLI paths, LLM providers, and checks system dependencies.
---

# OKC Setup & Environment Wizard (`/okc-setup`)

Use this skill when the user wants to initialize, configure, or check their Obsidian Knowledge Curator project environment.

## Usage & Execution

```bash
# Interactive setup in terminal
uv run python scripts/setup_project.py

# Headless / Antigravity execution
uv run python scripts/setup_project.py --non-interactive --sync

# Check system dependencies only
uv run python scripts/setup_project.py --check-deps

# Custom vault path configuration
uv run python scripts/setup_project.py --vault-path "/path/to/Obsidian" --sync
```

## Key Configuration Parameters
1. `VAULT_ROOT` / `OBSIDIAN_VAULT_PATH`: Absolute path to your Obsidian vault.
2. `OBSIDIAN_CLI_PATH`: Path to Obsidian CLI binary.
3. `DENSITY_GRADER_PROVIDER`: `gemini` or `ollama`.
4. `GEMINI_API_KEY`: API key for Gemini models.
5. System binaries check: `uv`, `obsidian`, `yt-dlp`, `buzz`, `ffmpeg`.
