# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-05-30

### Added
- **Generic Notion Curation Pipeline**: Refactored `curate_notion_import.py` to support fully parameterized command line execution (`--notion-dir`, `--target-kb`, `--course-name`) for any course or knowledge base.
- **Native Antigravity SDK Skills**: Added specialized native skills under `.agent/skills/` (`notion-curator`, `vault-linter`, `master-plan-builder`, `wiki-compiler`) enabling keyless, prompt-less autonomous execution in background agent contexts.

### Changed
- Replaced monolithic, hardcoded script values with dynamic system-prompt construction using `{TARGET_KB}` and `{COURSE_NAME}` references.
- Updated project documentation (`README.md`, `GEMINI.md`, `walkthrough.md`) to reflect the new dynamic scripts and native skill-based architecture.

## [2.0.0] - 2026-05-28

### Added
- **Staging/Drafting Execution Pattern**: Seamlessly write temporary drafts locally to `temp_note.md` in workspace before final secure vault copy commands.
- **Rule Zero Grounding**: Automatic google search lookups for video IDs before vault writing to prevent metadata drift.
- **Dynamic preferredModel settings**: Unified setting inside `.agent/settings.json` referencing Gemini 3.1 Pro.
- **Repository Structure Setup**: Automatic generation of `/docs`, `/agents`, `/prompts`, `/connectors`, `/configs`, `/memory`, and `/tests` directories.

### Changed
- Refactored Obsidian Knowledge Curator from a monolithic Claude Project architecture into a highly modular, decoupled **Antigravity 2.0 SDK** design.
- Reorganized YouTube scraping connection to prioritize robust Python-based API requests via `youtube-transcript-api` and `uv run`.

### Fixed
- Fixed critical exception: instantiating `YouTubeTranscriptApi` class correctly instead of using deprecated static methods.
- Solved context decay issue when parsing long transcripts (using the "Slicing" pattern to process in discrete chunks).
