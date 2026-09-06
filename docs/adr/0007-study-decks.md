# ADR 0007: Study Decks & Flashcards Engine (`/okc-study`)

*   **Status**: Approved
*   **Date**: 2026-09-05
*   **Deciders**: Carlos Ibarra, Antigravity Architect
*   **Target Release**: Obsidian Knowledge Curator v2.4.0


---

## Context and Problem Statement

Obsidian Knowledge Curator (OKC) excels at multi-modal ingestion (YouTube, books, research papers, articles, tweets, podcasts) and knowledge synthesis into `raw/` sources and `wiki/` concepts. While notes currently include an informal `## Flashcards` section (`Q:` / `A:`), flashcards have existed only as unstructured text:

1. **Lack of Lifecycle & Persistence**: Cards lack persistent identifiers and provenance. Modifying a note or running merge operations makes it impossible to track whether a card was updated, deleted, or verified.
2. **Missing Pedagogical Formulation**: Cards generated in bulk often violate core formulation principles (SuperMemo 20 rules): lack of atomicity, ambiguous context, or answers not strictly grounded in source evidence.
3. **No Direct SRS Synchronization**: Users must manually copy questions or rely on third-party scrapers to practice active recall in spaced repetition systems like Anki.
4. **Disposable vs Durable State Contradiction**: The existing `vault_index.db` is an ephemeral metadata cache designed to be dropped and rebuilt at any time. Storing study history, review states, and card identities inside it would cause catastrophic data loss upon cache invalidation.

---

## Decision Drivers

*   **Three-Tier Architecture**: Deterministic Python coordinator + durable SQLite persistence + semantic LLM execution via the Antigravity agent host.
*   **Durable Study State Isolation**: Persist study state, runs, knowledge units, card identities, and Anki mappings in `study-state/<vault_id>/study.db`, completely isolated from disposable indices.
*   **Two-Phase Knowledge Modeling**: Separate semantic comprehension (**KnowledgeUnit** with verifiable source evidence spans) from pedagogical card formulation (**CardItem** with retrieval objectives).
*   **Standard Anki Compatibility & Direct MCP Sync**: Support standard Anki models (`Basic` and `Cloze`) and sync directly to Anki via the `anki` MCP server (`createDeck`, `addNotes`, `storeMediaFile`).
*   **Managed Markdown Output in Vault**: Store curated study decks in `<RootFolder>/study/<Deck Name>.md` with unobtrusive HTML comments (`<!-- id: ... anki_id: ... rev: ... unit: ... -->`) preserving clean readability and Obsidian tooling compatibility.
*   **Incremental & Deterministic**: AST structural parsing with `markdown-it-py`, SHA-256 content hashing, and zero duplicate card generation on repeated runs.

---

## Considered Options

1.  **Option A (Third-party Obsidian Plugin Exclusively)**: Rely solely on community plugins (e.g., Obsidian_to_Anki or Obsidian Spaced Repetition) scanning raw notes.
    *   *Rejected*: Plugins lack semantic comprehension, evidence-grounded validation, multi-chapter reconciliation, and structured unit modeling.
2.  **Option B (Single-pass Direct Flashcard Generation)**: Have the LLM read raw note chunks and immediately write Q/A pairs to disk without intermediate models or persistence.
    *   *Rejected*: Leaves no audit trail of coverage, cannot detect hallucinations or missing concepts, and breaks incremental updates when notes change.
3.  **Option C (Coordinated Two-Phase Engine with SQLite Persistence & MCP Sync)**: Build `src/agent_tools/flashcards/` containing models, AST source parsing, knowledge unit extraction, card generation, and dual Markdown/Anki publishing.
    *   *Selected*: Balances deterministic code boundaries with LLM reasoning, provides rock-solid persistence, and seamlessly integrates with Anki.

---

## Decision Outcome

We selected **Option C**. The feature is introduced in **Obsidian Knowledge Curator v2.1.0** via the `/okc-study` slash command and skill.

---

## Technical Architecture

