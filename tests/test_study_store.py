"""Tests for StudyStore SQLite persistence."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
    KnowledgeUnit,
    SourceDocument,
    SourceSpan,
    UnitType,
    WorkItem,
)
from src.agent_tools.flashcards.store import StudyStore


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_study.db"
        store = StudyStore(db_path=db_path)
        yield store


def test_upsert_document_and_spans(temp_store):
    doc = SourceDocument.create(
        vault_path="AI Engineer/raw/test.md",
        content_bytes=b"# Test\nHello world",
        mtime=123456.0,
        title="Test Doc",
    )
    temp_store.upsert_document(doc)

    fetched = temp_store.get_document_by_path("AI Engineer/raw/test.md")
    assert fetched is not None
    assert fetched.document_id == doc.document_id
    assert fetched.byte_hash == doc.byte_hash

    span = SourceSpan.create(
        document_id=doc.document_id,
        heading_path="Test Doc / Intro",
        start_line=1,
        end_line=2,
        text="Hello world",
    )
    temp_store.save_spans([span])

    spans = temp_store.get_spans_by_document(doc.document_id)
    assert len(spans) == 1
    assert spans[0].text_content == "Hello world"
    assert spans[0].span_id == span.span_id


def test_upsert_and_list_units(temp_store):
    doc = SourceDocument.create(
        vault_path="AI Engineer/raw/test.md",
        content_bytes=b"Content",
        mtime=123.0,
    )
    temp_store.upsert_document(doc)

    unit = KnowledgeUnit.create(
        concept="Write-Ahead Logging",
        explanation="Technique to ensure atomicity and durability in DBMS.",
        source_document_id=doc.document_id,
        unit_type=UnitType.DEFINITION,
        claims=["Logs changes before writing to disk"],
    )
    temp_store.upsert_unit(unit)

    fetched = temp_store.get_unit(unit.unit_id)
    assert fetched is not None
    assert fetched.concept == "Write-Ahead Logging"
    assert fetched.unit_type == UnitType.DEFINITION
    assert fetched.claims == ["Logs changes before writing to disk"]

    units = temp_store.list_units_by_document(doc.document_id)
    assert len(units) == 1
    assert units[0].unit_id == unit.unit_id


def test_deck_and_cards_lifecycle(temp_store):
    deck = DeckManifest.create(
        name="System Design Fundamentals",
        vault_path="AI Engineer/study/System Design Fundamentals.md",
        category="AI Engineer",
        anki_deck_name="Machine Learning::System Design",
    )
    temp_store.upsert_deck(deck)

    fetched_deck = temp_store.get_deck(deck.deck_id)
    assert fetched_deck is not None
    assert fetched_deck.name == "System Design Fundamentals"

    card = CardItem.create(
        deck_id=deck.deck_id,
        front="¿Qué es WAL?",
        back="Write-Ahead Logging para garantizar durabilidad.",
        card_type=CardType.BASIC,
    )
    temp_store.save_cards([card])

    cards = temp_store.list_cards_by_deck(deck.deck_id)
    assert len(cards) == 1
    assert cards[0].front == "¿Qué es WAL?"
    assert cards[0].anki_note_id is None

    # Update Anki Note ID
    temp_store.update_card_anki_id(card.card_id, 1725500000000)
    cards_updated = temp_store.list_cards_by_deck(deck.deck_id)
    assert cards_updated[0].anki_note_id == 1725500000000


def test_runs_and_work_items(temp_store):
    temp_store.create_run("run_123", "deck_abc")
    work = WorkItem(
        work_id="work_1",
        run_id="run_123",
        stage="extract_units",
        input_data={"section": "Intro"},
    )
    temp_store.add_work_item(work)

    pending = temp_store.get_pending_work_item("run_123")
    assert pending is not None
    assert pending.work_id == "work_1"

    temp_store.complete_work_item("work_1", {"units_found": 3})
    assert temp_store.get_pending_work_item("run_123") is None
