# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.8.0] - 2026-08-06

### Added
- **`GraphifyMapper` Local Context Engine (`scripts/graphify_mapper.py`)**: Implemented a hybrid zero-token local context mapper that queries `graphify-out/graph.json` to predict target `raw/` category directories and detect existing `wiki/` concepts (<50ms latency, $0.00 LLM token cost). Falls back to a lightweight LLM query only when local confidence is below 70%.
- **Podcast & Audio Ingestion Pipeline (`/okc-urlPodcast` & `scripts/fetch_podcast_data.py`)**: Added dedicated podcast and audio processing using `yt-dlp` + Buzz CLI (Whisper) for local offline transcription. Supports Siemens.FM, Spotify, Apple Podcasts, RSS feeds, YouTube audio, and direct `.mp3`/`.m4a` files.
- **`okc-urlPodcast` Skill & Slash Command**: Added `.agents/skills/okc-urlPodcast/SKILL.md` and registered `/okc-urlPodcast <url>` in `.agents/AGENTS.md`.
- **3-Tier Scraping Fallback Chain (`scripts/fetch_article_data.py`)**: Upgraded article scraping to a 3-tier fallback pipeline (Tier 1: `mcp-server-fetch`/`trafilatura`, Tier 2: Browser User-Agent DOM parsing with SSL bypass for restricted sites like LinkedIn, Medium, and captchas, Tier 3: Search-backed web compilation fallback). Includes auto-redirections for podcast and audio URLs.
- **Graphify Context Enrichment Across Ingestion Scripts**: Updated `fetch_article_data.py`, `fetch_youtube_data.py`, `fetch_twitter_data.py`, and `fetch_book_data.py` to automatically inject pre-calculated `"graphify_context"` objects into `temp/fetched_data.json`, cutting curation LLM tokens and latency.

## [2.7.0] - 2026-07-29

### Added
- **`okc-bookSummary` Non-Fiction Book Ingestion Pipeline**: Added non-fiction book ingestion pipeline and skill (`scripts/fetch_book_data.py` and `.agents/skills/okc-bookSummary/`). Supports PDF, EPUB, DOCX, TXT, and MD files.
- **Default Obsidian Vault Integration**: Standardized default writing of book summaries, individual chapter notes (`Chapter XX — <Title>.md`), images, wiki concepts, and Master Plan updates directly to `VAULT_ROOT`.
- **Enforced Chapter Depth (1,600–2,650 words)**: Configured word count rules requiring 900–1,500 words for Section 3 (Enriched Summary Development) and 1,600–2,650 words total per chapter note to ensure technical depth.
- **Visual Content & Mermaid.js Diagrams**: Native Mermaid.js mindmaps, sequence diagrams, architecture flows, and extracted figure callouts in every chapter.
- **Automatic Temporary File Cleanup**: Added `--clean` flag to `scripts/fetch_book_data.py` and automated deletion of temporary extraction files from `temp/` upon completion.
- **Slash Commands Update**: Added `/okc-bookSummary` and `/okc-book` to `.agents/AGENTS.md` and project documentation.

## [2.6.0] - 2026-07-17

### Added
- **Dynamic Web Scraping via CDP (`fetch_article_data.py`)**: Implemented a layout-aware web scraper that processes static HTML using `requests`/`BeautifulSoup` and falls back to launching local headless Google Chrome Canary/Chrome on macOS. Interacts via Chrome DevTools Protocol (CDP) and WebSocket handshakes (`--remote-debugging-port=9222`) to wait for client-side JavaScript rendering before extracting the DOM. This bypasses the OS restrictions of standard sandbox tools.
- **WebSocket Integration**: Added `websocket-client` dependency in `pyproject.toml` to enable CDP WebSocket handshakes.
- **Integrated Ingestion Workflows**: Updated custom slash command mapping in `.agents/AGENTS.md` and the `okc-urlArticle` skill guides to route all article ingestions through the automated `scripts/fetch_article_data.py` pipeline.

