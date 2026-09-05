# ADR 0006: Note Normalizer, Deduplication, and Header Sanitizer Engine

*   **Status**: Approved
*   **Date**: 2026-09-05
*   **Deciders**: Carlos Ibarra, Antigravity Architect

---

## Context and Problem Statement

As the Obsidian Knowledge Curator (OKC) scales across multi-modal ingestion pipelines (YouTube, web articles, podcasts, books, office documents, and Notion migrations), thousands of notes are compiled into the vault. Over time, external imports and repetitive ingestions introduce three operational challenges:

1. **Duplicate Notes**: Repeated ingestions or migrations occasionally create duplicate copies of notes across different subfolders, polluting the knowledge graph and degrading search relevance.
2. **Empty or Low-Value Stubs**: Ingestion edge-cases (e.g., interrupted runs, empty placeholder files) generate stubs that dilute technical density and inflate node counts.
3. **Inconsistent Metadata Headers**: Notes imported from external platforms (e.g., Notion, legacy Markdown dumps) often lack the canonical Obsidian blockquote metadata (`Author`, `Source`, `Type`, `Processed`, `Tags: #no-read-yet`), disrupting automated Master Plan compilation and SQLite metadata queries.

Performing manual audits, deduplications, and header additions across a multi-thousand-note vault is labor-intensive and error-prone.

## Decision Drivers

*   **Content-Hash Deduplication**: Identify identical note content via deterministic SHA-256 digests rather than brittle file name matching.
*   **Safe Non-Destructive Archiving**: Never delete duplicate notes or stubs outright; move them into a localized `_archive/` directory to allow manual verification or recovery.
*   **Canonical Header Standardization**: Detect notes lacking metadata and non-destructively inject the standardized Obsidian blockquote header.
*   **Dry-Run Safety**: Support previewing all proposed changes via `--dry-run` without modifying any filesystem state.
*   **Atomic Vault Synchronization**: Provide a `--sync` flag that immediately updates the SQLite index and regenerates Category Master Plans after normalization.
*   **Native Agent Integration**: Expose functionality via both CLI (`scripts/normalize_notes.py`) and agent skill (`.agents/skills/okc-normalize/`, `/okc-normalize`).

## Considered Options

1.  **Option A (Ad-hoc Manual Cleanup & Custom Shell Scripts)**: Rely on manual file inspections or transient shell commands (`find`, `rm`, `sed`). Rejected due to high risk of data loss and lack of standardized reporting.
2.  **Option B (Dedicated Note Normalizer Engine)**: Build a robust, tested Python engine (`src/agent_tools/note_normalizer.py`), standalone CLI (`scripts/normalize_notes.py`), and corresponding agent skill (`okc-normalize`).

## Decision Outcome

We chose **Option B**. The note normalizer engine was implemented as a core component of the curation toolchain.

---

## Technical Architecture

The normalizer executes in three distinct phases:

1. **Audit & Analysis Phase**:
   - Recursively traverses the target directory.
   - Computes SHA-256 hashes of markdown body content.
   - Classifies notes into:
     - `canonical`: Primary notes with valid content and structure.
     - `duplicate`: Identical content copies of an existing canonical note.
     - `stub`: Notes with fewer than minimum content threshold words or empty bodies.
     - `missing_header`: Notes lacking the canonical `> **Author — Title**` blockquote.

2. **Execution & Archiving Phase (`--fix`)**:
   - Creates an `_archive/` subfolder within the target directory.
   - Safely moves duplicates and stubs into `_archive/`.
   - Injects canonical blockquote headers into notes missing them, inferring title and type from path conventions.

3. **Atomic Synchronization Phase (`--sync`)**:
   - Calls `sync_db()` from `scripts/vault_db.py` to refresh the SQLite index.
   - Regenerates affected Category Master Plans to reflect cleaned structures.

---

## Consequences

*   **Positive**:
    *   **Zero Data Loss**: Safe archiving into `_archive/` preserves historical copies.
    *   **Consistent Metadata**: All vault notes adhere to the standard header specification required by `vault_db.py` and `update_master_plan.py`.
    *   **Higher Signal-to-Noise**: Elimination of stubs and duplicates keeps the Graphify AST index and concept cards lean.
    *   **Full Test Coverage**: Validated via unit tests in `tests/test_note_normalizer.py`.
*   **Neutral**:
    *   Deep recursive scans of very large directories require reading file contents into memory to compute content hashes.
