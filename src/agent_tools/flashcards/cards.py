"""Card formulation, validation, and deduplication engine."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    KnowledgeUnit,
    UnitType,
)


def validate_card_quality(front: str, back: str, card_type: CardType) -> Tuple[bool, Optional[str]]:
    """Checks pedagogical quality and atomicity based on SuperMemo principles."""
    f = front.strip()
    b = back.strip()

    if not f:
        return False, "Front cannot be empty"
    if not b:
        return False, "Back cannot be empty"

    if card_type == CardType.CLOZE:
        if not re.search(r"\{\{c\d+::.+?\}\}", f) and not re.search(r"\{\{c\d+::.+?\}\}", b):
            return False, "Cloze card must contain deletion syntax '{{c1::...}}'"
        return True, None

    # Basic card checks
    if len(f) < 5:
        return False, "Question is too short / ambiguous"
    if len(b) < 3:
        return False, "Answer is too short"

    # Avoid vague deictic references
    vague_starters = ("¿qué es esto?", "¿qué significa esto?", "¿cómo funciona esto?", "what is this?", "how does it work?")
    if f.lower() in vague_starters:
        return False, "Question lacks context (vague deictic reference)"

    return True, None


def deduplicate_cards(
    new_cards: List[CardItem],
    existing_cards: List[CardItem],
) -> Tuple[List[CardItem], List[CardItem]]:
    """Separates new unique cards from already existing duplicates."""
    seen_hashes: Set[str] = {c.revision_hash for c in existing_cards}
    seen_ids: Set[str] = {c.card_id for c in existing_cards}

    unique_cards: List[CardItem] = []
    skipped_duplicates: List[CardItem] = []

    for card in new_cards:
        if card.card_id in seen_ids or card.revision_hash in seen_hashes:
            skipped_duplicates.append(card)
        else:
            seen_ids.add(card.card_id)
            seen_hashes.add(card.revision_hash)
            unique_cards.append(card)

    return unique_cards, skipped_duplicates


def generate_cards_from_unit(
    unit: KnowledgeUnit,
    deck_id: str,
    source_file: Optional[str] = None,
) -> List[CardItem]:
    """Generates atomic, pedagogical flashcards from a validated KnowledgeUnit."""
    cards: List[CardItem] = []
    concept = unit.concept.strip()
    explanation = unit.explanation.strip()
    evidence = unit.evidence_spans[0] if unit.evidence_spans else None

    tags = ["study-deck"]
    if unit.unit_type == UnitType.FORMULA:
        tags.append("math")
    elif unit.unit_type == UnitType.PROCESS:
        tags.append("process")

    # 1. Primary Concept Card (Basic)
    if unit.unit_type == UnitType.QUESTION:
        front = concept
        back = explanation
    elif unit.unit_type == UnitType.DEFINITION:
        front = f"¿Qué es y cuál es la función principal de **{concept}**?"
        back = explanation
    elif unit.unit_type == UnitType.FORMULA:
        front = f"¿Cuál es la formulación matemática y el propósito de **{concept}**?"
        back = explanation
    elif unit.unit_type == UnitType.PROCESS:
        front = f"¿Cómo se describe el proceso de **{concept}** y cuáles son sus fases clave?"
        back = explanation
    elif unit.unit_type == UnitType.CAUSALITY:
        front = f"¿Cuál es la causa y el impacto principal asociado a **{concept}**?"
        back = explanation
    else:
        front = f"En el contexto de la arquitectura técnica, ¿qué define a **{concept}**?"
        back = explanation


    card1 = CardItem.create(
        deck_id=deck_id,
        front=front,
        back=back,
        card_type=CardType.BASIC,
        unit_id=unit.unit_id,
        tags=tags,
        source_file=source_file,
        evidence_citation=evidence,
    )
    cards.append(card1)

    # 2. Cloze Card for concise definitions or conditions
    if len(explanation.split()) <= 40 and unit.unit_type in (UnitType.DEFINITION, UnitType.FACT):
        # Find key term or concept in explanation or cloze the concept itself
        cloze_front = f"**{concept}**: {explanation}"
        # Wrap the concept in cloze
        cloze_card_text = f"**{{{{c1::{concept}}}}}**: {explanation}"
        card_cloze = CardItem.create(
            deck_id=deck_id,
            front=cloze_card_text,
            back=explanation,
            card_type=CardType.CLOZE,
            unit_id=unit.unit_id,
            tags=tags + ["cloze"],
            source_file=source_file,
            evidence_citation=evidence,
        )
        cards.append(card_cloze)

    return cards


def plan_three_way_merge(
    db_cards: List[CardItem],
    user_cards: List[CardItem],
    proposed_cards: List[CardItem],
    suppressed_ids: Optional[Set[str]] = None,
) -> Tuple[List[CardItem], List[CardItem], List[str]]:
    """Performs a 3-way merge between:
    - db_cards: baseline in SQLite
    - user_cards: current markdown file (with possible human edits / deletions)
    - proposed_cards: newly generated candidates from updated sources

    Returns:
    - final_cards: complete list of cards to render and persist
    - cards_to_update_anki: cards whose text changed and need an update in Anki
    - deleted_card_ids: card IDs deleted by user to suppress in DB
    """
    suppressed = suppressed_ids or set()
    db_map = {c.card_id: c for c in db_cards}
    user_map = {c.card_id: c for c in user_cards}
    proposed_map = {c.card_id: c for c in proposed_cards}

    final_cards: List[CardItem] = []
    cards_to_update_anki: List[CardItem] = []
    deleted_card_ids: List[str] = []

    # 1. Process cards that were in db_cards
    for c_id, db_card in db_map.items():
        if c_id not in user_map:
            # User explicitly removed it from the markdown deck
            deleted_card_ids.append(c_id)
            continue

        u_card = user_map[c_id]
        if db_card.anki_note_id and not u_card.anki_note_id:
            u_card.anki_note_id = db_card.anki_note_id

        # Did the user edit front or back?
        if u_card.front != db_card.front or u_card.back != db_card.back:
            # Human edit takes priority over generator
            refreshed = CardItem.create(
                deck_id=u_card.deck_id,
                front=u_card.front,
                back=u_card.back,
                card_type=u_card.card_type,
                unit_id=u_card.unit_id or db_card.unit_id,
                source_file=db_card.source_file,
            )
            refreshed.card_id = c_id
            refreshed.anki_note_id = u_card.anki_note_id
            final_cards.append(refreshed)
            if refreshed.anki_note_id:
                cards_to_update_anki.append(refreshed)
        else:
            # User did not modify it. Did the source propose an update?
            if c_id in proposed_map and proposed_map[c_id].revision_hash != db_card.revision_hash:
                prop_card = proposed_map[c_id]
                prop_card.anki_note_id = db_card.anki_note_id
                final_cards.append(prop_card)
                if prop_card.anki_note_id:
                    cards_to_update_anki.append(prop_card)
            else:
                final_cards.append(db_card)

    # 2. Process user manual cards (cards present in markdown but never in DB)
    for c_id, u_card in user_map.items():
        if c_id not in db_map:
            final_cards.append(u_card)

    # 3. Process new cards from proposed_cards
    for c_id, prop_card in proposed_map.items():
        if c_id not in db_map and c_id not in user_map and c_id not in suppressed and c_id not in deleted_card_ids:
            final_cards.append(prop_card)

    return final_cards, cards_to_update_anki, deleted_card_ids
