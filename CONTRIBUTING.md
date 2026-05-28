# Contributing to Obsidian Knowledge Curator

We maintain a strict **Modular Skill Architecture**. To extend this agent with a new capability (e.g., Notion sync or Slack notifier):

## Development Guidelines

1. **Do not modify the Core Orchestrator (`GEMINI.md`)**: The core cognitive architecture is non-negotiable and governs the global verification pipeline.
2. **Create a Decoupled Skill**: Add a dedicated directory under `.agent/skills/your-skill-name/`.
3. **Declare Tools**: Include a `tools.json` inside your skill folder matching the Model Context Protocol (MCP) spec.
4. **Implement Tests**: Add characterization and formatting tests inside `/tests` validating that your skill's inputs and outputs follow the vault formatting rules.

## Git Workflow

*   **Branch Naming**: Use `feat/skill-[name]`, `fix/[issue]`, or `chore/[task]`.
*   **Commit Style**: Follow **Conventional Commits**:
    *   `feat(skill): add note-review visual snapshot skill`
    *   `fix(scraper): rescue HTTP 429 when downloading VTT transcripts`
