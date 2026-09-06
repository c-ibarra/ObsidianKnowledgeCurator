"""High-level coordinator engine for Study Decks & Flashcards."""

from __future__ import annotations

import hashlib
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import VAULT_ROOT
from src.agent_tools.flashcards.cards import (
    deduplicate_cards,
    generate_cards_from_unit,
    plan_three_way_merge,
    validate_card_quality,
)
from src.agent_tools.flashcards.deck import (
    parse_markdown_deck,
    render_markdown_deck,
    sync_deck_to_anki,
    update_anki_note_fields,
    write_deck_file,
)
from src.agent_tools.flashcards.journal import (
    abort_deck_transaction,
    commit_deck_transaction,
    prepare_deck_transaction,
    recover_pending_transactions,
)

from src.agent_tools.flashcards.knowledge import (
    extract_deterministic_units,
)
from src.agent_tools.flashcards.media import (
    freeze_card_media,
    generate_diagram_card,
)
from src.agent_tools.flashcards.models import (
    CardItem,
    DeckManifest,
    JournalOperation,
    KnowledgeUnit,
    StudyRequest,
)

from src.agent_tools.flashcards.sources import (
    extract_media_references,
    parse_markdown_document,
    scan_scope,
)
from src.agent_tools.flashcards.store import StudyStore


def infer_deck_category(source_path: Path, vault_root: Path) -> str:
    """Infers high-level vault category from source path (e.g., 'AI Engineer', 'software engineer')."""
    try:
        rel = source_path.resolve().relative_to(vault_root.resolve())
        parts = rel.parts
        # If path is dataScienceKnowledgeBase/<Category>/...
        if len(parts) >= 2 and parts[0] == "dataScienceKnowledgeBase":
            return parts[1]
        elif len(parts) >= 1:
            return parts[0]
    except ValueError:
        pass
    return "General"


