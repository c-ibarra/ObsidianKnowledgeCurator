# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.15.0] - 2026-09-06

### Added
- **High-Density Active Recall (HDAR) Book Flashcard Engine (`scripts/book_flashcards_engine.py`, `/okc-bookFlashcards`, `/okc-bookDeck`)**: Implemented whole-book flashcard generation engine adhering to the 7-rule HDAR standard (ADR 0008). Automatically decomposes EPUB and PDF non-fiction books into semantic chapters and sections, formulates atomic `Basic (optional reversed card)` notes, avoids duplicates, links extracted diagrams, and syncs directly to Anki and Obsidian.
- **`okc-bookFlashcards` Native Agent Skill (`.agents/skills/okc-bookFlashcards/SKILL.md`)**: Registered native skill and slash command handler in `GEMINI.md` and `.agents/AGENTS.md`.
- **ADR 0008 (`docs/adr/0008-hdar-book-flashcards-engine.md`)**: Documented the architectural decisions, design drivers, and multi-format convergence of the full-book flashcard extraction engine.
- **Production AI Engineering Active Recall Deck**: Curated and synchronized 163 high-yield cards from Chip Huyen's *AI Engineering: Building Applications with Foundation Models* into Anki (`AI Engineer::Chip Huyen — AI Engineering`) and Obsidian study note.

## [2.14.0] - 2026-09-05

### Added
- **Note Normalizer & Stub Sanitizer Engine (`src/agent_tools/note_normalizer.py`, `scripts/normalize_notes.py`, `/okc-normalize`)**: Implemented automated audit, deduplication, stub removal, and canonical Obsidian blockquote header injection (ADR 0006). Supports `--dry-run`, safe archiving to local `_archive/` with `--fix`, and atomic SQLite index/Master Plan updates with `--sync`.
- **`okc-normalize` Native Agent Skill (`.agents/skills/okc-normalize/SKILL.md`)**: Registered native skill and documentation in `AGENTS.md` and `README.md`.
- **ADR 0006 (`docs/adr/0006-note-normalizer-and-sanitizer.md`)**: Documented the architectural decisions, design drivers, and consequences of content-hash deduplication and non-destructive archiving.
- **Enhanced OKC Doctor & Vault Health Linters**: Integrated normalization checks, dead link detection refinements, and SQLite index synchronization into `scripts/okc_doctor.py`, `scripts/vault_db.py`, `scripts/vault_linter.py`, and `scripts/vault_health_linter.py`.
- **Book Ingestion Service Refinements**: Refactored `src/agent_tools/book_ingestion/engine.py` with improved HDAS formatting and full test coverage in `tests/test_book_ingestion.py`.
- **Comprehensive Test Coverage**: Added `tests/test_note_normalizer.py` and expanded `tests/test_okc_doctor.py` (35 unit tests passing).

## [2.13.0] - 2026-08-21

### Added
- **Configurable local/remote Graphify backend (`GRAPHIFY_BACKEND`, ADR 0005)**: `scripts/knowledge_commands.py`'s `run_explore()` and `scripts/okc_doctor.py`'s dashboard node/edge counts now read from `graphify-daemon` (a separately-maintained resident MCP process serving an always-current in-RAM graph snapshot) by default, with silent fallback to the legacy `graphify_helper.py` pipeline. `GRAPHIFY_BACKEND=local`/`remote` in `.env` forces one source explicitly (`remote` fails loudly instead of silently falling back). `vault_linter.py`/`update_master_plan.py` are unaffected — the daemon doesn't cover vault metadata (titles, links, contradictions), only the concept graph.
- New `docs/adr/0005-graphify-daemon-dual-backend.md` documenting the decision and the alternatives considered (including extending the daemon itself, deferred as out of scope).
- `.agents/rules/graphify.md` rewritten to document the full two-layer graph architecture (vault metadata index vs. concept graph) and the two distinct mechanisms scripts use to reach the daemon (`run_explore()` reads its on-disk snapshot file; `okc_doctor.py` calls its live `graph_stats` MCP tool directly — different freshness characteristics despite sharing one `GRAPHIFY_BACKEND` knob).

## [2.12.0] - 2026-08-17

### Added
- **OKC Doctor Diagnostic & Synchronization Suite (`scripts/okc_doctor.py`, `/okc-doctor`, `/okc-diagnosticsAndSynchronization`)**: Built an automated, 7-stage full-vault health check, integrity audit, and synchronization suite (ADR 0004).
- **Invisible Unicode (ZWSP) Detection & Auto-Sanitization (`--fix`)**: Implemented recursive scanning and sanitization of zero-width space characters (`\u200b`, `\u200c`, `\u200d`, `\ufeff`) that interfere with markdown wikilinks, regex parsers, and search indices.
- **Visual Assets Inspection (`assets/images/`)**: Audits total vs unreferenced visual assets and figures across the vault.
- **Protected Zones Immutability Audit**: Ensures zero unauthorized modifications across protected engineering zones (`dswok`, `system-design-primer`, `data-science-interviews`, `ai-engineering-field-guide`, `ai-system-design-interview-studio`).
- **Dedicated Agent Skills (`okc-doctor` & `okc-diagnosticsAndSynchronization`)**: Registered native skills under `.agents/skills/` for frictionless execution with detailed status scorecard generation.
- **Visual Architecture Asset**: Added `assets/images/okc-linkedin-architecture-card.jpg` documenting the end-to-end multi-modal architecture.

