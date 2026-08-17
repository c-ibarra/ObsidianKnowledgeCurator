# ADR 0003: Centralized Configuration Module, Setup Wizard, and Repository Privacy Protection

*   **Status**: Approved
*   **Date**: 2026-08-17
*   **Deciders**: Carlos Ibarra, Antigravity Architect

---

## Context and Problem Statement

As Obsidian Knowledge Curator (OKC) expanded with over 30 automation scripts, multi-format parsers, Graphify indexers, and agent skills, path resolution and environment management were fragmented across multiple locations:
1. **Redundant Boilerplate**: Over 20 scripts independently implemented ad-hoc `.env` parsers (`load_env()`) and default path fallbacks.
2. **Hardcoded Path Risk & Repository Privacy Leaks**: Several legacy migration scripts and tracked agent configuration files (`.agents/settings.json`) contained absolute personal system paths (e.g. `/Users/carlosibarra/Library/...`), posing a risk of leaking personal system directory structures to public Git repositories.
3. **Environment Setup Friction**: Initializing the repository on a new machine or switching the local Obsidian Vault location (e.g. from OneDrive to `~/Documents/Obsidian`) required manual file editing across scattered scripts and settings.

## Decision Drivers

*   **Single Source of Truth**: Unified access to all project and vault paths through a dedicated Python configuration module (`src.config`).
*   **Strict Repository Privacy & Zero-Leak Guarantee**: Absolute personal paths must NEVER reside in Git-tracked files (`.env.template` and `.agents/settings.json` must only contain generic placeholders).
*   **First-Time Setup Experience**: Automated interactive and headless setup wizard (`scripts/setup_project.py` / `/okc-setup`) to configure local `.env` and validate system dependencies (`obsidian`, `yt-dlp`, `buzz`, `ffmpeg`, `uv`).
*   **Graphify & SQLite Index Adaptability**: Dynamic binding of Graphify root and SQLite database indices to the active configured vault location.

## Considered Options

1.  **Option A (Ad-Hoc Updates)**: Manually update `.env` and replace path strings in individual scripts whenever the vault path changes.
2.  **Option B (Centralized Config & Dual-Mode Setup Wizard)**: Create `src/config.py` as the sole configuration authority, create `.env.template` as the versioned template, sanitize all Git-tracked settings, and implement `scripts/setup_project.py` with dual support for interactive CLI and Antigravity slash command `/okc-setup`.

## Decision Outcome

We selected **Option B** because:
*   `src/config.py` provides clean, typed, and cached access to `VAULT_ROOT`, `ASSETS_IMAGES_DIR`, `GRAPHIFY_OUT_DIR`, `TEMP_DIR`, and category discovery helpers (`discover_vault_categories()`).
*   The `.env.template` + `.env` separation ensures that local user configurations remain strictly isolated and gitignored.
*   The `setup_project.py` script eliminates manual setup errors by automatically discovering Obsidian vault directories, detecting binary locations, and running initial synchronization pipelines (`sync_vault.py`).

---

## Consequences

*   **Positive**:
    *   **100% Privacy Protection**: No personal system paths exist in tracked files or repository history moving forward.
    *   **Zero Configuration Redundancy**: All scripts import configuration from `src.config`.
    *   **Streamlined Onboarding**: New environments can be configured in seconds via `uv run python scripts/setup_project.py` or `/okc-setup`.
    *   **Seamless Graphify Alignment**: Graphify and SQLite indices adapt immediately when `.env` changes.
*   **Neutral**:
    *   Python scripts inside `scripts/` require inserting the project root to `sys.path` to import from `src.config`.
