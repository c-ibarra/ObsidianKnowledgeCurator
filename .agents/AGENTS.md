# Custom Slash Command Handlers

When the user starts a message with a slash command, you must immediately execute the corresponding Python script in the workspace using your `run_command` tool, capture the output, and present the findings to the user.

## Command Mappings

*   **`/okc-trace <topic>`**
    *   *Purpose:* Chronological trace of an idea.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --trace "<topic>"`
*   **`/okc-emerge`**
    *   *Purpose:* Find implied ideas in recent notes.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --emerge`
*   **`/okc-drift`**
    *   *Purpose:* Compare intentions vs actual behaviors in notes.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --drift`
*   **`/okc-find <query>`**
    *   *Purpose:* Case-insensitive substring search for note titles.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --find "<query>"`
*   **`/okc-explore <concept>`**
    *   *Purpose:* Explore a concept in the local graph index and view its direct relationships.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --explore "<concept>"`
*   **`/getContextSize`**
    *   *Purpose:* Show current conversation context window size, character count, and estimated token count.
    *   *Execution:* `uv run python scripts/knowledge_commands.py --tokens`
*   **`/okc-sync`**


    *   *Purpose:* Rebuild master plans and run vault linter.
    *   *Execution:* `uv run python scripts/sync_vault.py`
*   **`/okc-linter`**
    *   *Purpose:* Run vault linter separately.
    *   *Execution:* `uv run python scripts/vault_linter.py`
*   **`/okc-urlYoutube <url>`**
    *   *Purpose:* Ingest a YouTube video. It downloads subtitles or automatically falls back to local Buzz CLI Whisper transcription if subtitles are disabled. It curates the note in `raw/` (including `Processed/Procesado` date), compiles concepts in `wiki/`, and syncs the vault.
    *   *Execution:* Run `uv run python scripts/fetch_youtube_data.py --url "<url>"`. Once completed, read `temp/fetched_data.json` and `temp/fetched_data.txt`, generate the curated note in `raw/`, compile concepts in `wiki/`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-urlArticle <url>`**
    *   *Purpose:* Fetch content from an article or web page, curate it in `raw/`, compile concepts in `wiki/`, and sync the vault.
    *   *Execution:* Run `uv run python scripts/fetch_article_data.py --url "<url>"`. Once completed, read `temp/fetched_data.json` and `temp/fetched_data.txt`, generate the curated note in `raw/`, compile concepts in `wiki/`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-urlPodcast <url>`**
    *   *Purpose:* Ingest a podcast episode or audio link, transcribe audio using Buzz CLI (Whisper), map Graphify context, curate note in `raw/`, compile concepts in `wiki/`, and sync the vault.
    *   *Execution:* Run `uv run python scripts/fetch_podcast_data.py --url "<url>"`. Once completed, read `temp/fetched_data.json` and `temp/fetched_data.txt`, generate the curated note in `raw/`, compile concepts in `wiki/`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-urlPlaylist <url>`**
    *   *Purpose:* Ingest an entire YouTube playlist, curate each video sequentially in `raw/` and `wiki/`, and sync the vault.
    *   *Execution:* Fetch the list of all video IDs in the playlist, process each video sequentially (downloading the transcript, curating it in `raw/`, and updating `wiki/`), and run `uv run python scripts/sync_vault.py`.
*   **`/okc-urlTwitter <url>`**
    *   *Purpose:* Ingest a Twitter/X post or video. It extracts post text and metadata, and if a video is present without subtitles, it automatically downloads the audio and transcribes it using Buzz CLI / Whisper. It curates the note in `raw/` (including `Processed/Procesado` date), compiles concepts in `wiki/`, and syncs the vault.
    *   *Execution:* Run `uv run python scripts/fetch_twitter_data.py --url "<url>"`. Once completed, read `temp/fetched_data.json` and `temp/fetched_data.txt`, generate the curated note in `raw/`, compile concepts in `wiki/`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-book <input>`** / **`/okc-bookSummary <input>`**
    *   *Purpose:* Ingest a non-fiction book or long document (PDF, EPUB, DOCX, TXT, MD) using the `okc-bookSummary` skill. It extracts structure, sanitizes text, segments chapters, synthesizes rich chapter notes (with anecdotes, metaphors, Mermaid mindmaps, key questions, and critical analysis), writes directly to the Obsidian Vault (`VAULT_ROOT`), compiles concepts in `wiki/`, purges temporary staging folders/files, and syncs the vault.
    *   *Execution:* Run `uv run python scripts/fetch_book_data.py --input "<input>"`. Read `temp/fetched_book_data.json` and `temp/fetched_book_data.txt`, generate book notes and chapter files directly in `VAULT_ROOT/dataScienceKnowledgeBase/<Category>/raw/Books/`, compile concepts in `wiki/`, run `uv run python scripts/fetch_book_data.py --clean`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-doc <input>`**
    *   *Purpose:* Ingest an office document, presentation, spreadsheet, EPUB or PDF (`.docx`, `.pptx`, `.xlsx`, `.epub`, `.pdf`, `.odt`, `.csv`) using AnyDoc (`firecrawl-anydoc`). Converts to clean Markdown, extracts embedded images to `<VAULT_ROOT>/assets/images/`, curates note in `raw/`, compiles concepts in `wiki/`, and syncs the vault.
    *   *Execution:* Run `uv run python scripts/fetch_doc_data.py --input "<input>"`. Read `temp/fetched_data.json` and `temp/fetched_data.txt`, generate curated note in `raw/`, compile concepts in `wiki/`, and run `uv run python scripts/sync_vault.py`.




## Formatting Guidelines
*   Always run the commands from the workspace root directory.
*   Format output inside a clean code block and append a list of any notes modified or referenced as clickable links (using the Obsidian URI scheme when relevant).

---

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout with `GEMINI.md` at repo root and ADRs in `docs/adr/`. See `docs/agents/domain.md`.

