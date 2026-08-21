# ADR 0004: OKC Doctor Unified Diagnostics, Integrity Audit, and Vault Synchronization Suite

*   **Status**: Approved
*   **Date**: 2026-08-17
*   **Deciders**: Carlos Ibarra, Antigravity Architect

---

## Context and Problem Statement

As the Obsidian Knowledge Curator (OKC) ecosystem matured across thousands of markdown notes, multiple knowledge categories (AI Engineer, Software Engineer, Machine Learning, Health & Medicine, etc.), and continuous multi-modal ingestions (YouTube, web articles, podcasts, books, office documents), maintaining comprehensive vault health and index synchronization presented several operational challenges:

1. **Fragmented Health Checks**: Link auditing (`vault_linter.py`), Master Plan regeneration (`update_master_plan.py`), and Graphify graph compilation (`graphify_helper.py` / `sync_vault.py`) were invoked through disparate scripts without a single consolidated diagnostic status report.
2. **Invisible Unicode Artifacts (Zero-Width Spaces - ZWSP)**: Web scrapers, PDF extractions, and multi-format converters occasionally introduce invisible unicode characters (`\u200b`, `\u200c`, `\u200d`, `\ufeff`), disrupting search indexing, regex matching, and Obsidian wikilink resolution.
3. **Orphan Visual Assets**: Continuous article and book ingestions download figures and diagrams into `assets/images/`. Over time, unreferenced or orphaned images accumulate without visibility.
4. **Read-Only Protected Zone Verification**: Strict assurance is required that protected engineering reference zones (`dswok`, `system-design-primer`, `data-science-interviews`, `ai-engineering-field-guide`, `ai-system-design-interview-studio`) remain 100% immutable and uncorrupted.

## Decision Drivers

*   **Single Unified Diagnostic Command**: Provide a one-stop health check and full synchronization suite via `/okc-doctor` (and its alias `/okc-diagnosticsAndSynchronization`), executable in terminal or directly inside agent chat.
*   **Multi-Stage Comprehensive Audit (7 Stages)**:
    1. Differential SQLite Index Synchronization.
    2. Category-wide Master Plan Dynamic Rebuilding.
    3. Wikilink Integrity, Orphan Notes, and Explicit Contradictions (`[!contradiction]`) Linter.
    4. Invisible Unicode (ZWSP) Detection and Auto-Sanitization (`--fix`).
    5. Visual Assets Audit (`assets/images/` total vs unreferenced).
    6. Protected Zones Immutability Audit.
    7. Graphify Structural Knowledge Graph & `KNOWLEDGE.md` Regeneration.
*   **Automated Remediation (`--fix`)**: Clean and sanitize unicode artifacts in-place without manual file editing.
*   **Executive Status Reporting**: Render a standardized markdown scorecard summarizing the status, metrics, and actionable recommendations.

## Considered Options

1.  **Option A (Independent Tool Invocation)**: Keep running individual scripts (`vault_linter.py`, `sync_vault.py`, `update_master_plan.py`) separately when needed.
2.  **Option B (OKC Doctor Diagnostic & Auto-Repair Suite)**: Build a dedicated orchestrator (`scripts/okc_doctor.py`) implementing the 7-stage verification lifecycle, integrated with native agent skills (`.agents/skills/okc-doctor/` and `.agents/skills/okc-diagnosticsAndSynchronization/`) and slash command handlers in `GEMINI.md` and `AGENTS.md`.

## Decision Outcome

We selected **Option B**. `scripts/okc_doctor.py` serves as the primary health and synchronization monitor for the entire vault.

---

## Consequences

*   **Positive**:
    *   **Holistic Vault Visibility**: Instant status of SQLite database, navigation plans, wikilink integrity, visual assets, and graph nodes in under 35 seconds across 3,000+ files.
    *   **Automated Unicode Hygiene**: Eliminates corrupted formatting and regex breakage through automatic ZWSP stripping.
    *   **Protected Zone Guarantee**: Actively verifies that protected directories have zero unauthorized modifications.
    *   **Native Agent Integration**: Seamless execution via `/okc-doctor` with zero cognitive overhead.
*   **Neutral**:
    *   Full diagnostics run all 7 stages sequentially, requiring ~30s execution time for comprehensive multi-thousand-note scans.
