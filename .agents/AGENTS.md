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
    *   *Execution:* Attempt to read the page content via `read_url_content` (or `browser_subagent` if blocked), format it into a note in `raw/`, extract concepts to `wiki/`, and run `uv run python scripts/sync_vault.py`.
*   **`/okc-urlPlaylist <url>`**
    *   *Purpose:* Ingest an entire YouTube playlist, curate each video sequentially in `raw/` and `wiki/`, and sync the vault.
    *   *Execution:* Fetch the list of all video IDs in the playlist, process each video sequentially (downloading the transcript, curating it in `raw/`, and updating `wiki/`), and run `uv run python scripts/sync_vault.py`.

## Formatting Guidelines
*   Always run the commands from the workspace root directory.
*   Format output inside a clean code block and append a list of any notes modified or referenced as clickable links (using the Obsidian URI scheme when relevant).
