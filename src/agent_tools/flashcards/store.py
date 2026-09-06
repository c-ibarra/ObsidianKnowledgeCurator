"""SQLite persistence for Study Decks & Flashcards state."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from typing import Any, Dict, List, Optional, Set

from src.config import get_study_state_dir
from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
    JournalEntry,
    JournalOperation,
    JournalStatus,
    KnowledgeUnit,
    SourceDocument,
    SourceSpan,
    UnitType,
    WorkItem,
)


class StudyStore:
    """Manages isolated SQLite persistence for study decks, units, and cards."""

    def __init__(self, db_path: Optional[Path] = None, vault_id: str = "default") -> None:
        if db_path is None:
            study_dir = get_study_state_dir(vault_id)
            self.db_path = study_dir / "study.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def _init_db(self) -> None:
        """Initializes tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS study_documents (
                    document_id TEXT PRIMARY KEY,
                    vault_path TEXT NOT NULL UNIQUE,
                    byte_hash TEXT NOT NULL,
                    mtime REAL NOT NULL,
                    title TEXT,
                    format TEXT NOT NULL DEFAULT 'markdown',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS study_spans (
                    span_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES study_documents(document_id) ON DELETE CASCADE,
                    heading_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    text_content TEXT NOT NULL,
                    content_digest TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS study_units (
                    unit_id TEXT PRIMARY KEY,
                    concept TEXT NOT NULL,
                    unit_type TEXT NOT NULL,
                    claims_json TEXT,
                    explanation TEXT NOT NULL,
                    conditions_json TEXT,
                    exceptions_json TEXT,
                    evidence_spans_json TEXT,
                    source_document_id TEXT NOT NULL REFERENCES study_documents(document_id) ON DELETE CASCADE,
                    importance INTEGER DEFAULT 3,
                    difficulty INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS study_decks (
                    deck_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    vault_path TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    anki_deck_name TEXT NOT NULL,
                    bound_sources_json TEXT,
                    revision_hash TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS study_cards (
                    card_id TEXT PRIMARY KEY,
                    deck_id TEXT NOT NULL REFERENCES study_decks(deck_id) ON DELETE CASCADE,
                    unit_id TEXT REFERENCES study_units(unit_id) ON DELETE SET NULL,
                    card_type TEXT NOT NULL DEFAULT 'Basic',
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    tags_json TEXT,
                    media_refs_json TEXT,
                    evidence_citation TEXT,
                    source_file TEXT,
                    revision_hash TEXT NOT NULL,
                    anki_note_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS study_runs (
                    run_id TEXT PRIMARY KEY,
                    deck_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS study_work_items (
                    work_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES study_runs(run_id) ON DELETE CASCADE,
                    stage TEXT NOT NULL,
                    input_json TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    result_json TEXT,
                    error TEXT
                );

                CREATE TABLE IF NOT EXISTS study_suppressions (
                    deck_id TEXT NOT NULL REFERENCES study_decks(deck_id) ON DELETE CASCADE,
                    card_id TEXT NOT NULL,
                    reason TEXT DEFAULT 'user_deleted',
                    suppressed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (deck_id, card_id)
                );

                CREATE TABLE IF NOT EXISTS study_media (
                    media_id TEXT PRIMARY KEY,
                    original_path TEXT NOT NULL,
                    published_path TEXT NOT NULL,
                    byte_size INTEGER NOT NULL,
                    mime_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS study_tx_journal (
                    tx_id TEXT PRIMARY KEY,
                    deck_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    target_path TEXT NOT NULL,
                    staging_path TEXT NOT NULL,
                    payload_json TEXT DEFAULT '{}',
                    status TEXT NOT NULL DEFAULT 'PREPARED',
                    created_at TEXT NOT NULL,
                    finalized_at TEXT,
                    error_message TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_spans_doc ON study_spans(document_id);
                CREATE INDEX IF NOT EXISTS idx_units_doc ON study_units(source_document_id);
                CREATE INDEX IF NOT EXISTS idx_cards_deck ON study_cards(deck_id);
                CREATE INDEX IF NOT EXISTS idx_cards_unit ON study_cards(unit_id);
                CREATE INDEX IF NOT EXISTS idx_suppressions_deck ON study_suppressions(deck_id);
                CREATE INDEX IF NOT EXISTS idx_tx_status ON study_tx_journal(status);
                """
            )


    # ------------------ Documents & Spans ------------------

    def upsert_document(self, doc: SourceDocument) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO study_documents (document_id, vault_path, byte_hash, mtime, title, format)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    vault_path = excluded.vault_path,
                    byte_hash = excluded.byte_hash,
                    mtime = excluded.mtime,
                    title = excluded.title,
                    format = excluded.format
                """,
                (doc.document_id, doc.vault_path, doc.byte_hash, doc.mtime, doc.title, doc.format),
            )

    def get_document_by_path(self, vault_path: str) -> Optional[SourceDocument]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM study_documents WHERE vault_path = ?", (vault_path,)
            ).fetchone()
            if not row:
                return None
            return SourceDocument(
                document_id=row["document_id"],
                vault_path=row["vault_path"],
                byte_hash=row["byte_hash"],
                mtime=row["mtime"],
                title=row["title"],
                format=row["format"],
            )

    def save_spans(self, spans: List[SourceSpan]) -> None:
        if not spans:
            return
        with self._get_connection() as conn:
            for s in spans:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO study_spans
                    (span_id, document_id, heading_path, start_line, end_line, text_content, content_digest)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (s.span_id, s.document_id, s.heading_path, s.start_line, s.end_line, s.text_content, s.content_digest),
                )

    def get_spans_by_document(self, document_id: str) -> List[SourceSpan]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM study_spans WHERE document_id = ? ORDER BY start_line ASC", (document_id,)
            ).fetchall()
            return [
                SourceSpan(
                    span_id=r["span_id"],
                    document_id=r["document_id"],
                    heading_path=r["heading_path"],
                    start_line=r["start_line"],
                    end_line=r["end_line"],
                    text_content=r["text_content"],
                    content_digest=r["content_digest"],
                )
                for r in rows
            ]

    # ------------------ Knowledge Units ------------------

    def upsert_unit(self, unit: KnowledgeUnit) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO study_units
                (unit_id, concept, unit_type, claims_json, explanation, conditions_json, exceptions_json, evidence_spans_json, source_document_id, importance, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(unit_id) DO UPDATE SET
                    concept = excluded.concept,
                    unit_type = excluded.unit_type,
                    claims_json = excluded.claims_json,
                    explanation = excluded.explanation,
                    conditions_json = excluded.conditions_json,
                    exceptions_json = excluded.exceptions_json,
                    evidence_spans_json = excluded.evidence_spans_json,
                    importance = excluded.importance,
                    difficulty = excluded.difficulty
                """,
                (
                    unit.unit_id,
                    unit.concept,
                    unit.unit_type.value,
                    json.dumps(unit.claims),
                    unit.explanation,
                    json.dumps(unit.conditions),
                    json.dumps(unit.exceptions),
                    json.dumps(unit.evidence_spans),
                    unit.source_document_id,
                    unit.importance,
                    unit.difficulty,
                ),
            )

    def get_unit(self, unit_id: str) -> Optional[KnowledgeUnit]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM study_units WHERE unit_id = ?", (unit_id,)).fetchone()
            if not row:
                return None
            return KnowledgeUnit(
                unit_id=row["unit_id"],
                concept=row["concept"],
                unit_type=UnitType(row["unit_type"]),
                claims=json.loads(row["claims_json"] or "[]"),
                explanation=row["explanation"],
                conditions=json.loads(row["conditions_json"] or "[]"),
                exceptions=json.loads(row["exceptions_json"] or "[]"),
                evidence_spans=json.loads(row["evidence_spans_json"] or "[]"),
                source_document_id=row["source_document_id"],
                importance=row["importance"],
                difficulty=row["difficulty"],
            )

    def list_units_by_document(self, document_id: str) -> List[KnowledgeUnit]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM study_units WHERE source_document_id = ?", (document_id,)
            ).fetchall()
            return [
                KnowledgeUnit(
                    unit_id=r["unit_id"],
                    concept=r["concept"],
                    unit_type=UnitType(r["unit_type"]),
                    claims=json.loads(r["claims_json"] or "[]"),
                    explanation=r["explanation"],
                    conditions=json.loads(r["conditions_json"] or "[]"),
                    exceptions=json.loads(r["exceptions_json"] or "[]"),
                    evidence_spans=json.loads(r["evidence_spans_json"] or "[]"),
                    source_document_id=r["source_document_id"],
                    importance=r["importance"],
                    difficulty=r["difficulty"],
                )
                for r in rows
            ]

    # ------------------ Decks ------------------

    def upsert_deck(self, deck: DeckManifest) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO study_decks
                (deck_id, name, vault_path, category, anki_deck_name, bound_sources_json, revision_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(deck_id) DO UPDATE SET
                    name = excluded.name,
                    vault_path = excluded.vault_path,
                    category = excluded.category,
                    anki_deck_name = excluded.anki_deck_name,
                    bound_sources_json = excluded.bound_sources_json,
                    revision_hash = excluded.revision_hash,
                    updated_at = excluded.updated_at
                """,
                (
                    deck.deck_id,
                    deck.name,
                    deck.vault_path,
                    deck.category,
                    deck.anki_deck_name,
                    json.dumps(deck.bound_sources),
                    deck.revision_hash,
                    deck.created_at,
                    deck.updated_at,
                ),
            )

    def get_deck(self, deck_id: str) -> Optional[DeckManifest]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM study_decks WHERE deck_id = ?", (deck_id,)).fetchone()
            if not row:
                return None
            return DeckManifest(
                deck_id=row["deck_id"],
                name=row["name"],
                vault_path=row["vault_path"],
                category=row["category"],
                anki_deck_name=row["anki_deck_name"],
                bound_sources=json.loads(row["bound_sources_json"] or "[]"),
                revision_hash=row["revision_hash"] or "",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def get_deck_by_name(self, name: str) -> Optional[DeckManifest]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM study_decks WHERE name = ?", (name,)).fetchone()
            if not row:
                return None
            return DeckManifest(
                deck_id=row["deck_id"],
                name=row["name"],
                vault_path=row["vault_path"],
                category=row["category"],
                anki_deck_name=row["anki_deck_name"],
                bound_sources=json.loads(row["bound_sources_json"] or "[]"),
                revision_hash=row["revision_hash"] or "",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    # ------------------ Cards ------------------

    def save_cards(self, cards: List[CardItem]) -> None:
        if not cards:
            return
        with self._get_connection() as conn:
            for c in cards:
                conn.execute(
                    """
                    INSERT INTO study_cards
                    (card_id, deck_id, unit_id, card_type, front, back, tags_json, media_refs_json, evidence_citation, source_file, revision_hash, anki_note_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(card_id) DO UPDATE SET
                        unit_id = excluded.unit_id,
                        card_type = excluded.card_type,
                        front = excluded.front,
                        back = excluded.back,
                        tags_json = excluded.tags_json,
                        media_refs_json = excluded.media_refs_json,
                        evidence_citation = excluded.evidence_citation,
                        source_file = excluded.source_file,
                        revision_hash = excluded.revision_hash,
                        anki_note_id = COALESCE(excluded.anki_note_id, study_cards.anki_note_id),
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        c.card_id,
                        c.deck_id,
                        c.unit_id,
                        c.card_type.value,
                        c.front,
                        c.back,
                        json.dumps(c.tags),
                        json.dumps(c.media_refs),
                        c.evidence_citation,
                        c.source_file,
                        c.revision_hash,
                        c.anki_note_id,
                    ),
                )

    def update_card_anki_id(self, card_id: str, anki_note_id: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE study_cards SET anki_note_id = ?, updated_at = CURRENT_TIMESTAMP WHERE card_id = ?",
                (anki_note_id, card_id),
            )

    def list_cards_by_deck(self, deck_id: str) -> List[CardItem]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM study_cards WHERE deck_id = ? ORDER BY card_id ASC", (deck_id,)
            ).fetchall()
            return [
                CardItem(
                    card_id=r["card_id"],
                    deck_id=r["deck_id"],
                    unit_id=r["unit_id"],
                    card_type=CardType(r["card_type"]),
                    front=r["front"],
                    back=r["back"],
                    tags=json.loads(r["tags_json"] or "[]"),
                    media_refs=json.loads(r["media_refs_json"] or "[]"),
                    evidence_citation=r["evidence_citation"],
                    source_file=r["source_file"],
                    revision_hash=r["revision_hash"],
                    anki_note_id=r["anki_note_id"],
                )
                for r in rows
            ]

    def delete_cards(self, card_ids: List[str]) -> None:
        """Deletes cards from study_cards by their card_ids."""
        if not card_ids:
            return
        with self._get_connection() as conn:
            conn.executemany(
                "DELETE FROM study_cards WHERE card_id = ?",
                [(cid,) for cid in card_ids],
            )

    def add_suppression(self, deck_id: str, card_id: str, reason: str = "user_deleted") -> None:
        """Registers a card as suppressed so it won't be resurrected in future updates."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO study_suppressions (deck_id, card_id, reason) VALUES (?, ?, ?)",
                (deck_id, card_id, reason),
            )

    def list_suppressions(self, deck_id: str) -> Set[str]:
        """Returns the set of suppressed card_ids for a deck."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT card_id FROM study_suppressions WHERE deck_id = ?", (deck_id,)
            ).fetchall()
            return {r["card_id"] for r in rows}

    def remove_suppression(self, deck_id: str, card_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM study_suppressions WHERE deck_id = ? AND card_id = ?",
                (deck_id, card_id),
            )

    # ------------------ Media Assets ------------------

    def upsert_media(
        self,
        media_id: str,
        original_path: str,
        published_path: str,
        byte_size: int,
        mime_type: str,
    ) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO study_media (media_id, original_path, published_path, byte_size, mime_type)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(media_id) DO UPDATE SET
                    original_path = excluded.original_path,
                    published_path = excluded.published_path,
                    byte_size = excluded.byte_size,
                    mime_type = excluded.mime_type
                """,
                (media_id, original_path, published_path, byte_size, mime_type),
            )

    def get_media(self, media_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM study_media WHERE media_id = ?", (media_id,)).fetchone()
            if not row:
                return None
            return dict(row)

    # ------------------ Runs & Work Items ------------------

    def create_run(self, run_id: str, deck_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO study_runs (run_id, deck_id, status) VALUES (?, ?, 'running')",
                (run_id, deck_id),
            )

    def update_run_status(self, run_id: str, status: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE study_runs SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE run_id = ?",
                (status, run_id),
            )

    def add_work_item(self, item: WorkItem) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO study_work_items (work_id, run_id, stage, input_json, status, result_json, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.work_id,
                    item.run_id,
                    item.stage,
                    json.dumps(item.input_data),
                    item.status,
                    json.dumps(item.result) if item.result else None,
                    item.error,
                ),
            )

    def get_pending_work_item(self, run_id: str) -> Optional[WorkItem]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM study_work_items WHERE run_id = ? AND status = 'pending' ORDER BY rowid ASC LIMIT 1",
                (run_id,),
            ).fetchone()
            if not row:
                return None
            return WorkItem(
                work_id=row["work_id"],
                run_id=row["run_id"],
                stage=row["stage"],
                input_data=json.loads(row["input_json"] or "{}"),
                status=row["status"],
                result=json.loads(row["result_json"]) if row["result_json"] else None,
                error=row["error"],
            )

    def complete_work_item(self, work_id: str, result: Dict[str, Any]) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE study_work_items SET status = 'completed', result_json = ? WHERE work_id = ?",
                (json.dumps(result), work_id),
            )

    def fail_work_item(self, work_id: str, error: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE study_work_items SET status = 'failed', error = ? WHERE work_id = ?",
                (error, work_id),
            )

    # ------------------ Transaction Journal ------------------

    def create_tx(self, entry: JournalEntry) -> None:
        """Records a new transaction in PREPARED state."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO study_tx_journal
                (tx_id, deck_id, operation, target_path, staging_path, payload_json, status, created_at, finalized_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.tx_id,
                    entry.deck_id,
                    entry.operation.value,
                    entry.target_path,
                    entry.staging_path,
                    entry.payload_json,
                    entry.status.value,
                    entry.created_at,
                    entry.finalized_at,
                    entry.error_message,
                ),
            )

    def update_tx_status(
        self,
        tx_id: str,
        status: JournalStatus,
        error_message: Optional[str] = None,
        finalized_at: Optional[str] = None,
    ) -> None:
        """Transitions a transaction status (e.g. COMMITTED, ABORTED, RECOVERED)."""
        final_time = finalized_at or time.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE study_tx_journal
                SET status = ?, error_message = ?, finalized_at = ?
                WHERE tx_id = ?
                """,
                (status.value, error_message, final_time, tx_id),
            )

    def get_tx(self, tx_id: str) -> Optional[JournalEntry]:
        """Retrieves a specific transaction record by tx_id."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM study_tx_journal WHERE tx_id = ?",
                (tx_id,),
            ).fetchone()
            if not row:
                return None
            return JournalEntry(
                tx_id=row["tx_id"],
                deck_id=row["deck_id"],
                operation=JournalOperation(row["operation"]),
                target_path=row["target_path"],
                staging_path=row["staging_path"],
                payload_json=row["payload_json"] or "{}",
                status=JournalStatus(row["status"]),
                created_at=row["created_at"],
                finalized_at=row["finalized_at"],
                error_message=row["error_message"],
            )

    def list_pending_transactions(self) -> List[JournalEntry]:
        """Returns all transactions that are still in PREPARED state."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM study_tx_journal WHERE status = 'PREPARED' ORDER BY rowid ASC"
            ).fetchall()
            return [
                JournalEntry(
                    tx_id=r["tx_id"],
                    deck_id=r["deck_id"],
                    operation=JournalOperation(r["operation"]),
                    target_path=r["target_path"],
                    staging_path=r["staging_path"],
                    payload_json=r["payload_json"] or "{}",
                    status=JournalStatus(r["status"]),
                    created_at=r["created_at"],
                    finalized_at=r["finalized_at"],
                    error_message=r["error_message"],
                )
                for r in rows
            ]