## [2.11.0] - 2026-08-17

### Added
- **Centralized Configuration Authority (`src/config.py` & `src/__init__.py`)**: Created unified module as the single source of truth for all project paths (`VAULT_ROOT`, `ASSETS_IMAGES_DIR`, `GRAPHIFY_OUT_DIR`, `TEMP_DIR`, `SKILLS_DIR`), environment loading, and category discovery (`discover_vault_categories()`).
- **Interactive & Headless Setup Wizard (`scripts/setup_project.py` & `/okc-setup`)**: Added setup wizard script with dual-mode support (interactive CLI and Antigravity slash command), auto-detecting Vault locations (`~/Documents/Obsidian`), Obsidian CLI binaries, LLM providers (`gemini`/`ollama`), and validating system dependencies (`obsidian`, `yt-dlp`, `buzz`, `ffmpeg`, `uv`).
- **Official Environment Template (`.env.template`)**: Created standard git-tracked template file to safely initialize private `.env` without exposing personal user paths.
- **Repository Privacy Protection & Path Leak Prevention (ADR 0003)**: Sanitized all Git-tracked settings (`.agents/settings.json`) to generic placeholders, guaranteeing 0 personal system path leaks in public repositories.
- **Full Vault Migration & Graphify Rebuild**: Migrated vault reference to `~/Documents/Obsidian`, synchronized SQLite index (2,946 active files), and rebuilt Graphify graph (20,724 nodes, 20,715 edges) and `KNOWLEDGE.md` index (589 concepts).

### Changed
- **Refactored 25+ Scripts**: Eliminated duplicated `load_env()` implementations and hardcoded strings across `scripts/` and `src/agent_tools/`, routing all path and environment resolution through `src.config`.

## [2.10.0] - 2026-08-15

### Added
- **High-Density Actionable Synthesis (HDAS) Standard for Books (`okc-bookSummary`)**: Upgraded the book curation architecture to a 7-section modular structure combining continuous narrative depth with active learning tools (Tesis Central & Insight en 1 Frase, Preguntas de Indagación, Desarrollo Enriquecido con Modelos Mentales, Callouts Visuales de Metáfora/Cita/Trampa Común, Smart Cross-Domain Commentary, Guía de Aplicación Práctica con retos de 15 minutos, y Takeaway Ejecutivo en 1 Frase).
- **AnyDoc Document Ingestion Pipeline (`/okc-doc` & `scripts/fetch_doc_data.py`)**: Added native headless ingestion for office documents and formats (`.docx`, `.pptx`, `.xlsx`, `.epub`, `.pdf`, `.odt`, `.csv`) using `src/agent_tools/anydoc_engine.py`, extracting images directly to `<VAULT_ROOT>/assets/images/`.
- **Full Book Curation & Master Note Architecture**: Ingested and curated Kai-Fu Lee's *AI Superpowers* (*Superpotencias de la Inteligencia Artificial*) with 10 HDAS chapters, executive master note, and cross-linked domain concepts in `dataScienceKnowledgeBase/Machine Learning/raw/books/`.
- **Knowledge Concept Synthesis**: Curated and cross-linked domain concepts in `wiki/`: `MomentoSputnik.md`, `EmprendedoresGladiadores.md`, `CuatroOlasIA.md`, `ModeloOMO.md`, `EstipendioInversionSocial.md`, and `SimbiosisHombreMaquina.md`.

## [2.9.0] - 2026-08-07

### Added
- **Mandatory Local Image Preservation Policy & Engine (`scripts/fetch_article_data.py`)**: Added `download_article_images()` helper to automatically parse image URLs (HTML `<img>` tags, markdown `![]()`, Medium `miro.medium.com`, etc.), fetch remote image files via HTTP/SSL-bypass, save them directly to `<VAULT_ROOT>/assets/images/<slug>-img-<idx>.<ext>`, and embed native Obsidian wikilink syntax `![[assets/images/...]]` in notes.
- **Skill & Rule Alignment (`GEMINI.md`, `okc-urlArticle`, `okc-bookSummary`)**: Updated `GEMINI.md` global rules and `.agents/skills/okc-urlArticle/SKILL.md` to strictly enforce local image downloading into `<VAULT_ROOT>/assets/images/` for 100% offline self-containment and protection against broken external URLs.
- **Synthesized Knowledge Concepts**: Curated and cross-linked new technical concept notes in `wiki/`:
  - `OpenTelemetryGenAISemanticConventions.md` (GenAI OTel standard, `gen_ai.invoke_agent`, `gen_ai.inference.client`, `gen_ai.execute_tool`).
  - `AIObservabilitySignals.md` (Spans, p50/p95/p99 Metrics Histograms, Opt-In Event details).
  - `ForwardDeployedEngineer.md` (FDE role, Palantir Deltas, OpenAI/Anthropic deployment labs, LATAM nearshore opportunity).
  - `DecompositionRoundInterview.md` (Signature interview round evaluating ambiguous problem decomposition and simple MVP V1 delivery).
  - `AIEnterpriseDeploymentGap.md` (Friction points bridging Jupyter notebooks to enterprise Fortune 500 production).

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