def run_create_deck(
    request: StudyRequest,
    store: Optional[StudyStore] = None,
    vault_root: Optional[Path] = None,
    sync_anki: bool = True,
) -> Dict[str, Any]:
    """Executes the complete creation pipeline for a new study deck."""
    v_root = vault_root or VAULT_ROOT
    db = store or StudyStore()
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # 1. Scan and validate scope
    source_files = scan_scope(request.source_path, vault_root=v_root)
    if not source_files:
        raise ValueError(f"No valid markdown source files found in: {request.source_path}")

    # Determine category & paths
    first_file = source_files[0]
    category = infer_deck_category(first_file, v_root)
    
    # Path inside vault: e.g. "dataScienceKnowledgeBase/AI Engineer/study/My Deck.md"
    # or "<category>/study/My Deck.md"
    rel_first = first_file.resolve().relative_to(v_root.resolve())
    if rel_first.parts[0] == "dataScienceKnowledgeBase" and len(rel_first.parts) >= 2:
        root_folder = f"dataScienceKnowledgeBase/{rel_first.parts[1]}"
    else:
        root_folder = rel_first.parts[0]

    vault_deck_path = f"{root_folder}/study/{request.deck_name}.md"

    # Determine Anki deck name
    anki_deck = request.anki_deck_name or f"{category}::{request.deck_name}"

    bound_sources: List[str] = []
    all_units: List[KnowledgeUnit] = []

    # 2. Parse documents & extract units
    doc_path_by_id: Dict[str, Path] = {}
    doc_spans_by_id: Dict[str, List] = {}
    for f in source_files:
        doc, sections, spans = parse_markdown_document(f, vault_root=v_root)
        db.upsert_document(doc)
        db.save_spans(spans)
        bound_sources.append(doc.vault_path)
        doc_path_by_id[doc.document_id] = f
        doc_spans_by_id[doc.document_id] = spans

        # Extract units
        units = extract_deterministic_units(spans, document_id=doc.document_id)
        for u in units:
            db.upsert_unit(u)
            all_units.append(u)

    # 3. Create Deck Manifest
    manifest = DeckManifest.create(
        name=request.deck_name,
        vault_path=vault_deck_path,
        category=category,
        anki_deck_name=anki_deck,
        bound_sources=bound_sources,
    )
    db.upsert_deck(manifest)
    db.create_run(run_id=run_id, deck_id=manifest.deck_id)

    # 4. Generate Cards
    existing_cards = db.list_cards_by_deck(manifest.deck_id)
    candidate_cards: List[CardItem] = []

    for unit in all_units:
        doc_file = doc_path_by_id.get(unit.source_document_id, first_file)
        cards = generate_cards_from_unit(unit, deck_id=manifest.deck_id, source_file=unit.source_document_id)
        for c in cards:
            c = freeze_card_media(c, doc_path=doc_file, vault_root=v_root, store=db)
            media_refs = extract_media_references(c.front + " " + c.back)
            if media_refs:
                c.media_refs = media_refs

            valid, _err = validate_card_quality(c.front, c.back, c.card_type)
            if valid:
                candidate_cards.append(c)

    # Generate dedicated visual diagram cards for all images found in documents
    seen_doc_images = set()
    for doc_id, spans in doc_spans_by_id.items():
        doc_file = doc_path_by_id.get(doc_id, first_file)
        for s in spans:
            for img_ref in extract_media_references(s.text_content):
                if img_ref not in seen_doc_images:
                    seen_doc_images.add(img_ref)
                    matching_unit = next((u for u in all_units if u.source_document_id == doc_id), None)
                    concept_name = matching_unit.concept if matching_unit else s.heading_path.split(" / ")[-1]
                    expl = matching_unit.explanation if matching_unit else f"Diagrama arquitectónico de {concept_name}."
                    diag_card = generate_diagram_card(
                        concept=concept_name,
                        explanation=expl,
                        image_ref=img_ref,
                        deck_id=manifest.deck_id,
                        unit_id=matching_unit.unit_id if matching_unit else None,
                        source_file=doc_id,
                    )
                    diag_card = freeze_card_media(diag_card, doc_path=doc_file, vault_root=v_root, store=db)
                    candidate_cards.append(diag_card)

    unique_cards, skipped_duplicates = deduplicate_cards(candidate_cards, existing_cards)
    all_final_cards = existing_cards + unique_cards

    # 5. Anki MCP Synchronization
    anki_results = {"deck_created": False, "notes_added": 0, "media_stored": 0, "errors": []}
    if sync_anki and unique_cards:
        try:
            anki_results = sync_deck_to_anki(manifest, unique_cards)
        except Exception as e:
            anki_results["errors"].append(str(e))

    # 6. Save cards to store
    db.save_cards(all_final_cards)

    # 7. Write Markdown file to Obsidian Vault via 2PC Journal
    deck_content = render_markdown_deck(manifest, all_final_cards)
    tx_id, _ = prepare_deck_transaction(
        store=db,
        deck_id=manifest.deck_id,
        operation=JournalOperation.CREATE_DECK,
        target_vault_path=manifest.vault_path,
        content=deck_content,
        vault_root=v_root,
    )

    try:
        output_file = commit_deck_transaction(store=db, tx_id=tx_id, vault_root=v_root)
    except Exception as e:
        abort_deck_transaction(store=db, tx_id=tx_id, error_message=str(e), vault_root=v_root)
        raise

    db.update_run_status(run_id=run_id, status="completed")


    return {
        "run_id": run_id,
        "deck_id": manifest.deck_id,
        "deck_name": manifest.name,
        "category": category,
        "vault_deck_path": str(output_file),
        "documents_scanned": len(source_files),
        "units_extracted": len(all_units),
        "cards_created": len(unique_cards),
        "duplicates_skipped": len(skipped_duplicates),
        "total_cards": len(all_final_cards),
        "anki_deck": anki_deck,
        "anki_sync": anki_results,
    }