## [2.5.0] - 2026-07-03

### Added
- **High-Fidelity PDF Conversion via `marker-pdf`**: Integrated `marker-pdf` in `pyproject.toml` and updated `temp/extract_pdf.py` to use `marker_single` CLI for extracting structured Markdown with LaTeX math syntax and clean tables from papers.
- **MCP Server Architecture Patterns curation**: Curated Carson Rodrigues & Oysturn Vas (2026) arXiv paper detailing the five architectural patterns (Resource Gateway, Tool Orchestrator, Stateful Session Server, Proxy Aggregator, and Domain-Specific Adapter) and four anti-patterns, syncing it natively with the vault's graph.

## [2.4.0] - 2026-06-27


### Added
- **Buzz CLI fallback in `fetch_youtube_data.py`**: Automatic local Whisper transcription fallback when YouTube subtitles are disabled or unavailable.
- **`Processed/Procesado` date metadata convention**: Standardized metadata headers across 308 notes in the vault and rules (`GEMINI.md`, `okc-urlYoutube`, `okc-urlArticle` skills) to record the date when curated notes are processed.
- **Vault health corrections**: Grouped Parax and ObsidianKnowledgeCurator comparative analysis notes inside dedicated subdirectories in `raw/Portfolio ideas/`, resolving the orphan note count in the vault down to 0.

### Fixed
- **`yt-dlp` cookie session error**: Removed cookies from the audio extraction subprocess to prevent "This live event has ended" API errors on ended livestreams.

## [2.3.0] - 2026-06-25

### Added
- **`scripts/sync_vault.py`**: A unified sync script that updates category/series Master Plans and executes the vault linter sequentially. Accepts a `--target-kb` flag and forwards it to child scripts.
- ** Fleshed out `--find <query>` command in `scripts/knowledge_commands.py`**: Performs fast, case-insensitive note name substring matching across the vault, printing matching nodes as wikilinks along with relative paths. Excludes config folders like `.obsidian` and `.git`.
- **Graphify Query Skill**: Added `.agents/skills/graphify-query/SKILL.md` to document how to query the local knowledge graph using `graphifyy`.

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
- **Native Antigravity SDK Skills**: Added specialized native skills under `.agents/skills/` (`notion-curator`, `vault-linter`, `master-plan-builder`, `wiki-compiler`) enabling keyless, prompt-less autonomous execution in background agent contexts.

### Changed
- Replaced monolithic, hardcoded script values with dynamic system-prompt construction using `{TARGET_KB}` and `{COURSE_NAME}` references.
- Updated project documentation (`README.md`, `GEMINI.md`, `walkthrough.md`) to reflect the new dynamic scripts and native skill-based architecture.

## [2.0.0] - 2026-05-28

### Added
- **Staging/Drafting Execution Pattern**: Seamlessly write temporary drafts locally to `temp_note.md` in workspace before final secure vault copy commands.
- **Rule Zero Grounding**: Automatic google search lookups for video IDs before vault writing to prevent metadata drift.
- **Dynamic preferredModel settings**: Unified setting inside `.agents/settings.json` referencing Gemini 3.1 Pro.
- **Repository Structure Setup**: Automatic generation of `/docs`, `/agents`, `/prompts`, `/connectors`, `/configs`, `/memory`, and `/tests` directories.

### Changed
- Refactored Obsidian Knowledge Curator from a monolithic Claude Project architecture into a highly modular, decoupled **Antigravity 2.0 SDK** design.
- Reorganized YouTube scraping connection to prioritize robust Python-based API requests via `youtube-transcript-api` and `uv run`.

### Fixed
- Fixed critical exception: instantiating `YouTubeTranscriptApi` class correctly instead of using deprecated static methods.
- Solved context decay issue when parsing long transcripts (using the "Slicing" pattern to process in discrete chunks).
