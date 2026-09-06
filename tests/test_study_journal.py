"""Tests for Two-Phase Commit (2PC) Journal and Crash Recovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from src.agent_tools.flashcards.journal import (
    abort_deck_transaction,
    commit_deck_transaction,
    prepare_deck_transaction,
    recover_pending_transactions,
)
from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
    JournalEntry,
    JournalOperation,
    JournalStatus,
    StudyRequest,
)
from src.agent_tools.flashcards.engine import run_create_deck, run_update_deck
from src.agent_tools.flashcards.store import StudyStore


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "test_vault"
    vault.mkdir(parents=True, exist_ok=True)
    return vault


@pytest.fixture
def test_store(tmp_path: Path) -> StudyStore:
    db_path = tmp_path / "test_study.db"
    return StudyStore(db_path=db_path)


def test_prepare_and_commit_transaction_lifecycle(test_store: StudyStore, tmp_vault: Path):
    target_rel = "dataScienceKnowledgeBase/AI Engineer/study/Test Deck.md"
    content = "# Study Deck — Test Deck\n\nQ: What is 2PC?\nA: Two phase commit.\n"

    # 1. Prepare
    tx_id, staging_file = prepare_deck_transaction(
        store=test_store,
        deck_id="deck_123",
        operation=JournalOperation.CREATE_DECK,
        target_vault_path=target_rel,
        content=content,
        vault_root=tmp_vault,
    )

    assert tx_id.startswith("tx_")
    assert staging_file.exists()
    assert staging_file.read_text(encoding="utf-8") == content

    # Verify journal entry in DB
    tx = test_store.get_tx(tx_id)
    assert tx is not None
    assert tx.status == JournalStatus.PREPARED
    assert tx.deck_id == "deck_123"

    pending = test_store.list_pending_transactions()
    assert len(pending) == 1
    assert pending[0].tx_id == tx_id

    # 2. Commit
    published = commit_deck_transaction(store=test_store, tx_id=tx_id, vault_root=tmp_vault)
    assert published == tmp_vault / target_rel
    assert published.exists()
    assert not staging_file.exists()

    # Verify DB marked as COMMITTED
    tx_committed = test_store.get_tx(tx_id)
    assert tx_committed.status == JournalStatus.COMMITTED
    assert len(test_store.list_pending_transactions()) == 0


def test_abort_transaction(test_store: StudyStore, tmp_vault: Path):
    target_rel = "AI Engineer/study/Abort Deck.md"
    content = "Some content that fails validation"

    tx_id, staging_file = prepare_deck_transaction(
        store=test_store,
        deck_id="deck_abort",
        operation=JournalOperation.CREATE_DECK,
        target_vault_path=target_rel,
        content=content,
        vault_root=tmp_vault,
    )
    assert staging_file.exists()

    # Abort
    abort_deck_transaction(
        store=test_store,
        tx_id=tx_id,
        error_message="Simulated failure before publication",
        vault_root=tmp_vault,
    )

    assert not staging_file.exists()
    tx = test_store.get_tx(tx_id)
    assert tx.status == JournalStatus.ABORTED
    assert "Simulated failure" in tx.error_message
    assert len(test_store.list_pending_transactions()) == 0


def test_crash_recovery_auto_commit(test_store: StudyStore, tmp_vault: Path):
    target_rel = "AI Engineer/study/Crash Deck.md"
    content = "# Recovered Content\n\nQ: Crash?\nA: Recovered."

    tx_id, staging_file = prepare_deck_transaction(
        store=test_store,
        deck_id="deck_crash",
        operation=JournalOperation.CREATE_DECK,
        target_vault_path=target_rel,
        content=content,
        vault_root=tmp_vault,
    )
    assert staging_file.exists()

    # Simulate sudden crash: process dies right after prepare_deck_transaction
    # Run recovery with auto_commit_valid=True
    recovered = recover_pending_transactions(store=test_store, vault_root=tmp_vault, auto_commit_valid=True)
    assert len(recovered) == 1
    assert recovered[0]["action"] == "recovered_committed"
    assert recovered[0]["tx_id"] == tx_id

    # The file should now be in target position
    target_file = tmp_vault / target_rel
    assert target_file.exists()
    assert not staging_file.exists()
    assert target_file.read_text(encoding="utf-8") == content

    # Status in journal should be RECOVERED
    tx = test_store.get_tx(tx_id)
    assert tx.status == JournalStatus.RECOVERED
    assert len(test_store.list_pending_transactions()) == 0


def test_crash_recovery_clean_only(test_store: StudyStore, tmp_vault: Path):
    target_rel = "AI Engineer/study/Clean Deck.md"
    content = "# Staging Content To Discard"

    tx_id, staging_file = prepare_deck_transaction(
        store=test_store,
        deck_id="deck_clean",
        operation=JournalOperation.CREATE_DECK,
        target_vault_path=target_rel,
        content=content,
        vault_root=tmp_vault,
    )
    assert staging_file.exists()

    # Recovery with auto_commit_valid=False (clean-only)
    recovered = recover_pending_transactions(store=test_store, vault_root=tmp_vault, auto_commit_valid=False)
    assert len(recovered) == 1
    assert recovered[0]["action"] == "aborted_cleaned"

    assert not staging_file.exists()
    assert not (tmp_vault / target_rel).exists()

    tx = test_store.get_tx(tx_id)
    assert tx.status == JournalStatus.ABORTED
    assert len(test_store.list_pending_transactions()) == 0


def test_engine_run_create_deck_uses_journal(test_store: StudyStore, tmp_vault: Path):
    source_dir = tmp_vault / "dataScienceKnowledgeBase" / "AI Engineer" / "raw" / "TestCat"
    source_dir.mkdir(parents=True, exist_ok=True)
    note_file = source_dir / "Note 1.md"
    note_file.write_text(
        """# Raft Consensus Protocol

> **Ongaro & Ousterhout — In Search of an Understandable Consensus Algorithm**
> Date: 2014 · Type: paper · Tags: #no-read-yet

## 📌 Key Takeaways
1. **Raft Protocol**: A distributed consensus algorithm designed for understandability.
2. **Leader Election**: Uses randomized timers to elect a strong leader.

## 1. Core Concepts
- **Log Replication**: The leader receives log entries from clients and replicates them across followers.
- **Heartbeat Mechanism**: Periodic empty append entries sent to prevent new elections.
""",
        encoding="utf-8",
    )

    req = StudyRequest(
        action="create",
        source_path="dataScienceKnowledgeBase/AI Engineer/raw/TestCat",
        deck_name="Raft Study",
    )


    res = run_create_deck(request=req, store=test_store, vault_root=tmp_vault, sync_anki=False)
    assert res["cards_created"] > 0

    # Ensure journal was written and COMMITTED
    with test_store._get_connection() as conn:
        rows = conn.execute("SELECT * FROM study_tx_journal WHERE deck_id = ?", (res["deck_id"],)).fetchall()
        assert len(rows) >= 1
        last_row = rows[-1]
        assert last_row["status"] == "COMMITTED"
        assert last_row["operation"] == "CREATE_DECK"
