---
name: okc-study
description: Creates, manages, and syncs curated study decks and flashcards between Obsidian and Anki.
---

# OKC Study Decks & Flashcards Skill

Use this skill when the user wants to generate active-recall flashcard decks from curated notes, books, or entire categories, format them cleanly in Obsidian, and synchronize them directly to Anki.

Triggers include:
- `/okc-study`
- "crear mazo de estudio"
- "generar flashcards"
- "sincronizar mazo con anki"
- "study deck"
- "create study cards"

## Workflow

### 1. Create a Study Deck (`/okc-study create`)
To create a new managed study deck from a source folder or note and sync it directly to Anki:

```bash
uv run python scripts/study_deck.py create --source "<folder_or_note_path>" --deck "<DeckName>" [--anki-deck "<AnkiDeckName>"]
```

Example:
```bash
uv run python scripts/study_deck.py create --source "dataScienceKnowledgeBase/AI Engineer/raw/Claude Code" --deck "Claude Code Mastery"
```

### 2. Check Study Deck Status (`/okc-study status`)
To view card counts and Anki synchronization status:

```bash
uv run python scripts/study_deck.py status --deck "<DeckName>"
```

### 3. Synchronize to Anki (`/okc-study sync-anki`)
To push or re-sync pending flashcards and visual media to Anki:

```bash
uv run python scripts/study_deck.py sync-anki --deck "<DeckName>"
```

### 4. Recover Dangling Transactions (`/okc-study recover`)
To scan the 2PC journal and cleanly recover or abort interrupted transactions after a crash:

```bash
uv run python scripts/study_deck.py recover [--clean-only]
```

## Formulation Principles (SuperMemo 20 Rules)


When generating or refining flashcards with the agent:
1. **Minimum Information Principle**: Every card must test a single, atomic concept or step.
2. **Context First**: Explicitly name the domain or technology in the question (avoid "What is this?").
3. **Dual Model Standard**:
   - `Basic`: Question (`Q:`) / Answer (`A:`).
   - `Cloze`: Text with deletions (`{{c1::key concept}}`).
4. **Evidence Grounding**: Every card must be backed by verifiable source facts and reference its Knowledge Unit.
5. **No Visual Answers**: Questions must not reveal the answer in image file names or alt texts.
