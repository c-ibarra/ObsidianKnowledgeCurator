"""Tests for Phase 6: Media management, hash freezing, and visual diagram cards."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.cards import CardType
from src.agent_tools.flashcards.engine import run_create_deck
from src.agent_tools.flashcards.media import (
    freeze_card_media,
    freeze_media_asset,
    generate_diagram_card,
)
from src.agent_tools.flashcards.models import CardItem, StudyRequest
from src.agent_tools.flashcards.store import StudyStore


def test_freeze_media_asset():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        img_dir = v_root / "assets" / "images"
        img_dir.mkdir(parents=True, exist_ok=True)

        sample_img = img_dir / "test_diag.png"
        sample_img.write_bytes(b"\x89PNG\r\n\x1a\nfake_image_bytes_12345")

        db_path = v_root / "study.db"
        store = StudyStore(db_path=db_path)

        record = freeze_media_asset(sample_img, vault_root=v_root, store=store)
        assert record.filename.startswith("study_")
        assert record.filename.endswith(".png")
        assert record.published_path == f"assets/images/study/{record.filename}"

        frozen_file = v_root / record.published_path
        assert frozen_file.exists()
        assert frozen_file.read_bytes() == sample_img.read_bytes()

        # Check SQLite record
        stored_media = store.get_media(record.media_id)
        assert stored_media is not None
        assert stored_media["published_path"] == record.published_path


def test_freeze_card_media():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        img_dir = v_root / "assets" / "images"
        img_dir.mkdir(parents=True, exist_ok=True)

        original_img = img_dir / "architecture.png"
        original_img.write_bytes(b"image_content_abc")

        doc_dir = v_root / "AI Engineer" / "raw"
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_file = doc_dir / "System.md"
        doc_file.write_text("# System", encoding="utf-8")

        card = CardItem.create(
            deck_id="deck_test",
            front="Observa el diagrama: ![[architecture.png]]",
            back="Flujo de datos.",
            media_refs=["architecture.png"],
        )

        db_path = v_root / "study.db"
        store = StudyStore(db_path=db_path)

        frozen_card = freeze_card_media(card, doc_path=doc_file, vault_root=v_root, store=store)
        assert "architecture.png" not in frozen_card.front
        assert "assets/images/study/study_" in frozen_card.front
        assert any("assets/images/study/study_" in ref for ref in frozen_card.media_refs)


def test_generate_diagram_card():
    card = generate_diagram_card(
        concept="Replicación Primario-Secundario",
        explanation="El primario procesa escrituras y replica el WAL a réplicas asíncronas.",
        image_ref="assets/images/study/study_123456789abc.png",
        deck_id="deck_test",
        unit_id="ku_diag_1",
    )
    assert card.card_type == CardType.BASIC
    assert "diagram" in card.tags
    assert "![[assets/images/study/study_123456789abc.png]]" in card.front
    assert "Replicación Primario-Secundario" in card.front
    assert "asíncronas" in card.back


def test_end_to_end_media_in_run_create_deck():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        img_dir = v_root / "assets" / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        test_img = img_dir / "network_flow.png"
        test_img.write_bytes(b"network_flow_binary_data")

        note_dir = v_root / "AI Engineer" / "raw"
        note_dir.mkdir(parents=True, exist_ok=True)
        note_file = note_dir / "Networking.md"
        note_file.write_text(
            """# Networking Protocols

## 1. Flow Diagram
- **TCP Handshake**: SYN -> SYN-ACK -> ACK.

![[network_flow.png]]
""",
            encoding="utf-8",
        )

        db_path = v_root / "study.db"
        store = StudyStore(db_path=db_path)

        req = StudyRequest(
            action="create",
            source_path=str(note_dir),
            deck_name="Networking Deck",
        )

        res = run_create_deck(req, store=store, vault_root=v_root, sync_anki=False)
        assert res["cards_created"] >= 1

        # Verify frozen image in study folder
        study_img_dir = v_root / "assets" / "images" / "study"
        assert study_img_dir.exists()
        frozen_files = list(study_img_dir.glob("study_*.png"))
        assert len(frozen_files) == 1

        # Check generated deck file content
        deck_content = Path(res["vault_deck_path"]).read_text(encoding="utf-8")
        assert "assets/images/study/study_" in deck_content
