# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
