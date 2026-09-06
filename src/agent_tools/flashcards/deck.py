"""Obsidian Markdown rendering and direct Anki synchronization for Study Decks."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import VAULT_ROOT, ASSETS_IMAGES_DIR
from src.agent_tools.flashcards.models import (
    CardItem,
    CardType,
    DeckManifest,
)


def render_markdown_deck(manifest: DeckManifest, cards: List[CardItem]) -> str:
    """Renders a curated study deck into clean, canonical Obsidian Markdown."""
    processed_date = time.strftime("%d-%m-%Y")
    lines: List[str] = [
        f"# Study Deck — {manifest.name}",
        "",
        f"> **Curated Study Deck — {manifest.name}**",
    ]

    if manifest.bound_sources:
        sources_str = " · ".join(f"[[{s}]]" for s in manifest.bound_sources[:3])
        if len(manifest.bound_sources) > 3:
            sources_str += f" (+{len(manifest.bound_sources) - 3} more)"
        lines.append(f"> Source: {sources_str}")

    lines.extend([
        f"> Target Anki Deck: {manifest.anki_deck_name}",
        f"> Category: {manifest.category} · Cards: {len(cards)} · Processed: {processed_date}",
        "> Type: study-deck",
        "> Tags: #study-deck #anki #no-read-yet",
        "",
        "## Flashcards",
        "",
    ])

    for card in cards:
        anki_part = f" anki_id: {card.anki_note_id}" if card.anki_note_id else ""
        unit_part = f" unit: {card.unit_id}" if card.unit_id else ""
        comment = f"<!-- id: {card.card_id}{anki_part} rev: {card.revision_hash}{unit_part} -->"

        if card.card_type == CardType.CLOZE:
            lines.append(f"**Cloze Card**:")
            lines.append(card.front)
            if card.back and card.back != card.front:
                lines.append(f"> Context: {card.back}")
            lines.append(comment)
            lines.append("")
        else:
            lines.append(f"Q: {card.front}")
            lines.append(f"A: {card.back}")
            lines.append(comment)
            lines.append("")

    if manifest.bound_sources:
        lines.append("## Sources")
        for s in manifest.bound_sources:
            lines.append(f"- [[{s}]]")
        lines.append("")

    return "\n".join(lines)


def write_deck_file(
    manifest: DeckManifest,
    cards: List[CardItem],
    vault_root: Optional[Path] = None,
    store: Optional[Any] = None,
    tx_id: Optional[str] = None,
) -> Path:
    """Writes the rendered deck file to the Obsidian Vault atomically."""
    v_root = vault_root or VAULT_ROOT
    deck_path = v_root / manifest.vault_path
    deck_path.parent.mkdir(parents=True, exist_ok=True)

    content = render_markdown_deck(manifest, cards)
    
    # Atomic write using a temporary file in the same directory before rename
    tmp_path = deck_path.with_suffix(f".tmp.{time.time_ns()}")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(deck_path)
    return deck_path



def _call_anki_connect(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    anki_url: str = "http://127.0.0.1:8765",
) -> Any:
    """Dispatches a JSON-RPC request to AnkiConnect."""
    payload = {
        "action": action,
        "version": 6,
        "params": params or {},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        anki_url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("error"):
                raise RuntimeError(f"AnkiConnect error on {action}: {res['error']}")
            return res.get("result")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Could not connect to Anki at {anki_url}. Is Anki open with AnkiConnect installed? Error: {e}")


def sync_deck_to_anki(
    manifest: DeckManifest,
    cards: List[CardItem],
    anki_url: str = "http://127.0.0.1:8765",
) -> Dict[str, Any]:
    """Syncs cards and media assets directly to Anki via AnkiConnect."""
    results: Dict[str, Any] = {
        "deck_created": False,
        "notes_added": 0,
        "media_stored": 0,
        "errors": [],
    }

    # 1. Create or ensure deck exists
    try:
        _call_anki_connect("createDeck", {"deck": manifest.anki_deck_name}, anki_url=anki_url)
        results["deck_created"] = True
    except Exception as e:
        results["errors"].append(f"createDeck: {e}")

    # 2. Upload referenced media files
    stored_media = set()
    for card in cards:
        for media_ref in card.media_refs:
            clean_name = Path(media_ref).name
            if clean_name not in stored_media:
                media_path = ASSETS_IMAGES_DIR / "study" / clean_name
                if not media_path.exists():
                    media_path = ASSETS_IMAGES_DIR / clean_name
                if not media_path.exists():
                    media_path = VAULT_ROOT / media_ref

                if media_path.exists():
                    try:
                        _call_anki_connect(
                            "storeMediaFile",
                            {"filename": clean_name, "path": str(media_path.resolve())},
                            anki_url=anki_url,
                        )
                        stored_media.add(clean_name)
                        results["media_stored"] += 1
                    except Exception as e:
                        results["errors"].append(f"storeMediaFile({clean_name}): {e}")

    # 3. Add notes in batches
    basic_cards = [c for c in cards if c.card_type == CardType.BASIC and not c.anki_note_id]
    cloze_cards = [c for c in cards if c.card_type == CardType.CLOZE and not c.anki_note_id]

    # Process Basic cards
    if basic_cards:
        notes_payload = []
        for c in basic_cards:
            front_text = c.front
            back_text = c.back
            # Convert embedded image markdown ![[foo.png]] to <img src="foo.png"> for Anki
            for m in c.media_refs:
                img_tag = f'<br><img src="{Path(m).name}">'
                front_text = front_text.replace(f"![[{m}]]", img_tag)
                back_text = back_text.replace(f"![[{m}]]", img_tag)

            notes_payload.append({
                "deckName": manifest.anki_deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": front_text.replace("\n", "<br>"),
                    "Back": back_text.replace("\n", "<br>"),
                },
                "options": {
                    "allowDuplicate": True,
                    "duplicateScope": "deck",
                },
                "tags": c.tags + [manifest.category.replace(" ", "-"), "okc-curated"],
            })

        try:
            res_ids = _call_anki_connect("addNotes", {"notes": notes_payload}, anki_url=anki_url)

            if isinstance(res_ids, list):
                for card_obj, note_id in zip(basic_cards, res_ids):
                    if note_id:
                        card_obj.anki_note_id = note_id
                        results["notes_added"] += 1
        except Exception as e:
            results["errors"].append(f"addNotes(Basic): {e}")

    # Process Cloze cards
    if cloze_cards:
        cloze_payload = []
        for c in cloze_cards:
            text_val = c.front
            for m in c.media_refs:
                img_tag = f'<br><img src="{Path(m).name}">'
                text_val = text_val.replace(f"![[{m}]]", img_tag)

            cloze_payload.append({
                "deckName": manifest.anki_deck_name,
                "modelName": "Cloze",
                "fields": {
                    "Text": text_val.replace("\n", "<br>"),
                    "Back Extra": (c.back or "").replace("\n", "<br>"),
                },
                "tags": c.tags + [manifest.category.replace(" ", "-"), "okc-curated"],
            })

        try:
            res_ids = _call_anki_connect("addNotes", {"notes": cloze_payload}, anki_url=anki_url)
            if isinstance(res_ids, list):
                for card_obj, note_id in zip(cloze_cards, res_ids):
                    if note_id:
                        card_obj.anki_note_id = note_id
                        results["notes_added"] += 1
        except Exception as e:
            results["errors"].append(f"addNotes(Cloze): {e}")

    return results


def update_anki_note_fields(
    anki_note_id: int,
    front: str,
    back: str,
    card_type: CardType,
    anki_url: str = "http://127.0.0.1:8765",
) -> bool:
    """Updates fields of an existing note in Anki via AnkiConnect without losing SRS history."""
    if card_type == CardType.CLOZE:
        fields = {"Text": front.replace("\n", "<br>"), "Back Extra": (back or "").replace("\n", "<br>")}
    else:
        fields = {"Front": front.replace("\n", "<br>"), "Back": back.replace("\n", "<br>")}

    try:
        _call_anki_connect(
            "updateNoteFields",
            {"note": {"id": anki_note_id, "fields": fields}},
            anki_url=anki_url,
        )
        return True
    except Exception:
        return False


_COMMENT_RE = re.compile(
    r"<!--\s*(?:type:\s*(?P<type>\w+)\s+)?id:\s*(?P<id>[\w\-]+)(?:\s+anki_id:\s*(?P<anki_id>\d+))?(?:\s+rev:\s*(?P<rev>[\w\-]+))?(?:\s+unit:\s*(?P<unit>[\w\-]+))?\s*-->"
)


def parse_markdown_deck(content: str, deck_id: str = "") -> List[CardItem]:
    """Parses an existing study deck Markdown file into CardItem objects,

    preserving IDs, Anki Note IDs, revision hashes, and human edits.
    """
    cards: List[CardItem] = []
    lines = content.splitlines()
    i = 0
    in_flashcards = False

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## Flashcards"):
            in_flashcards = True
            i += 1
            continue
        elif in_flashcards and line.startswith("## "):
            break

        if not in_flashcards:
            i += 1
            continue

        # Basic card: Q: ... / A: ...
        if line.startswith("Q:"):
            front = line[2:].strip()
            back = ""
            comment_match = None
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("A:") and not lines[i].strip().startswith("Q:") and not lines[i].strip().startswith("##"):
                if lines[i].strip():
                    front += "\n" + lines[i].strip()
                i += 1

            if i < len(lines) and lines[i].strip().startswith("A:"):
                back = lines[i].strip()[2:].strip()
                i += 1
                while i < len(lines):
                    l_sub = lines[i].strip()
                    m = _COMMENT_RE.search(l_sub)
                    if m:
                        comment_match = m
                        i += 1
                        break
                    elif l_sub.startswith("Q:") or l_sub.startswith("##") or l_sub.startswith("**Cloze Card**:"):
                        break
                    elif l_sub:
                        back += "\n" + l_sub
                    i += 1

            if comment_match:
                c_id = comment_match.group("id")
                anki_id = int(comment_match.group("anki_id")) if comment_match.group("anki_id") else None
                rev = comment_match.group("rev") or ""
                unit_id = comment_match.group("unit")
            else:
                c_id = f"card_legacy_{hashlib.sha256((deck_id + ':' + front).encode('utf-8')).hexdigest()[:12]}"
                anki_id = None
                rev = hashlib.sha256(f"{front}|{back}|Basic".encode("utf-8")).hexdigest()[:12]
                unit_id = None

            card = CardItem.create(
                deck_id=deck_id,
                front=front,
                back=back,
                card_type=CardType.BASIC,
                unit_id=unit_id,
            )
            card.card_id = c_id
            card.anki_note_id = anki_id
            card.revision_hash = rev
            cards.append(card)
            continue

        # Cloze card
        if line.startswith("**Cloze Card**:"):
            i += 1
            cloze_front = ""
            cloze_back = ""
            comment_match = None

            while i < len(lines):
                l_sub = lines[i].strip()
                m = _COMMENT_RE.search(l_sub)
                if m:
                    comment_match = m
                    i += 1
                    break
                elif l_sub.startswith("Q:") or l_sub.startswith("##") or l_sub.startswith("**Cloze Card**:"):
                    break
                elif l_sub.startswith("> Context:"):
                    cloze_back = l_sub[10:].strip()
                elif l_sub:
                    if cloze_front:
                        cloze_front += "\n" + l_sub
                    else:
                        cloze_front = l_sub
                i += 1

            if cloze_front:
                if comment_match:
                    c_id = comment_match.group("id")
                    anki_id = int(comment_match.group("anki_id")) if comment_match.group("anki_id") else None
                    rev = comment_match.group("rev") or ""
                    unit_id = comment_match.group("unit")
                else:
                    c_id = f"card_cloze_{hashlib.sha256((deck_id + ':' + cloze_front).encode('utf-8')).hexdigest()[:12]}"
                    anki_id = None
                    rev = hashlib.sha256(f"{cloze_front}|{cloze_back}|Cloze".encode("utf-8")).hexdigest()[:12]
                    unit_id = None

                card = CardItem.create(
                    deck_id=deck_id,
                    front=cloze_front,
                    back=cloze_back or cloze_front,
                    card_type=CardType.CLOZE,
                    unit_id=unit_id,
                )
                card.card_id = c_id
                card.anki_note_id = anki_id
                card.revision_hash = rev
                cards.append(card)
                continue

        i += 1

    return cards
