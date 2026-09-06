"""Tests for card quality, deduplication, and markdown deck rendering."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.cards import (
    deduplicate_cards,
    generate_cards_from_unit,
    validate_card_quality,
)
from src.agent_tools.flashcards.deck import (
    render_markdown_deck,
    write_deck_file,
)
from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
    KnowledgeUnit,
    UnitType,
)


def test_validate_card_quality():
    # Valid basic
    valid, err = validate_card_quality("¿Qué es un Reverse Proxy?", "Un servidor que intercepta peticiones cliente.", CardType.BASIC)
    assert valid is True
    assert err is None

    # Vague deictic reference rejected
    valid, err = validate_card_quality("¿Qué es esto?", "Una respuesta.", CardType.BASIC)
    assert valid is False
    assert "vague deictic reference" in err.lower()

    # Invalid cloze without {{c1::...}}
    valid, err = validate_card_quality("Texto sin cloze", "Contexto", CardType.CLOZE)
    assert valid is False
    assert "cloze" in err.lower()

    # Valid cloze
    valid, err = validate_card_quality("El protocolo {{c1::HTTP/2}} soporta multiplexación.", "Contexto", CardType.CLOZE)
    assert valid is True


def test_deduplicate_cards():
    deck_id = "deck_test"
    c1 = CardItem.create(deck_id=deck_id, front="Pregunta 1", back="Respuesta 1")
    c2 = CardItem.create(deck_id=deck_id, front="Pregunta 2", back="Respuesta 2")
    c1_dup = CardItem.create(deck_id=deck_id, front="Pregunta 1", back="Respuesta 1")

    unique, duplicates = deduplicate_cards([c1, c2, c1_dup], existing_cards=[])
    assert len(unique) == 2
    assert len(duplicates) == 1
    assert duplicates[0].front == "Pregunta 1"


def test_render_and_write_markdown_deck():
    manifest = DeckManifest.create(
        name="Distributed Systems",
        vault_path="AI Engineer/study/Distributed Systems.md",
        category="AI Engineer",
        anki_deck_name="Machine Learning::Distributed Systems",
        bound_sources=["AI Engineer/raw/dist_sys.md"],
    )

    card1 = CardItem.create(
        deck_id=manifest.deck_id,
        front="¿Qué garantiza el teorema CAP?",
        back="Que en una red particionada se debe elegir entre consistencia y disponibilidad.",
        unit_id="ku_cap_1",
    )
    card1.anki_note_id = 1725599999999

    card2 = CardItem.create(
        deck_id=manifest.deck_id,
        front="En sistemas distribuidos, el teorema {{c1::CAP}} define el compromiso entre C, A y P.",
        back="Consistencia, Disponibilidad, Tolerancia a Particiones",
        card_type=CardType.CLOZE,
        unit_id="ku_cap_2",
    )

    content = render_markdown_deck(manifest, [card1, card2])
    assert "# Study Deck — Distributed Systems" in content
    assert "> Target Anki Deck: Machine Learning::Distributed Systems" in content
    assert "Q: ¿Qué garantiza el teorema CAP?" in content
    assert "<!-- id: " in content
    assert "anki_id: 1725599999999" in content
    assert "unit: ku_cap_1" in content
    assert "{{c1::CAP}}" in content

    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        written_path = write_deck_file(manifest, [card1, card2], vault_root=v_root)
        assert written_path.exists()
        assert written_path.read_text(encoding="utf-8") == content
