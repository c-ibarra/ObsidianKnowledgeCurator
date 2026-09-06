"""Media management, SHA-256 hash freezing, and visual diagram card formulation."""

from __future__ import annotations

import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.config import VAULT_ROOT
from src.agent_tools.flashcards.models import CardItem, CardType
from src.agent_tools.flashcards.sources import (
    extract_media_references,
    resolve_media_path,
)
from src.agent_tools.flashcards.store import StudyStore


class MediaAssetRecord(BaseModel):
    """Metadata record for a frozen study media asset."""
    media_id: str
    original_path: str
    published_path: str
    byte_size: int
    mime_type: str
    filename: str


def freeze_media_asset(
    original_file: Path,
    vault_root: Optional[Path] = None,
    store: Optional[StudyStore] = None,
) -> MediaAssetRecord:
    """Freezes an image by copying it into assets/images/study/ named by its SHA-256 digest."""
    v_root = vault_root or VAULT_ROOT
    if not original_file.exists():
        raise FileNotFoundError(f"Media file does not exist: {original_file}")

    content_bytes = original_file.read_bytes()
    digest = hashlib.sha256(content_bytes).hexdigest()
    ext = original_file.suffix.lower() or ".png"
    target_filename = f"study_{digest[:12]}{ext}"

    target_dir = v_root / "assets" / "images" / "study"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / target_filename

    if not target_path.exists():
        shutil.copy2(original_file, target_path)

    mime_type, _ = mimetypes.guess_type(str(original_file))
    mime_type = mime_type or "application/octet-stream"
    published_rel_path = f"assets/images/study/{target_filename}"

    record = MediaAssetRecord(
        media_id=digest,
        original_path=str(original_file),
        published_path=published_rel_path,
        byte_size=len(content_bytes),
        mime_type=mime_type,
        filename=target_filename,
    )

    if store:
        store.upsert_media(
            media_id=digest,
            original_path=str(original_file),
            published_path=published_rel_path,
            byte_size=len(content_bytes),
            mime_type=mime_type,
        )

    return record


def freeze_card_media(
    card: CardItem,
    doc_path: Path,
    vault_root: Optional[Path] = None,
    store: Optional[StudyStore] = None,
) -> CardItem:
    """Inspects card front/back and media_refs, freezes all referenced images to assets/images/study/,

    and updates the markdown references to the immutable canonical path.
    """
    v_root = vault_root or VAULT_ROOT
    all_refs = extract_media_references(card.front + " " + card.back + " " + " ".join(card.media_refs))
    if not all_refs:
        return card

    frozen_refs: List[str] = []
    new_front = card.front
    new_back = card.back

    for ref in all_refs:
        resolved = resolve_media_path(ref, doc_path=doc_path, vault_root=v_root)
        if resolved and resolved.exists():
            asset = freeze_media_asset(resolved, vault_root=v_root, store=store)
            frozen_rel = asset.published_path
            frozen_refs.append(frozen_rel)

            # Replace markdown references
            new_front = new_front.replace(f"![[{ref}]]", f"![[{frozen_rel}]]")
            new_front = new_front.replace(f"({ref})", f"({frozen_rel})")
            new_back = new_back.replace(f"![[{ref}]]", f"![[{frozen_rel}]]")
            new_back = new_back.replace(f"({ref})", f"({frozen_rel})")
        else:
            frozen_refs.append(ref)

    card.front = new_front
    card.back = new_back
    card.media_refs = sorted(list(set(frozen_refs)))
    return card


def generate_diagram_card(
    concept: str,
    explanation: str,
    image_ref: str,
    deck_id: str,
    unit_id: Optional[str] = None,
    source_file: Optional[str] = None,
) -> CardItem:
    """Formulates a visual diagram flashcard presenting the diagram on the front

    and querying the key architectural flows or components.
    """
    front = (
        f"¿Qué componentes, flujos o relaciones clave ilustra este diagrama de **{concept}**?\n\n"
        f"![[{image_ref}]]"
    )
    back = explanation.strip()
    return CardItem.create(
        deck_id=deck_id,
        front=front,
        back=back,
        card_type=CardType.BASIC,
        unit_id=unit_id,
        tags=["study-deck", "diagram", "visual"],
        media_refs=[image_ref],
        source_file=source_file,
    )
