"""Tests for Phase 5: Three-Way Merge, ADD, UPDATE, and Markdown Deck Parsing."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.cards import plan_three_way_merge
from src.agent_tools.flashcards.deck import parse_markdown_deck, render_markdown_deck
from src.agent_tools.flashcards.engine import (
    run_add_to_deck,
    run_create_deck,
    run_update_deck,
)
from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
    StudyRequest,
)
from src.agent_tools.flashcards.store import StudyStore


def test_parse_markdown_deck():
    sample = """# Study Deck — Test Deck

> **Curated Study Deck — Test Deck**
> Category: AI Engineer · Cards: 3 · Processed: 05-09-2026

## Flashcards

Q: ¿Qué es MapReduce?
A: Un modelo de programación para procesamiento distribuido.
<!-- id: card_123 anki_id: 1725511111111 rev: rev_aaa unit: ku_1 -->

**Cloze Card**:
El teorema {{c1::CAP}} equilibra consistencia y disponibilidad.
> Context: Sistemas distribuidos
<!-- id: card_456 anki_id: 1725522222222 rev: rev_bbb unit: ku_2 -->

Q: Tarjeta Legacy sin comentario
A: Respuesta legacy
"""
    cards = parse_markdown_deck(sample, deck_id="deck_test")
    assert len(cards) == 3

    # Card 1: Basic with metadata
    c1 = cards[0]
    assert c1.card_id == "card_123"
    assert c1.anki_note_id == 1725511111111
    assert c1.front == "¿Qué es MapReduce?"
    assert c1.back == "Un modelo de programación para procesamiento distribuido."
    assert c1.card_type == CardType.BASIC

    # Card 2: Cloze with metadata
    c2 = cards[1]
    assert c2.card_id == "card_456"
    assert c2.anki_note_id == 1725522222222
    assert "{{c1::CAP}}" in c2.front
    assert c2.card_type == CardType.CLOZE

    # Card 3: Legacy without comment
    c3 = cards[2]
    assert "card_legacy" in c3.card_id
    assert c3.front == "Tarjeta Legacy sin comentario"
    assert c3.back == "Respuesta legacy"


def test_plan_three_way_merge_preserves_user_edit():
    c_orig = CardItem.create(
        deck_id="deck_1",
        front="¿Qué es WAL?",
        back="Write-Ahead Logging.",
        unit_id="ku_wal",
    )
    c_orig.card_id = "card_wal_1"
    c_orig.anki_note_id = 999

    # User manually edited the answer in Markdown
    c_user = CardItem.create(
        deck_id="deck_1",
        front="¿Qué es WAL?",
        back="Write-Ahead Logging para durabilidad ACID (editado por Carlos).",
        unit_id="ku_wal",
    )
    c_user.card_id = "card_wal_1"
    c_user.anki_note_id = 999

    # Source generator suggests something else
    c_proposed = CardItem.create(
        deck_id="deck_1",
        front="¿Qué es WAL?",
        back="Técnica de logging de transacciones en DBMS.",
        unit_id="ku_wal",
    )
    c_proposed.card_id = "card_wal_1"

    final_cards, to_update_anki, deleted_ids = plan_three_way_merge(
        db_cards=[c_orig],
        user_cards=[c_user],
        proposed_cards=[c_proposed],
    )

    assert len(final_cards) == 1
    assert "editado por Carlos" in final_cards[0].back
    assert final_cards[0].anki_note_id == 999
    assert len(to_update_anki) == 1
    assert to_update_anki[0].card_id == "card_wal_1"
    assert len(deleted_ids) == 0


def test_plan_three_way_merge_user_deletion():
    c1 = CardItem.create(deck_id="deck_1", front="Q1", back="A1")
    c1.card_id = "card_1"
    c2 = CardItem.create(deck_id="deck_1", front="Q2", back="A2")
    c2.card_id = "card_2"

    # User deleted c2 from markdown deck
    user_cards = [c1]
    proposed_cards = [c1, c2]

    final_cards, to_update_anki, deleted_ids = plan_three_way_merge(
        db_cards=[c1, c2],
        user_cards=user_cards,
        proposed_cards=proposed_cards,
    )

    assert len(final_cards) == 1
    assert final_cards[0].card_id == "card_1"
    assert "card_2" in deleted_ids


def test_plan_three_way_merge_source_update():
    c1 = CardItem.create(deck_id="deck_1", front="Q1", back="Old Answer")
    c1.card_id = "card_1"
    c1.anki_note_id = 888

    # User didn't edit card
    c_user = CardItem.create(deck_id="deck_1", front="Q1", back="Old Answer")
    c_user.card_id = "card_1"
    c_user.anki_note_id = 888

    # Source updated the answer
    c_proposed = CardItem.create(deck_id="deck_1", front="Q1", back="Updated Answer from Source")
    c_proposed.card_id = "card_1"

    final_cards, to_update_anki, deleted_ids = plan_three_way_merge(
        db_cards=[c1],
        user_cards=[c_user],
        proposed_cards=[c_proposed],
    )

    assert len(final_cards) == 1
    assert final_cards[0].back == "Updated Answer from Source"
    assert len(to_update_anki) == 1
    assert to_update_anki[0].anki_note_id == 888


def test_run_add_and_update_deck_e2e():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        raw_dir = v_root / "AI Engineer" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)

        f1 = raw_dir / "Source1.md"
        f1.write_text(
            """# Source 1
## Definitions
- **Consistency**: All nodes see the same data simultaneously.
""",
            encoding="utf-8",
        )

        db_path = v_root / "study.db"
        store = StudyStore(db_path=db_path)

        # 1. Create deck with Source1
        req_create = StudyRequest(
            action="create",
            source_path=str(f1),
            deck_name="System Concepts",
        )
        res_create = run_create_deck(req_create, store=store, vault_root=v_root, sync_anki=False)
        assert res_create["cards_created"] >= 1
        initial_cards = res_create["cards_created"]

        # 2. Add Source2
        f2 = raw_dir / "Source2.md"
        f2.write_text(
            """# Source 2
## Definitions
- **Availability**: Every non-failing node returns a response.
""",
            encoding="utf-8",
        )

        req_add = StudyRequest(
            action="add",
            source_path=str(f2),
            deck_name="System Concepts",
        )
        res_add = run_add_to_deck(req_add, store=store, vault_root=v_root, sync_anki=False)
        assert res_add["new_cards_added"] >= 1
        assert res_add["total_cards"] > initial_cards

        # 3. Test Update with No-Op
        res_update_noop = run_update_deck("System Concepts", store=store, vault_root=v_root, sync_anki=False)
        assert res_update_noop["status"] == "no-op"

        # 4. Modify Source1 and run Update
        f1.write_text(
            """# Source 1
## Definitions
- **Consistency**: Strict linearizability across distributed nodes.
""",
            encoding="utf-8",
        )
        res_update = run_update_deck("System Concepts", store=store, vault_root=v_root, sync_anki=False)
        assert res_update["status"] == "updated"
