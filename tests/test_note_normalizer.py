#!/usr/bin/env python3
"""Unit tests for src/agent_tools/note_normalizer.py."""

import tempfile
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.agent_tools.note_normalizer import (
    NoteStatus,
    compute_content_hash,
    detect_note_status,
    infer_metadata_cascade,
    build_canonical_header,
    inject_canonical_header,
    safe_archive_file,
    NoteNormalizer,
)


def test_compute_content_hash():
    c1 = "This is a note with some content.\n"
    c2 = "This is a note with some content.\n\n"
    # Content hash should strip whitespace differences at edges
    assert compute_content_hash(c1) == compute_content_hash(c2)
    assert compute_content_hash("Different content") != compute_content_hash(c1)
    print("test_compute_content_hash: PASS")


def test_detect_note_status():
    # 1. Stub
    assert detect_note_status("Short", is_file_size_small=True) == NoteStatus.STUB
    assert detect_note_status("") == NoteStatus.STUB
    assert detect_note_status("Coding Interview Patterns") == NoteStatus.STUB

    # 2. Canonical note
    canonical_text = (
        "# My Note Title\n\n"
        "> **Author — Title**\n"
        "> Source: book\n"
        "> Channel/Author: ByteByteGo · Date: Year 2026\n"
        "> Type: book\n\n"
        "## Intuition\nSome body text here."
    )
    assert detect_note_status(canonical_text) == NoteStatus.CANONICAL

    # 3. Missing header
    raw_text = "## Intuition\nSome body text here without H1 or blockquote."
    assert detect_note_status(raw_text) == NoteStatus.MISSING_HEADER
    print("test_detect_note_status: PASS")


def test_infer_metadata_cascade():
    # Level 1: from image slug
    content_with_image = (
        "Problem statement here.\n\n"
        "![[assets/images/coding-patterns-two-pointers-pair-sum-sorted-image-01-01-2-oiiakqqk.svg]]\n"
        "More text."
    )
    dummy_path = Path("/tmp/vault/software engineer/raw/Books/ByteByteGo - Coding Interview Patterns/Coding Interview Patterns 02.md")
    meta = infer_metadata_cascade(dummy_path, content_with_image)
    assert "Pair Sum - Sorted" in meta["title"] or "Pair Sum Sorted" in meta["title"]
    assert meta["author"] == "ByteByteGo"
    assert "ByteByteGo Coding Interview Patterns" in meta["series"]

    # Level 2: from function signature
    content_with_func = (
        "Given an array, return something.\n\n"
        "```python\n"
        "def find_median_sorted_arrays(nums1, nums2):\n"
        "    pass\n"
        "```\n"
    )
    dummy_path2 = Path("/tmp/vault/Category/Note.md")
    meta2 = infer_metadata_cascade(dummy_path2, content_with_func)
    assert "Find Median Sorted Arrays" in meta2["title"]

    print("test_infer_metadata_cascade: PASS")


def test_inject_canonical_header():
    content = "## Intuition\nCore body content."
    meta = {
        "title": "Two Pointers Strategy",
        "author": "ByteByteGo",
        "source": "Coding Interview Patterns",
        "series": "[[Master Plan — ByteByteGo Coding Interview Patterns]]",
        "type": "book",
        "date": "Year 2026",
    }
    header = build_canonical_header(meta)
    assert header.startswith("# Two Pointers Strategy")
    assert "> **ByteByteGo — Two Pointers Strategy**" in header
    assert "Type: book" in header

    new_content = inject_canonical_header(content, meta)
    assert new_content.startswith("# Two Pointers Strategy")
    assert "## Intuition\nCore body content." in new_content
    print("test_inject_canonical_header: PASS")


def test_safe_archive_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        note_file = tmp_path / "Duplicate Note.md"
        note_file.write_text("duplicate text", encoding="utf-8")

        archived = safe_archive_file(note_file, reason="duplicate_exact")
        assert not note_file.exists()
        assert archived.exists()
        assert "_archive" in str(archived.parent)
        assert "duplicate text" in archived.read_text(encoding="utf-8")
    print("test_safe_archive_file: PASS")


def test_normalizer_batch_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir) / "software engineer" / "raw" / "Books" / "TestBook"
        vault.mkdir(parents=True)

        # 1 canonical
        f_canon = vault / "Note 01.md"
        f_canon.write_text("# Note 01\n> **Author — Note 01**\n> Source: X\n\nBody", encoding="utf-8")

        # 1 missing header
        f_missing = vault / "Note 02.md"
        f_missing.write_text("## Intuition\n```python\ndef solve_problem(): pass\n```", encoding="utf-8")

        # 1 duplicate of f_missing
        f_dup = vault / "Note 02 Copy.md"
        f_dup.write_text("## Intuition\n```python\ndef solve_problem(): pass\n```", encoding="utf-8")

        # 1 stub
        f_stub = vault / "Stub.md"
        f_stub.write_text("just 10 bytes", encoding="utf-8")

        normalizer = NoteNormalizer(target_dir=vault, dry_run=False)
        report = normalizer.run()

        assert len(report["canonical"]) == 1
        assert len(report["normalized"]) == 1
        assert len(report["duplicates"]) == 1
        assert len(report["stubs"]) == 1

        # Check that missing header was injected
        content_fixed = f_missing.read_text(encoding="utf-8")
        assert content_fixed.startswith("# ")
        assert "> **" in content_fixed

        # Check that duplicate and stub were moved to _archive
        archive_dir = vault / "_archive"
        assert archive_dir.exists()
        assert (archive_dir / "Note 02 Copy.md").exists()
        assert (archive_dir / "Stub.md").exists()
    print("test_normalizer_batch_run: PASS")


if __name__ == "__main__":
    print("=== RUNNING NOTE NORMALIZER UNIT TESTS ===")
    test_compute_content_hash()
    test_detect_note_status()
    test_infer_metadata_cascade()
    test_inject_canonical_header()
    test_safe_archive_file()
    test_normalizer_batch_run()
    print("=== ALL TESTS PASSED ===")
