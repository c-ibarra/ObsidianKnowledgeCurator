# ADR 0008: High-Density Active Recall (HDAR) Full-Book Flashcard Engine (`/okc-bookFlashcards`)

*   **Status**: Approved
*   **Date**: 2026-09-06
*   **Deciders**: Carlos Ibarra, Antigravity Architect
*   **Target Release**: Obsidian Knowledge Curator v2.15.0

---

## Context and Problem Statement

Technical non-fiction books (e.g., *AI Engineering* by Chip Huyen, *Designing Data-Intensive Applications* by Martin Kleppmann) contain complex architectures, mathematical formulas, and deep operational trade-offs spanning 10+ chapters and hundreds of semantic sections. 

While the existing `/okc-study` engine excels at parsing already-curated Obsidian notes via AST, ingesting a raw non-fiction book directly into spaced repetition flashcards presented distinct challenges:

1. **Massive Context & Truncation Risks**: Processing whole EPUB/PDF books in a single LLM context window causes context overflow, model degradation, or superficial card generation that samples only initial chapters.
2. **Missing High-Yield Book Rubric**: Generic flashcard generation often produces low-value superficial trivia ("Who wrote chapter 3?") rather than testing causal mechanisms, architectural trade-offs, and failure modes.
3. **Multi-Format Disconnect**: Users need cards exported to multiple mediums simultaneously: 1-click Anki TSV imports, structured JSON databases, native Obsidian study notes (`VAULT_ROOT/.../study/`), and direct AnkiConnect/MCP synchronization.
4. **Resilience & Checkpoints**: Ingesting 10+ chapters takes sequential processing time; any transient API error or crash without persistent chapter checkpoints would force reprocessing from scratch.

---

## Decision Drivers

*   **Sequential Chapter-by-Chapter Processing**: Strict decomposition of the book into chapters, semantic sections, and concepts without skipping or sampling.
*   **High-Density Active Recall (HDAR) Standard**: Enforce a 7-rule pedagogical rubric guaranteeing atomic, high-yield flashcards focused on mechanisms, mathematical formulas, operational trade-offs, and failure modes.
*   **Persistent Resilient Checkpoints**: Maintain execution progress in `checkpoint.json` to allow resume-on-failure and incremental batching.
*   **Standard Model Alignment (`Basic (optional reversed card)`)**: Support asymmetric cards (`Add Reverse = ""`) and symmetric concepts (`Add Reverse = "y"`), with strict HTML image embeddings (`<img src="...">`).
*   **Multi-Output Convergence**: Export identical card collections across JSON, Markdown (Obsidian Vault), TSV (Anki manual import), and direct AnkiConnect synchronization.
*   **Encapsulated Unified CLI & Agent Skill**: Consolidate chapter extraction, concept generation, deduplication, audit reporting, and Anki synchronization into a single command line interface (`scripts/book_flashcards_engine.py`) and native Antigravity skill (`.agents/skills/okc-bookFlashcards/`).

---

## Decision Outcome

We created and integrated the **HDAR Full-Book Flashcard Engine** (`scripts/book_flashcards_engine.py`, `/okc-bookFlashcards` / `/okc-bookDeck`).

---

## Technical Architecture

### 1. High-Density Active Recall (HDAR) 7-Rule Rubric
Every generated card is evaluated and validated against:
1. **Zero Hallucination / Strict Grounding**: 100% faithful to source text; zero external speculation.
2. **Atomic Information Units**: Exactly one retrieval target per card (no multi-part questions or wall-of-text answers).
3. **Mechanism & Trade-Off Orientation**: Prioritizes "Why", "How does X work under the hood?", "What is the trade-off between A and B?", and "What is the failure mode of X?".
4. **Asymmetric Precision**: Standard Q/A cards use unidirectional recall; symmetric definitions use `allow_reverse: true` with `Basic (optional reversed card)`.
5. **Direct Media Binding**: Architectural diagrams and figures are referenced via `<img src="filename.png">` and uploaded directly to Anki via `storeMediaFile`.
6. **Bilingual Cognitive Balance**: Questions and explanations retain rigorous English technical terminology with accessible Spanish conceptual commentary where appropriate.
7. **Complete Structural Traceability**: Every card carries chapter ID, section name, exact source reference, and domain tags.

### 2. Processing Pipeline (`scripts/book_flashcards_engine.py`)

```
Raw Book (EPUB/PDF)
       ↓
[Phase 1: Extraction & Segmentation] -> extracted_book/ (ch01.json ... chN.json) + images/
       ↓
[Phase 2: Sequential Chapter Ingestion] -> Evaluates semantic sections against HDAR rubric
       ↓
[Phase 3: Resilient Checkpointing] -> checkpoint.json (tracks completed chapters)
       ↓
[Phase 4: Global Deduplication & Audit] -> audit_report.md
       ↓
[Phase 5: Multi-Format Compilation] -> deck_full.json, deck_full.md, deck_full_anki.tsv
       ↓
[Phase 6: Dual Publishing & Synchronization]
       ├──> Direct AnkiConnect / Anki MCP (Deck creation, storeMediaFile, addNotes)
       └──> Native Obsidian Vault Note (<VAULT_ROOT>/.../study/<Deck Name>.md)
```

---

## Consequences & Validation

### Positive
- **Proven at Scale**: Successfully ingested and verified all 10 chapters of *AI Engineering* by Chip Huyen, generating 163 verified atomic flashcards with 0 duplicates and syncing media diagrams to Anki.
- **Unified Interface**: Reduced what required multiple custom scripts into a single reusable CLI command and Antigravity slash command (`/okc-bookFlashcards`).
- **Data Boundary Hygiene**: Raw extracted book assets and generated flashcard files reside in local scratch directories (`output/`, excluded by `.gitignore`), while the curated study note is preserved in the Obsidian Vault.

### Negative / Trade-offs
- **Execution Latency**: Sequential chapter extraction and multi-stage verification for 10+ chapters requires multiple sequential model turns rather than a single fast prompt.