### 1. Data Model (`src/agent_tools/flashcards/models.py`)
- **`SourceDocument`**: Vault path, byte hash, format, last modified timestamp.
- **`SourceSpan`**: Verifiable text slice, heading path, line range, and content digest.
- **`KnowledgeUnit`**: Atomic technical concept, claims, conditions, exceptions, and direct `SourceSpan` evidence citations.
- **`RecallObjective`**: Evaluated facet (definition, process step, causal mechanism, contrast).
- **`CardItem`**: Pedagogical card representation (type: `Basic` or `Cloze`, front blocks, back blocks, tags, media references, unit reference, card ID, revision hash, and Anki note ID).
- **`DeckManifest`**: Deck identity, vault output destination, bound sources, and Anki target deck name.

### 2. State & Persistence (`src/agent_tools/flashcards/store.py`)
- SQLite database located at `PROJECT_ROOT/study-state/<vault_id>/study.db`.
- WAL mode enabled, enforcing foreign keys.
- Tables:
  - `study_documents`
  - `study_sections`
  - `study_units`
  - `study_evidence`
  - `study_cards`
  - `study_decks`
  - `study_runs`
  - `study_work_items`
  - `study_suppressions`
  - `study_media`
  - `study_tx_journal`

### 3. Structural Source Parsing (`src/agent_tools/flashcards/sources.py`)
- Uses `markdown-it-py` to parse Markdown into structured AST tokens.
- Preserves heading hierarchies, paragraphs, code fences, LaTeX math blocks (`$...$`, `$$...$$`), tables with headers, and Obsidian wikilinks/embeds (`![[...]]`).
- Enforces strict exclusion of protected zones (`PROTECTED_ZONES`).

### 4. Generation & Anki MCP Synchronization (`src/agent_tools/flashcards/deck.py`)
- Generates standard Obsidian Markdown deck:
  ```markdown
  # Study Deck — System Design

  > **Curated Study Deck — System Design**
  > Source: [[dataScienceKnowledgeBase/AI Engineer/raw/...]]
  > Target Anki Deck: Machine Learning::System Design
  > Cards: 24 · Processed: 05-09-2026
  > Tags: #study-deck #anki

  ## Flashcards

  Q: ¿Cuál es el propósito del Write-Ahead Logging (WAL) en bases de datos relacionales?
  A: Garantizar la durabilidad (D de ACID) registrando las modificaciones en disco secuencialmente antes de aplicarlas a las páginas de datos.
  <!-- id: card_a1b2c3d4 anki_id: 1725580000000 rev: 9f8e7d unit: ku_db_wal -->
  ```
- Calls MCP `anki:createDeck` to ensure the deck exists in Anki.
- Calls MCP `anki:storeMediaFile` for referenced visual assets in `assets/images/`.
- Calls MCP `anki:addNotes` to push notes into Anki with tags and field mappings, capturing the returned note IDs into SQLite and Markdown.
- Calls MCP `anki:updateNoteFields` during incremental updates to keep card edits synced without resetting spaced-repetition progress.

### 5. Two-Phase Commit Journal & Recovery (`src/agent_tools/flashcards/journal.py`)
- Ensures transactional consistency between SQLite state, filesystem Markdown files, and Anki.
- `PREPARED` -> Writes staging files (`<Deck>.md.<tx_id>.tmp`) and logs transaction intent.
- `COMMITTED` -> Performs atomic filesystem swap and transitions state in SQLite.
- `ABORTED` / `RECOVERED` -> Cleans up dangling files or finishes interrupted commits via `study_deck.py recover`.


---

## Rollout Plan

- **Phase 0-4 (MVP in v2.1.0)** [Completed]:
  - Phase 0: Architecture, ADR 0007, and Agent guidelines.
  - Phase 1: Pydantic models and SQLite durable store.
  - Phase 2: Structural AST parser and source span extraction.
  - Phase 3: Knowledge Unit extraction and evidence validation.
  - Phase 4: Card generation, Markdown deck rendering for `CREATE`, and Anki MCP synchronization.
- **Phase 5 (v2.2.0)** [Completed]:
  - Three-way merge for human edits (`ADD` and `UPDATE` operations).
- **Phase 6 (v2.3.0)** [Completed]:
  - SHA-256 media asset cloning and deep visual comprehension.
- **Phase 7 (v2.4.0)** [Completed]:
  - Two-phase commit journal (`study_tx_journal`), atomic swaps, and crash recovery (`recover`).

