#!/usr/bin/env python3
"""CLI utility for managing Study Decks and Flashcards in Obsidian Knowledge Curator.

Usage:
  uv run python scripts/study_deck.py create --source "<path>" --deck "<name>" [--anki-deck "<anki_name>"] [--no-anki]
  uv run python scripts/study_deck.py status --deck "<name>"
  uv run python scripts/study_deck.py sync-anki --deck "<name>"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import VAULT_ROOT
from src.agent_tools.flashcards.deck import sync_deck_to_anki, write_deck_file
from src.agent_tools.flashcards.engine import (
    run_add_to_deck,
    run_create_deck,
    run_update_deck,
)
from src.agent_tools.flashcards.journal import recover_pending_transactions

from src.agent_tools.flashcards.models import StudyRequest
from src.agent_tools.flashcards.store import StudyStore


def handle_create(args: argparse.Namespace) -> int:
    request = StudyRequest(
        action="create",
        source_path=args.source,
        deck_name=args.deck,
        anki_deck_name=args.anki_deck,
        include_images=not args.no_images,
    )
    sync_anki = not args.no_anki

    print(f"[*] Starting study deck creation: '{args.deck}' from '{args.source}'...")
    try:
        results = run_create_deck(request=request, sync_anki=sync_anki)
    except Exception as e:
        print(f"[!] Error creating study deck: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print("\n" + "=" * 50)
    print("✅ STUDY DECK CREATED SUCCESSFULLY")
    print("=" * 50)
    print(f"• Deck Name        : {results['deck_name']}")
    print(f"• Category         : {results['category']}")
    print(f"• Documents Scanned: {results['documents_scanned']}")
    print(f"• Units Extracted  : {results['units_extracted']}")
    print(f"• Cards Generated  : {results['cards_created']} (Total: {results['total_cards']})")
    print(f"• Target Anki Deck : {results['anki_deck']}")
    
    anki_sync = results.get("anki_sync", {})
    if sync_anki:
        print(f"• Anki Sync Status : {anki_sync.get('notes_added', 0)} notes added, {anki_sync.get('media_stored', 0)} media files stored")
        if anki_sync.get("errors"):
            print(f"  ⚠️ Anki Warnings: {anki_sync['errors']}")
    else:
        print("• Anki Sync Status : Skipped (--no-anki)")

    print(f"\n📁 Obsidian Deck File:")
    print(f"  {results['vault_deck_path']}")
    print("=" * 50)
    return 0


def handle_status(args: argparse.Namespace) -> int:
    store = StudyStore()
    deck = store.get_deck_by_name(args.deck)
    if not deck:
        print(f"[!] Deck '{args.deck}' not found in study state.", file=sys.stderr)
        return 1

    cards = store.list_cards_by_deck(deck.deck_id)
    print(f"\n📊 Deck Status: {deck.name}")
    print(f"• Deck ID        : {deck.deck_id}")
    print(f"• Category       : {deck.category}")
    print(f"• Vault Path     : {deck.vault_path}")
    print(f"• Target Anki    : {deck.anki_deck_name}")
    print(f"• Total Cards    : {len(cards)}")
    synced_count = sum(1 for c in cards if c.anki_note_id)
    print(f"• Synced to Anki : {synced_count}/{len(cards)}")
    return 0


def handle_sync_anki(args: argparse.Namespace) -> int:
    store = StudyStore()
    deck = store.get_deck_by_name(args.deck)
    if not deck:
        print(f"[!] Deck '{args.deck}' not found in study state.", file=sys.stderr)
        return 1

    cards = store.list_cards_by_deck(deck.deck_id)
    print(f"[*] Syncing {len(cards)} cards for deck '{deck.name}' to Anki...")
    res = sync_deck_to_anki(deck, cards)
    store.save_cards(cards)
    write_deck_file(deck, cards)

    print(f"✅ Anki Sync Complete:")
    print(f"• Notes added : {res.get('notes_added', 0)}")
    print(f"• Media stored: {res.get('media_stored', 0)}")
    if res.get("errors"):
        print(f"⚠️ Errors: {res['errors']}")
    return 0


def handle_add(args: argparse.Namespace) -> int:
    request = StudyRequest(
        action="add",
        source_path=args.source,
        deck_name=args.deck,
    )
    sync_anki = not args.no_anki
    print(f"[*] Adding sources from '{args.source}' to existing deck '{args.deck}'...")
    try:
        results = run_add_to_deck(request=request, sync_anki=sync_anki)
    except Exception as e:
        print(f"[!] Error adding sources to deck: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print("\n" + "=" * 50)
    print("✅ SOURCES ADDED TO DECK SUCCESSFULLY")
    print("=" * 50)
    print(f"• Deck Name       : {results['deck_name']}")
    print(f"• New Sources     : {results['new_sources_added']} (Total: {results['total_sources']})")
    print(f"• New Cards Added : {results['new_cards_added']} (Total: {results['total_cards']})")
    anki_sync = results.get("anki_sync", {})
    if sync_anki:
        print(f"• Anki Sync       : {anki_sync.get('notes_added', 0)} notes added")
    print(f"\n📁 Updated Obsidian Deck:")
    print(f"  {results['vault_deck_path']}")
    print("=" * 50)
    return 0


def handle_update(args: argparse.Namespace) -> int:
    sync_anki = not args.no_anki
    force = getattr(args, "force", False)
    print(f"[*] Checking for source changes and updating deck '{args.deck}'...")
    try:
        results = run_update_deck(deck_name=args.deck, sync_anki=sync_anki, force=force)
    except Exception as e:
        print(f"[!] Error updating deck: {e}", file=sys.stderr)
        return 1


    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print("\n" + "=" * 50)
    if results.get("status") == "no-op":
        print("ℹ️ DECK IS ALREADY UP TO DATE")
        print("=" * 50)
        print(f"• {results['message']}")
        print(f"• Total Cards: {results['total_cards']}")
    else:
        print("✅ DECK UPDATED (THREE-WAY MERGE COMPLETE)")
        print("=" * 50)
        print(f"• Deck Name           : {results['deck_name']}")
        print(f"• Total Cards         : {results['total_cards']}")
        print(f"• Anki Cards Updated  : {results['cards_updated_anki']}")
        print(f"• New Cards Added     : {results['new_cards_added']}")
        print(f"• Deleted by User     : {results['cards_deleted_by_user']}")
        print(f"\n📁 Updated Obsidian Deck:")
        print(f"  {results['vault_deck_path']}")
    print("=" * 50)
    return 0


def handle_recover(args: argparse.Namespace) -> int:
    store = StudyStore()
    auto_commit = not args.clean_only
    print("[*] Checking for uncommitted or dangling transactions in journal...")
    results = recover_pending_transactions(store=store, vault_root=VAULT_ROOT, auto_commit_valid=auto_commit)

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print("\n" + "=" * 50)
    if not results:
        print("✅ JOURNAL CLEAN — NO DANGLING TRANSACTIONS FOUND")
        print("=" * 50)
        return 0

    print(f"⚠️ RECOVERED {len(results)} TRANSACTION(S)")
    print("=" * 50)
    for res in results:
        print(f"• TX ID  : {res.get('tx_id')}")
        print(f"  Deck   : {res.get('deck_id')}")
        print(f"  Action : {res.get('action')}")
        if "target" in res:
            print(f"  Target : {res.get('target')}")
        if "error" in res:
            print(f"  Error  : {res.get('error')}")
        print("-" * 40)
    print("=" * 50)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Study Decks & Flashcards CLI for Obsidian Knowledge Curator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Create a new study deck from source notes")
    p_create.add_argument("--source", required=True, help="Path or folder relative to VAULT_ROOT")
    p_create.add_argument("--deck", required=True, help="Deck name (e.g., 'System Design')")
    p_create.add_argument("--anki-deck", default=None, help="Explicit Anki deck name")
    p_create.add_argument("--no-anki", action="store_true", help="Skip direct Anki synchronization")
    p_create.add_argument("--no-images", action="store_true", help="Do not extract or resolve media")
    p_create.add_argument("--json", action="store_true", help="Output results as JSON")

    # add
    p_add = subparsers.add_parser("add", help="Add new source notes to an existing study deck")
    p_add.add_argument("--source", required=True, help="New path or folder relative to VAULT_ROOT")
    p_add.add_argument("--deck", required=True, help="Existing deck name")
    p_add.add_argument("--no-anki", action="store_true", help="Skip direct Anki synchronization")
    p_add.add_argument("--json", action="store_true", help="Output results as JSON")

    # update
    p_update = subparsers.add_parser("update", help="Update deck with source changes and 3-way merge")
    p_update.add_argument("--deck", required=True, help="Existing deck name")
    p_update.add_argument("--force", action="store_true", help="Force re-extraction and 3-way merge even if file mtimes are unchanged")
    p_update.add_argument("--no-anki", action="store_true", help="Skip direct Anki synchronization")
    p_update.add_argument("--json", action="store_true", help="Output results as JSON")


    # status
    p_status = subparsers.add_parser("status", help="Check status of an existing deck")
    p_status.add_argument("--deck", required=True, help="Deck name")

    # sync-anki
    p_sync = subparsers.add_parser("sync-anki", help="Push unsynced cards of a deck to Anki")
    p_sync.add_argument("--deck", required=True, help="Deck name")

    # recover
    p_recover = subparsers.add_parser("recover", help="Recover dangling transactions from the 2PC journal")
    p_recover.add_argument("--clean-only", action="store_true", help="Abort and remove staging files instead of auto-committing")
    p_recover.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if args.command == "create":
        return handle_create(args)
    elif args.command == "add":
        return handle_add(args)
    elif args.command == "update":
        return handle_update(args)
    elif args.command == "status":
        return handle_status(args)
    elif args.command == "sync-anki":
        return handle_sync_anki(args)
    elif args.command == "recover":
        return handle_recover(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())

