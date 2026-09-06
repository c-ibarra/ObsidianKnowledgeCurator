"""Two-Phase Commit (2PC) Journal & Crash Recovery for Study Decks.

Ensures transactional integrity across SQLite persistence, Obsidian Vault filesystem,
and Spaced Repetition (Anki) state.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import VAULT_ROOT
from src.agent_tools.flashcards.models import (
    CardItem,
    DeckManifest,
    JournalEntry,
    JournalOperation,
    JournalStatus,
)
from src.agent_tools.flashcards.store import StudyStore

logger = logging.getLogger(__name__)


def prepare_deck_transaction(
    store: StudyStore,
    deck_id: str,
    operation: JournalOperation,
    target_vault_path: str,
    content: str,
    manifest_data: Optional[Dict[str, Any]] = None,
    cards_data: Optional[List[Dict[str, Any]]] = None,
    vault_root: Optional[Path] = None,
) -> Tuple[str, Path]:
    """Phase 1: Prepares a transaction by writing to a staging file and logging PREPARED state.

    Returns:
        Tuple of (tx_id, staging_file_path).
    """
    v_root = vault_root or VAULT_ROOT
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"

    target_file = v_root / target_vault_path
    staging_file = target_file.with_name(f"{target_file.name}.{tx_id}.tmp")

    # Ensure parent directory exists
    staging_file.parent.mkdir(parents=True, exist_ok=True)

    # Write staged content to .tmp file
    staging_file.write_text(content, encoding="utf-8")

    # Relative staging path for portable journal records
    try:
        rel_staging = str(staging_file.resolve().relative_to(v_root.resolve()))
    except Exception:
        rel_staging = str(staging_file)

    payload = {
        "manifest": manifest_data or {},
        "cards": cards_data or [],
        "content_length": len(content),
    }

    entry = JournalEntry(
        tx_id=tx_id,
        deck_id=deck_id,
        operation=operation,
        target_path=target_vault_path,
        staging_path=rel_staging,
        payload_json=json.dumps(payload),
        status=JournalStatus.PREPARED,
    )

    store.create_tx(entry)
    return tx_id, staging_file


def commit_deck_transaction(
    store: StudyStore,
    tx_id: str,
    vault_root: Optional[Path] = None,
) -> Path:
    """Phase 2: Atomically applies the staging file to the target and marks COMMITTED.

    Returns:
        The published destination Path.
    """
    v_root = vault_root or VAULT_ROOT
    entry = store.get_tx(tx_id)
    if not entry:
        raise ValueError(f"Transaction {tx_id} not found in journal.")

    if entry.status != JournalStatus.PREPARED:
        raise RuntimeError(f"Cannot commit transaction {tx_id} in state {entry.status}")

    staging_path = v_root / entry.staging_path
    target_path = v_root / entry.target_path

    if not staging_path.exists():
        raise FileNotFoundError(f"Staging file missing for transaction {tx_id}: {staging_path}")

    # Atomic rename/replace on POSIX/OS
    staging_path.replace(target_path)

    store.update_tx_status(tx_id=tx_id, status=JournalStatus.COMMITTED)
    return target_path


def abort_deck_transaction(
    store: StudyStore,
    tx_id: str,
    error_message: Optional[str] = None,
    vault_root: Optional[Path] = None,
) -> None:
    """Rollback: Cleans up any staging file and records ABORTED state in journal."""
    v_root = vault_root or VAULT_ROOT
    entry = store.get_tx(tx_id)
    if not entry:
        return

    staging_path = v_root / entry.staging_path
    if staging_path.exists():
        try:
            staging_path.unlink()
        except OSError as e:
            logger.warning("Failed to remove staging file %s during abort: %s", staging_path, e)

    store.update_tx_status(
        tx_id=tx_id,
        status=JournalStatus.ABORTED,
        error_message=error_message,
    )


def recover_pending_transactions(
    store: StudyStore,
    vault_root: Optional[Path] = None,
    auto_commit_valid: bool = True,
) -> List[Dict[str, Any]]:
    """Scans for dangling PREPARED transactions caused by sudden halts or crashes.

    If auto_commit_valid is True and the staging file is intact, completes the commit.
    Otherwise, cleans up dangling staging files and marks them RECOVERED or ABORTED.
    """
    v_root = vault_root or VAULT_ROOT
    pending = store.list_pending_transactions()
    results: List[Dict[str, Any]] = []

    for tx in pending:
        staging_path = v_root / tx.staging_path
        target_path = v_root / tx.target_path

        if staging_path.exists():
            if auto_commit_valid:
                try:
                    staging_path.replace(target_path)
                    store.update_tx_status(
                        tx_id=tx.tx_id,
                        status=JournalStatus.RECOVERED,
                        error_message="Recovered and committed dangling staging file",
                    )
                    results.append({
                        "tx_id": tx.tx_id,
                        "deck_id": tx.deck_id,
                        "action": "recovered_committed",
                        "target": str(target_path),
                    })
                except Exception as e:
                    store.update_tx_status(
                        tx_id=tx.tx_id,
                        status=JournalStatus.ABORTED,
                        error_message=f"Recovery failed: {e}",
                    )
                    results.append({
                        "tx_id": tx.tx_id,
                        "deck_id": tx.deck_id,
                        "action": "recovery_failed",
                        "error": str(e),
                    })
            else:
                staging_path.unlink(missing_ok=True)
                store.update_tx_status(
                    tx_id=tx.tx_id,
                    status=JournalStatus.ABORTED,
                    error_message="Aborted and cleaned dangling staging file during recovery",
                )
                results.append({
                    "tx_id": tx.tx_id,
                    "deck_id": tx.deck_id,
                    "action": "aborted_cleaned",
                })
        else:
            # Staging file doesn't exist, cannot commit
            store.update_tx_status(
                tx_id=tx.tx_id,
                status=JournalStatus.ABORTED,
                error_message="Staging file was missing during crash recovery",
            )
            results.append({
                "tx_id": tx.tx_id,
                "deck_id": tx.deck_id,
                "action": "aborted_missing_staging",
            })

    return results
