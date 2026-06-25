# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-06-25

### Added
- **`scripts/sync_vault.py`**: A unified sync script that updates category/series Master Plans and executes the vault linter sequentially. Accepts a `--target-kb` flag and forwards it to child scripts.
- ** Fleshed out `--find <query>` command in `scripts/knowledge_commands.py`**: Performs fast, case-insensitive note name substring matching across the vault, printing matching nodes as wikilinks along with relative paths. Excludes config folders like `.obsidian` and `.git`.
- **Graphify Query Skill**: Added `.agent/skills/graphify-query/SKILL.md` to document how to query the local knowledge graph using `graphifyy`.

### Fixed
- **Dynamic Import bug in `knowledge_commands.py`**: Fixed a crash where the script failed to dynamically load `call_gemini` from the non-existent `curate_workflow.py` by redirecting it to `curate_notion_import.py`.

### Changed
- **Adaptive Ingestion Policy**: Documented density control rules in `GEMINI.md` to avoid redundant stubs and promote incremental wiki updates.

## [2.2.0] - 2026-06-11

### Added
- **Native Agentic Curation**: The Antigravity agent now handles LLM reasoning, parsing, and markdown generation natively within its context, eliminating the need for hardcoded API calls inside scripts.
- **`fetch_youtube_data.py`**: A new headless utility script replacing `curate_workflow.py` and `batch_wiki_extractor.py`. It solely extracts video metadata and transcripts via `yt-dlp` and `youtube-transcript-api` to a temporary JSON file for the agent to read.

### Changed
- Removed `.env` dependency for Gemini API keys in curation scripts, delegating all intelligence to the Antigravity SDK.
- Updated `GEMINI.md` and `README.md` to reflect the new native curation architecture.

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
