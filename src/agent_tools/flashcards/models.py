"""Data models for Study Decks & Flashcards in Obsidian Knowledge Curator."""

from __future__ import annotations

import hashlib
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CardType(str, Enum):
    BASIC = "Basic"
    CLOZE = "Cloze"


class UnitType(str, Enum):
    DEFINITION = "definition"
    PROCESS = "process"
    CAUSALITY = "causality"
    CONTRAST = "contrast"
    FORMULA = "formula"
    FACT = "fact"
    QUESTION = "question"



class SourceDocument(BaseModel):
    """Represents a source file inside the Obsidian Vault."""
    document_id: str
    vault_path: str
    byte_hash: str
    mtime: float
    title: Optional[str] = None
    format: str = "markdown"

    @classmethod
    def create(cls, vault_path: str, content_bytes: bytes, mtime: float, title: Optional[str] = None) -> SourceDocument:
        byte_hash = hashlib.sha256(content_bytes).hexdigest()
        doc_id = hashlib.sha256(vault_path.encode("utf-8")).hexdigest()[:16]
        return cls(
            document_id=doc_id,
            vault_path=vault_path,
            byte_hash=byte_hash,
            mtime=mtime,
            title=title or vault_path.split("/")[-1].replace(".md", ""),
            format="markdown",
        )


class SourceSpan(BaseModel):
    """An exact, verifiable content slice within a source document."""
    span_id: str
    document_id: str
    heading_path: str
    start_line: int
    end_line: int
    text_content: str
    content_digest: str

    @classmethod
    def create(cls, document_id: str, heading_path: str, start_line: int, end_line: int, text: str) -> SourceSpan:
        digest = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]
        span_id = f"span_{document_id[:8]}_{start_line}_{digest[:8]}"
        return cls(
            span_id=span_id,
            document_id=document_id,
            heading_path=heading_path,
            start_line=start_line,
            end_line=end_line,
            text_content=text,
            content_digest=digest,
        )


class SectionNode(BaseModel):
    """A structural section extracted from an AST."""
    section_id: str
    document_id: str
    heading_text: str
    heading_level: int
    parent_section_id: Optional[str] = None
    spans: List[SourceSpan] = Field(default_factory=list)


class KnowledgeUnit(BaseModel):
    """An atomic, evidence-backed conceptual unit extracted from sources."""
    unit_id: str
    concept: str
    unit_type: UnitType = UnitType.DEFINITION
    claims: List[str] = Field(default_factory=list)
    explanation: str
    conditions: List[str] = Field(default_factory=list)
    exceptions: List[str] = Field(default_factory=list)
    evidence_spans: List[str] = Field(default_factory=list)  # List of span_ids
    source_document_id: str
    importance: int = Field(default=3, ge=1, le=5)
    difficulty: int = Field(default=3, ge=1, le=5)

    @classmethod
    def create(
        cls,
        concept: str,
        explanation: str,
        source_document_id: str,
        unit_type: UnitType = UnitType.DEFINITION,
        claims: Optional[List[str]] = None,
        evidence_spans: Optional[List[str]] = None,
    ) -> KnowledgeUnit:
        normalized_concept = concept.strip().lower()
        seed = f"{normalized_concept}:{source_document_id}"
        unit_id = f"ku_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:12]}"
        return cls(
            unit_id=unit_id,
            concept=concept.strip(),
            unit_type=unit_type,
            claims=claims or [],
            explanation=explanation.strip(),
            evidence_spans=evidence_spans or [],
            source_document_id=source_document_id,
        )


class CardItem(BaseModel):
    """A single flashcard ready for Obsidian rendering and Anki synchronization."""
    card_id: str
    deck_id: str
    unit_id: Optional[str] = None
    card_type: CardType = CardType.BASIC
    front: str
    back: str
    tags: List[str] = Field(default_factory=list)
    media_refs: List[str] = Field(default_factory=list)
    evidence_citation: Optional[str] = None
    source_file: Optional[str] = None
    revision_hash: str = ""
    anki_note_id: Optional[int] = None

    @classmethod
    def create(
        cls,
        deck_id: str,
        front: str,
        back: str,
        card_type: CardType = CardType.BASIC,
        unit_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        media_refs: Optional[List[str]] = None,
        source_file: Optional[str] = None,
        evidence_citation: Optional[str] = None,
    ) -> CardItem:
        normalized = f"{front.strip()}|{back.strip()}|{card_type.value}"
        rev_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
        card_id = f"card_{hashlib.sha256((deck_id + ':' + normalized).encode('utf-8')).hexdigest()[:12]}"
        return cls(
            card_id=card_id,
            deck_id=deck_id,
            unit_id=unit_id,
            card_type=card_type,
            front=front.strip(),
            back=back.strip(),
            tags=tags or [],
            media_refs=media_refs or [],
            source_file=source_file,
            evidence_citation=evidence_citation,
            revision_hash=rev_hash,
        )


class DeckManifest(BaseModel):
    """Metadata and bindings for an Obsidian study deck."""
    deck_id: str
    name: str
    vault_path: str
    category: str
    anki_deck_name: str
    bound_sources: List[str] = Field(default_factory=list)
    card_ids: List[str] = Field(default_factory=list)
    revision_hash: str = ""
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    @classmethod
    def create(
        cls,
        name: str,
        vault_path: str,
        category: str,
        anki_deck_name: str,
        bound_sources: Optional[List[str]] = None,
    ) -> DeckManifest:
        deck_id = f"deck_{hashlib.sha256(vault_path.encode('utf-8')).hexdigest()[:12]}"
        return cls(
            deck_id=deck_id,
            name=name,
            vault_path=vault_path,
            category=category,
            anki_deck_name=anki_deck_name,
            bound_sources=bound_sources or [],
        )


class WorkItem(BaseModel):
    """An executable stage item dispatched for semantic processing."""
    work_id: str
    run_id: str
    stage: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # "pending", "completed", "failed"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StudyRequest(BaseModel):
    """CLI / Agent input parameters for study deck operations."""
    action: str = "create"
    source_path: str
    deck_name: str
    anki_deck_name: Optional[str] = None
    include_images: bool = True


class JournalStatus(str, Enum):
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    RECOVERED = "RECOVERED"


class JournalOperation(str, Enum):
    CREATE_DECK = "CREATE_DECK"
    UPDATE_DECK = "UPDATE_DECK"
    ADD_TO_DECK = "ADD_TO_DECK"


class JournalEntry(BaseModel):
    """A durable transaction record coordinating SQLite and filesystem state."""
    tx_id: str
    deck_id: str
    operation: JournalOperation
    target_path: str
    staging_path: str
    payload_json: str = "{}"
    status: JournalStatus = JournalStatus.PREPARED
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    finalized_at: Optional[str] = None
    error_message: Optional[str] = None

