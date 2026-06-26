# ADR 0001: Migration to Antigravity 2.0 and Decoupled Architecture

*   **Status**: Approved
*   **Date**: 2026-05-28
*   **Deciders**: Carlos Ibarra, Antigravity Architect

---

## Context and Problem Statement

The Obsidian Knowledge Curator was originally configured as a monolithic Claude Project. This resulted in highly coupled, prompt-heavy system instructions, tight environmental configurations, and rigid tool pathways. As the Obsidian Vault grew, this monolith suffered from **Context Decay** (context exceeding the 40% efficiency limit) and **Intent Drift** (hallucinating vault rules during multi-turn prompting).

We needed a highly modular, decoupled, and production-ready agent architecture that can seamlessly handle multi-source ingestions, enforce strict vault formatting, and scale without manual prompt maintenance.

## Decision Drivers

*   **Modularity**: Ability to hot-swap capability components (skills) without touching core orchestrator rules.
*   **Deterministic Formatting**: Enforcing zero-YAML note structure, backlinks validation, and strict header compliance.
*   **Scale**: Safely handling extremely long transcripts and large vaults without hitting token limits or API rate blocks.
*   **Security**: Completely isolating environment configurations, OneDrive Vault paths, and API keys.

## Considered Options

1.  **Option A**: Maintain the monolithic Claude Project setup with advanced prompt-engineering hacks.
2.  **Option B**: Refactor into **Antigravity 2.0 SDK**, decoupling configuration (`.agents/settings.json`), core system prompts (`GEMINI.md`), and reusable encapsulated capabilities (`.agents/skills/`).

## Decision Outcome

We selected **Option B (Antigravity 2.0 SDK Refactoring)** because it solves intent drift by separating cognitive orchestrator rules from mechanical tools. Additionally, it natively supports declarative Model Context Protocol (MCP) integrations, sandboxed Python runtime bindings via `uv`, and localized staging environments.

---

## Consequences

*   **Positive**:
    *   **High Modularity**: Adding a new skill (e.g. Notion integration) simply requires creating a directory in `.agents/skills/` without touching `GEMINI.md`.
    *   **Robust Scrapes**: YouTube transcripts are dynamically downloaded via Python wrappers (`youtube-transcript-api` in `uv run`), bypassing scrape blocks.
    *   **Staging Isolation**: Complex writes are drafted in a local `temp_note.md` workspace buffer before final copying, protecting target file systems from encoding corruptions.
*   **Neutral**:
    *   Requires configuring local environment values inside `.env` to locate absolute vault sync folders.