def run_add_to_deck(
    request: StudyRequest,
    store: Optional[StudyStore] = None,
    vault_root: Optional[Path] = None,
    sync_anki: bool = True,
) -> Dict[str, Any]:
    """Adds a new source file or folder to an existing study deck without overwriting existing cards."""
    v_root = vault_root or VAULT_ROOT
    db = store or StudyStore()

    manifest = db.get_deck_by_name(request.deck_name)
    if not manifest:
        raise ValueError(f"Study deck '{request.deck_name}' does not exist in store. Use 'create' first.")

    source_files = scan_scope(request.source_path, vault_root=v_root)
    if not source_files:
        raise ValueError(f"No valid markdown source files found in: {request.source_path}")

    # Read current cards from deck file
    deck_path = v_root / manifest.vault_path
    if deck_path.exists():
        user_cards = parse_markdown_deck(deck_path.read_text(encoding="utf-8"), deck_id=manifest.deck_id)
    else:
        user_cards = []

    db_cards = db.list_cards_by_deck(manifest.deck_id)
    suppressed = db.list_suppressions(manifest.deck_id)

    new_sources: List[str] = list(manifest.bound_sources)
    candidate_cards: List[CardItem] = []

    for f in source_files:
        doc, sections, spans = parse_markdown_document(f, vault_root=v_root)
        db.upsert_document(doc)
        db.save_spans(spans)
        if doc.vault_path not in new_sources:
            new_sources.append(doc.vault_path)

        units = extract_deterministic_units(spans, document_id=doc.document_id)
        for u in units:
            db.upsert_unit(u)
            cards = generate_cards_from_unit(u, deck_id=manifest.deck_id, source_file=doc.vault_path)
            for c in cards:
                c = freeze_card_media(c, doc_path=f, vault_root=v_root, store=db)
                media_refs = extract_media_references(c.front + " " + c.back)
                if media_refs:
                    c.media_refs = media_refs
                valid, _ = validate_card_quality(c.front, c.back, c.card_type)
                if valid:
                    candidate_cards.append(c)

    manifest.bound_sources = new_sources
    manifest.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    db.upsert_deck(manifest)

    final_cards, cards_to_update_anki, deleted_ids = plan_three_way_merge(
        db_cards=db_cards,
        user_cards=user_cards if user_cards else db_cards,
        proposed_cards=candidate_cards,
        suppressed_ids=suppressed,
    )

    if deleted_ids:
        for cid in deleted_ids:
            db.add_suppression(manifest.deck_id, cid)
        db.delete_cards(deleted_ids)

    # Sync only genuinely new cards to Anki
    cards_to_add_anki = [c for c in final_cards if not c.anki_note_id]
    anki_results = {"deck_created": False, "notes_added": 0, "media_stored": 0, "errors": []}
    if sync_anki and cards_to_add_anki:
        try:
            anki_results = sync_deck_to_anki(manifest, cards_to_add_anki)
        except Exception as e:
            anki_results["errors"].append(str(e))

    db.save_cards(final_cards)

    # Write Markdown file via 2PC Journal
    deck_content = render_markdown_deck(manifest, final_cards)
    tx_id, _ = prepare_deck_transaction(
        store=db,
        deck_id=manifest.deck_id,
        operation=JournalOperation.ADD_TO_DECK,
        target_vault_path=manifest.vault_path,
        content=deck_content,
        vault_root=v_root,
    )

    try:
        output_file = commit_deck_transaction(store=db, tx_id=tx_id, vault_root=v_root)
    except Exception as e:
        abort_deck_transaction(store=db, tx_id=tx_id, error_message=str(e), vault_root=v_root)
        raise


    return {
        "action": "add",
        "deck_id": manifest.deck_id,
        "deck_name": manifest.name,
        "new_sources_added": len(source_files),
        "total_sources": len(manifest.bound_sources),
        "new_cards_added": len(cards_to_add_anki),
        "total_cards": len(final_cards),
        "vault_deck_path": str(output_file),
        "anki_sync": anki_results,
    }


