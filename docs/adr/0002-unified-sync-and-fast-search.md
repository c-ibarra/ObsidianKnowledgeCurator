# ADR 0002: Consolidated Post-Ingestion Sync and Fast CLI Note Search

*   **Status**: Approved
*   **Date**: 2026-06-25
*   **Deciders**: Carlos Ibarra, Antigravity Architect

---

## Context and Problem Statement

Following the ingestion of a new raw source (e.g., a YouTube transcript or web article), two post-processing steps are required to keep the Obsidian Vault healthy and indexed:
1. **Master Plan Updates**: Reconstructing the category-level navigation table mapping learning order.
2. **Vault Health Check**: Running the linter to verify `[[wikilinks]]`, orphan notes, and contradictions.

Previously, these scripts were separate and required individual manual execution. Additionally, as the vault grew, the agent risked creating redundant stub concept pages in the `wiki/` zone due to lack of a fast, local way to check if a topic note already existed. Executing full LLM searches for file checking was slow, expensive, and context-diluting.

## Decision Drivers

*   **Ingestion Efficiency**: Minimizing execution steps after importing raw content.
*   **Vault Density and Quality Control**: Preventing the proliferation of duplicate, low-value concept pages.
*   **Zero Token Search**: Enabling the agent to search for existing files within milliseconds without invoking LLM models.

## Considered Options

1.  **Option A**: Keep execution of `update_master_plan.py` and `vault_linter.py` separate, and continue using LLM-based directory lookups for checks.
2.  **Option B**: Create a unified runner (`sync_vault.py`) that executes both indexing and health checks in one run, implement a fast `--find` CLI search flag in `knowledge_commands.py`, and codify these into a strict **Adaptive Ingestion Policy**.

## Decision Outcome

We selected **Option B** because:
*   A unified runner ensures that a category's navigation maps and integrity graph checks never drift out of sync.
*   The `--find` option uses a native OS directory walk that executes in <0.1s with 0 API token cost, providing a fast, reliable concept verification API for the agent.
*   The **Adaptive Ingestion Policy** establishes clear rules that prioritize updating existing wiki notes over creating duplicates.

---

## Consequences

*   **Positive**:
    *   **Drastically Reduced Duplication**: The agent can now check for note name matches instantly before writing a new file to the wiki zone.
    *   **Unified Post-Ingestion Sync**: Post-processing is simplified into a single `uv run python scripts/sync_vault.py --target-kb "..."` command.
*   **Neutral**:
    *   Adds a dependency on the `--target-kb` folder naming conventions to ensure sync maps locate the correct Master Plan path.
