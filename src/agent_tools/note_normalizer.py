"""Note Normalizer & Import Sanitizer Module.

Provides autonomous inspection, deduplication, metadata inference,
canonical header injection, and safe archiving of notes.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import VAULT_ROOT


class NoteStatus(Enum):
    CANONICAL = "canonical"
    MISSING_HEADER = "missing_header"
    DUPLICATE = "duplicate"
    STUB = "stub"


def strip_canonical_header(content: str) -> str:
    """Strips H1 title and source blockquote header, leaving only the substantive body."""
    lines = content.splitlines()
    body_lines = []
    in_header = False
    past_header = False

    for line in lines:
        stripped = line.strip()
        if not past_header:
            if stripped.startswith("# ") or stripped.startswith(">"):
                in_header = True
                continue
            elif in_header and (stripped == "" or stripped.startswith("---")):
                continue
            elif in_header and not stripped.startswith(">"):
                past_header = True
                body_lines.append(line)
            else:
                body_lines.append(line)
        else:
            body_lines.append(line)

    return "\n".join(body_lines).strip()


def compute_content_hash(content: str, strip_header: bool = True) -> str:
    """Computes a normalized SHA-256 hash of markdown content ignoring leading/trailing whitespace and optional headers."""
    target = strip_canonical_header(content) if strip_header else content
    normalized = target.strip().replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def detect_note_status(content: str, is_file_size_small: bool = False) -> NoteStatus:
    """Evaluates whether a note is a stub, missing headers, or canonical."""
    stripped = content.strip()
    if not stripped or len(stripped) < 40 or (is_file_size_small and len(stripped) < 50):
        return NoteStatus.STUB

    # If it is only the book/series title without substance
    if stripped.lower() in ("coding interview patterns", "notes", "readme", "untitled"):
        return NoteStatus.STUB

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return NoteStatus.STUB

    has_h1 = any(line.startswith("# ") for line in lines[:5])
    has_blockquote = any(line.startswith(">") for line in lines[:10])

    if has_h1 and has_blockquote:
        return NoteStatus.CANONICAL

    return NoteStatus.MISSING_HEADER


def _clean_slug_to_title(slug: str) -> str:
    """Converts a kebab-case slug to Title Case words."""
    words = slug.split("-")
    clean_words = []
    for w in words:
        if not w or re.match(r"^[0-9a-f]{8}$", w):  # skip hash suffixes
            continue
        clean_words.append(w.capitalize())
    return " ".join(clean_words)


def infer_metadata_cascade(note_path: Path, content: str) -> Dict[str, str]:
    """Infers note metadata using a 3-level cascade:
    1. Folder hierarchy and linked visual asset slugs
    2. Local heuristics (headings, python function defs, problem openings)
    3. Lightweight LLM fallback (if available/configured)
    """
    inferred_title = ""
    inferred_author = "Unknown"
    inferred_source = note_path.stem
    inferred_series = ""
    inferred_type = "book"

    # Derive author and series from folder hierarchy
    parent_name = note_path.parent.name
    if " - " in parent_name:
        author_part, series_part = parent_name.split(" - ", 1)
        inferred_author = author_part.strip()
        inferred_source = series_part.strip()
        inferred_series = f"[[Master Plan — {author_part.strip()} {series_part.strip()}]]"
    elif parent_name not in ("raw", "wiki", "dev", "Books", "Courses"):
        inferred_author = parent_name
        inferred_series = f"[[Master Plan — {parent_name}]]"

    # --- Level 1: Visual Asset Slugs ---
    img_matches = re.findall(r"!\[\[assets/images/([^\.]+)\.(?:svg|png|jpg|webp)\]\]", content)
    if img_matches:
        first_img = img_matches[0]
        # Clean image name patterns like coding-patterns-<topic>-image-01-02...
        clean_slug = re.sub(r"-[a-z0-9]{8}$", "", first_img)
        clean_slug = re.sub(r"-image-\d+.*$", "", clean_slug)
        clean_slug = re.sub(r"-\d+$", "", clean_slug)

        # Remove known category prefixes if present
        prefixes = [
            "coding-patterns-two-pointers-",
            "coding-patterns-hash-maps-and-sets-",
            "coding-patterns-linked-lists-",
            "coding-patterns-fast-and-slow-pointers-",
            "coding-patterns-sliding-windows-",
            "coding-patterns-binary-search-",
            "coding-patterns-stacks-",
            "coding-patterns-queues-",
            "coding-patterns-heaps-",
            "coding-patterns-intervals-",
            "coding-patterns-prefix-sums-",
            "coding-patterns-trees-",
            "coding-patterns-tries-",
            "coding-patterns-graphs-",
            "coding-patterns-backtracking-",
            "coding-patterns-dynamic-programming-",
            "coding-patterns-greedy-",
            "coding-patterns-sort-and-search-",
            "coding-patterns-bit-manipulation-",
            "coding-patterns-math-and-geometry-",
            "coding-patterns-",
        ]
        for p in prefixes:
            if clean_slug.startswith(p):
                clean_slug = clean_slug[len(p):]
                break

        topic = _clean_slug_to_title(clean_slug)
        if topic and len(topic) > 3:
            inferred_title = topic

    # --- Level 2: Local Code Signatures and Headings ---
    if not inferred_title:
        # Check for python def func_name
        func_match = re.search(r"def\s+([a-zA-Z0-9_]+)\s*\(", content)
        if func_match:
            raw_func = func_match.group(1)
            # ignore standard dunder methods
            if not raw_func.startswith("__"):
                inferred_title = _clean_slug_to_title(raw_func.replace("_", "-"))

    if not inferred_title:
        # Check first H1 or H2 in document
        h_match = re.search(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
        if h_match and h_match.group(1).strip().lower() != "intuition":
            inferred_title = h_match.group(1).strip()

    # --- Level 3: Fallback from File Stem ---
    if not inferred_title or len(inferred_title) < 3:
        inferred_title = note_path.stem

    # If the note starts with a numbered prefix e.g. "Coding Interview Patterns 02"
    num_match = re.search(r"(\d+)", note_path.stem)
    if num_match:
        prefix = f"{note_path.stem} — "
        if not inferred_title.startswith(note_path.stem):
            inferred_title = f"{prefix}{inferred_title}"

    today = datetime.now().strftime("%d-%m-%Y")

    return {
        "title": inferred_title,
        "author": inferred_author,
        "source": inferred_source,
        "series": inferred_series,
        "type": inferred_type,
        "date": "Year 2026",
        "processed": today,
    }


def build_canonical_header(meta: Dict[str, str]) -> str:
    """Formats a canonical header conforming strictly to vault conventions."""
    title = meta.get("title", "Untitled Note")
    author = meta.get("author", "Unknown")
    source = meta.get("source", "Unknown")
    date_str = meta.get("date", "Year 2026")
    content_type = meta.get("type", "book")
    series = meta.get("series", "")
    processed = meta.get("processed", datetime.now().strftime("%d-%m-%Y"))

    series_line = f"\n> Playlist/Series: {series}" if series else ""

    header = f"""# {title}