def run_update_deck(
    deck_name: str,
    store: Optional[StudyStore] = None,
    vault_root: Optional[Path] = None,
    sync_anki: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    """Updates an existing deck using Three-Way Merge:


    - Preserves human edits in Markdown.
    - Suppresses cards deleted by user.
    - Re-extracts and updates only changed sources.
    - Syncs field updates to Anki without resetting SRS review history.
    """
    v_root = vault_root or VAULT_ROOT
    db = store or StudyStore()

    manifest = db.get_deck_by_name(deck_name)
    if not manifest:
        raise ValueError(f"Study deck '{deck_name}' does not exist.")

    deck_path = v_root / manifest.vault_path
    if not deck_path.exists():
        raise FileNotFoundError(f"Deck Markdown file not found in vault: {deck_path}")

    user_cards = parse_markdown_deck(deck_path.read_text(encoding="utf-8"), deck_id=manifest.deck_id)
    db_cards = db.list_cards_by_deck(manifest.deck_id)
    suppressed = db.list_suppressions(manifest.deck_id)

    # Check for changes in bound source files
    changed_sources: List[Path] = []
    for s_path_str in manifest.bound_sources:
        s_path = v_root / s_path_str
        if not s_path.exists():
            continue
        curr_doc = db.get_document_by_path(s_path_str)
        curr_bytes = s_path.read_bytes()
        curr_hash = hashlib.sha256(curr_bytes).hexdigest()
        if not curr_doc or curr_doc.byte_hash != curr_hash or s_path.stat().st_mtime != curr_doc.mtime:
            changed_sources.append(s_path)

    # Check if user made any edits compared to DB
    user_edits_detected = False
    db_card_map = {c.card_id: c for c in db_cards}
    if len(user_cards) != len(db_cards):
        user_edits_detected = True
    else:
        for uc in user_cards:
            dbc = db_card_map.get(uc.card_id)
            if not dbc or uc.front != dbc.front or uc.back != dbc.back:
                user_edits_detected = True
                break

    # If no source changed and no user edits, return no-op unless force=True
    if not force and not changed_sources and not user_edits_detected:
        return {
            "action": "update",
            "status": "no-op",
            "message": "No changes detected in source notes or deck. Everything is up to date.",
            "deck_name": deck_name,
            "total_cards": len(db_cards),
        }


    # Re-parse changed sources or all sources if units need refresh
    all_candidate_cards: List[CardItem] = []
    for s_path_str in manifest.bound_sources:
        s_path = v_root / s_path_str
        if not s_path.exists():
            continue
        doc, sections, spans = parse_markdown_document(s_path, vault_root=v_root)
        db.upsert_document(doc)
        db.save_spans(spans)

        units = extract_deterministic_units(spans, document_id=doc.document_id)
        for u in units:
            db.upsert_unit(u)
            cards = generate_cards_from_unit(u, deck_id=manifest.deck_id, source_file=doc.vault_path)
            for c in cards:
                c = freeze_card_media(c, doc_path=s_path, vault_root=v_root, store=db)
                media_refs = extract_media_references(c.front + " " + c.back)
                if media_refs:
                    c.media_refs = media_refs
                valid, _ = validate_card_quality(c.front, c.back, c.card_type)
                if valid:
                    all_candidate_cards.append(c)

    final_cards, cards_to_update_anki, deleted_ids = plan_three_way_merge(
        db_cards=db_cards,
        user_cards=user_cards,
        proposed_cards=all_candidate_cards,
        suppressed_ids=suppressed,
    )

    # Record suppressions and remove from DB
    if deleted_ids:
        for cid in deleted_ids:
            db.add_suppression(manifest.deck_id, cid)
        db.delete_cards(deleted_ids)

    # Update modified cards in Anki via updateNoteFields
    anki_updated_count = 0
    if sync_anki:
        for c in cards_to_update_anki:
            if c.anki_note_id:
                ok = update_anki_note_fields(c.anki_note_id, c.front, c.back, c.card_type)
                if ok:
                    anki_updated_count += 1

    # Check if there are newly added cards that need initial Anki sync
    cards_to_add_anki = [c for c in final_cards if not c.anki_note_id]
    if sync_anki and cards_to_add_anki:
        sync_deck_to_anki(manifest, cards_to_add_anki)

    db.save_cards(final_cards)
    manifest.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    db.upsert_deck(manifest)

    # Write Markdown file via 2PC Journal
    deck_content = render_markdown_deck(manifest, final_cards)
    tx_id, _ = prepare_deck_transaction(
        store=db,
        deck_id=manifest.deck_id,
        operation=JournalOperation.UPDATE_DECK,
        target_vault_path=manifest.vault_path,
        content=deck_content,
        vault_root=v_root,
    )

    try:
        output_file = commit_deck_transaction(store=db, tx_id=tx_id, vault_root=v_root)
    except Exception as e:
        abort_deck_transaction(store=db, tx_id=tx_id, error_message=str(e), vault_root=v_root)
        raise


    return {
        "action": "update",
        "status": "updated",
        "deck_name": deck_name,
        "total_cards": len(final_cards),
        "cards_updated_anki": anki_updated_count,
        "new_cards_added": len(cards_to_add_anki),
        "cards_deleted_by_user": len(deleted_ids),
        "vault_deck_path": str(output_file),
    }
