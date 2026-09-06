---
name: okc-bookFlashcards
description: "High-Density Active Recall (HDAR) Book Flashcard Engine (/okc-bookFlashcards). Reads entire EPUB or non-fiction books, extracts semantic chapters and sections, formulates atomic active-recall flashcards, and synchronizes directly to Anki and Obsidian."
---

# High-Density Active Recall (HDAR) Book Flashcard Skill

Use this skill whenever the user asks to generate, build, or synchronize comprehensive flashcards from a technical book or long document (EPUB, PDF).

Triggers:
- `/okc-bookFlashcards <input>`
- `/okc-bookDeck <input>`
- "crear flashcards del libro"
- "generar mazo del libro"
- "transformar libro en flashcards"

---

## 🎯 Executive Standard: High-Density Active Recall (HDAR)

This skill enforces the 7 core principles of the **HDAR Standard** automatically, removing the need for 200-line user prompts:

### 1. Hierarchical Semantic Decomposition
```text
Document (EPUB / PDF)
  └── Chapter (Sequential Processing, no arbitrary skipping)
        └── Semantic Sections (Author H1/H2 boundaries, not token-chopping)
              └── Core Concepts (Mechanisms, Principles, Trade-offs)
                    └── Atomic Flashcards (Basic / Optional Reversed)
```

### 2. High-Yield Question Taxonomy (Not Just Definitions)
Combine diverse cognitive layers across each section:
- **Recall**: *What is X?* (concise, precise)
- **Understanding**: *Why does X function this way?*
- **Mechanism & Process**: *What are the sequential stages of X?*
- **Trade-offs & Comparisons**: *How does X differ from Y and when to choose which?*
- **Failure Modes & Defenses**: *What causes X to fail and how is it mitigated?*
- **System Architecture**: *Where does X fit within the broader production stack?*

### 3. Atomic Card Standard (`Basic (optional reversed card)`)
- **Card Type**: `Basic (optional reversed card)`
- **Front (Question)**: Clear, self-contained, independent of book context.
- **Back (Answer)**: Concise yet complete explanation, preserving technical terms in English.
- **Add Reverse**: Set to `"y"` ONLY for symmetric relationships (canonical definitions, exact formulas, terminology pairs). Leave empty `""` for explanatory, causal, or procedural questions.

### 4. Strict Book Fidelity (Zero Hallucination)
Cards must be grounded exclusively in the book text. Never use external knowledge to supplement or alter the author's statements. Preserve the author's technical definitions, examples, and terminology.

### 5. Media & Visual Diagram Integration
- Extract diagrams and architectural figures from the book into `output/<slug>/images/`.
- Upload images as Base64 to Anki media store via `storeMediaFile`.
- Embed cleanly using `<img src="filename.png">` in the answer.

### 6. Validation & Duplicate Purging Rubric
Every candidate card must satisfy:
- **Fidelity**: Supported 100% by the source section.
- **Clarity**: Unambiguous question and direct answer.
- **Atomicity**: Tests exactly one knowledge unit.
- **Independence**: Understandable without opening the book.
- **Deduplication**: Normalized n-gram check preventing redundant questions.

### 7. Resilient Checkpointing & Multi-Format Export
- Track progress per chapter in `checkpoint.json` (`pending`, `processing`, `completed`, `failed`).
- Compile to:
  1. `deck_full.json`: Complete database with metadata.
  2. `deck_full.md`: Obsidian Spaced Repetition plugin format.
  3. `deck_full_anki.tsv`: Anki TSV format.
  4. Direct Anki synchronization via AnkiConnect / MCP (`AI Engineer::<Deck Name>`).

---

## 🚀 Execution CLI

The engine is executed with:

```bash
# Ingest, extract, and generate cards for a new book
uv run python scripts/book_flashcards_engine.py --input "<path_to_epub>" --deck "<Deck Name>" [--sync-anki]

# Inspect processing status and checkpoint
uv run python scripts/book_flashcards_engine.py --status [--slug "<book_slug>"]

# Re-compile and export full deck artifacts
uv run python scripts/book_flashcards_engine.py --compile [--slug "<book_slug>"]
```