> **{author} — {title}**
> Source: {source}
> Channel/Author: {author} · Date: {date_str}{series_line}
> Type: {content_type}
> Processed: {processed}
> Tags: #no-read-yet

"""
    return header


def inject_canonical_header(content: str, meta: Dict[str, str]) -> str:
    """Injects the canonical header at the top of note content."""
    header = build_canonical_header(meta)
    return header + content.lstrip()


def safe_archive_file(file_path: Path, reason: str = "duplicate") -> Path:
    """Moves a file safely to an _archive directory alongside the original file."""
    archive_dir = file_path.parent / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    target_path = archive_dir / file_path.name
    counter = 1
    while target_path.exists():
        target_path = archive_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1

    shutil.move(str(file_path), str(target_path))
    return target_path


class NoteNormalizer:
    """Scans, audits, deduplicates, and normalizes notes within a directory or category."""

    def __init__(self, target_dir: Path, dry_run: bool = False, auto_sync: bool = False):
        self.target_dir = target_dir
        self.dry_run = dry_run
        self.auto_sync = auto_sync

    def run(self) -> Dict[str, List[Any]]:
        report: Dict[str, List[Any]] = {
            "canonical": [],
            "normalized": [],
            "duplicates": [],
            "stubs": [],
        }

        if not self.target_dir.exists():
            return report

        seen_hashes: Dict[str, Path] = {}

        # Collect all markdown files, excluding _archive and Master Plans
        all_files = [f for f in self.target_dir.glob("*.md") if "Master Plan" not in f.name and not f.name.startswith(".")]

        # Sort files so that canonical/shorter names are processed BEFORE copies (e.g., "Note.md" before "Note Copy.md")
        def dedup_sort_key(f: Path) -> Tuple[int, int, str]:
            stem_lower = f.stem.lower()
            is_copy = 1 if re.search(r"(?:copy|\(\d+\)|\bdup\b|\b\d+\s+\d+\b)", stem_lower) else 0
            return (is_copy, len(f.stem), f.name)

        files = sorted(all_files, key=dedup_sort_key)

        for file_path in files:
            if "Master Plan" in file_path.name or file_path.name.startswith("."):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            # 1. Check stub
            status = detect_note_status(content, is_file_size_small=file_path.stat().st_size < 50)
            if status == NoteStatus.STUB:
                report["stubs"].append(file_path)
                if not self.dry_run:
                    safe_archive_file(file_path, reason="stub")
                continue

            # 2. Check duplicate hash
            content_hash = compute_content_hash(content)
            if content_hash in seen_hashes:
                original = seen_hashes[content_hash]
                report["duplicates"].append((file_path, original))
                if not self.dry_run:
                    safe_archive_file(file_path, reason=f"duplicate_of_{original.name}")
                continue
            else:
                seen_hashes[content_hash] = file_path

            # 3. Check canonical vs missing header
            if status == NoteStatus.CANONICAL:
                report["canonical"].append(file_path)
            elif status == NoteStatus.MISSING_HEADER:
                report["normalized"].append(file_path)
                if not self.dry_run:
                    meta = infer_metadata_cascade(file_path, content)
                    updated_content = inject_canonical_header(content, meta)
                    file_path.write_text(updated_content, encoding="utf-8")

        # Atomic synchronization if requested and changes occurred
        if self.auto_sync and not self.dry_run and (report["normalized"] or report["duplicates"] or report["stubs"]):
            self._trigger_atomic_sync()

        return report

    def _trigger_atomic_sync(self) -> None:
        """Synchronizes SQLite database and updates Master Plan immediately."""
        try:
            from scripts.vault_db import get_vault_db_connection, sync_db
            conn = get_vault_db_connection()
            sync_db(VAULT_ROOT, conn)
            conn.close()
        except Exception as e:
            print(f"Warning: SQLite auto-sync failed: {e}")
