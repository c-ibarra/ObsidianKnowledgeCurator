"""Tests for AST structural parsing and scope scanning."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.sources import (
    extract_media_references,
    parse_markdown_document,
    scan_scope,
)


def test_extract_media_references():
    sample = (
        "Here is an image ![[assets/images/architecture.png]] and another "
        "![[diagram.svg|500]] and markdown format ![alt](assets/images/photo.jpg)."
    )
    refs = extract_media_references(sample)
    assert "assets/images/architecture.png" in refs
    assert "diagram.svg" in refs
    assert "assets/images/photo.jpg" in refs


def test_parse_markdown_document():
    sample_content = """# Architecture Overview

> **Author — Test**
> Tags: #no-read-yet

Introduction paragraph about system architecture.

## Cache Layer

The cache layer stores hot keys using Redis.

```python
def get_cached_val(key):
    return redis.get(key)
```

Mathematical relation:
$$L_{hit} = 1 - L_{miss}$$

| Key | Type |
|---|---|
| user_1 | hash |
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        doc_path = v_root / "AI Engineer" / "raw" / "arch.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(sample_content, encoding="utf-8")

        doc, sections, spans = parse_markdown_document(doc_path, vault_root=v_root)

        assert doc.vault_path == "AI Engineer/raw/arch.md"
        assert len(sections) >= 2
        # Verify heading hierarchy
        section_titles = [s.heading_text for s in sections]
        assert "Architecture Overview" in section_titles
        assert "Cache Layer" in section_titles

        # Spans should capture paragraphs, code, math, and tables
        texts = [s.text_content for s in spans]
        assert any("The cache layer stores hot keys" in t for t in texts)
        assert any("def get_cached_val" in t for t in texts)
        assert any("L_{hit}" in t for t in texts)
        assert any("user_1" in t for t in texts)


def test_scan_scope_and_protected_zones():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        # Create normal files
        f1 = v_root / "AI Engineer" / "raw" / "note1.md"
        f1.parent.mkdir(parents=True, exist_ok=True)
        f1.write_text("# Note 1", encoding="utf-8")

        # Create protected zone file
        f_prot = v_root / "system-design-primer" / "readme.md"
        f_prot.parent.mkdir(parents=True, exist_ok=True)
        f_prot.write_text("# Protected", encoding="utf-8")

        # Normal scan succeeds
        scanned = scan_scope("AI Engineer/raw", vault_root=v_root)
        assert len(scanned) == 1
        assert scanned[0] == f1.resolve()

        # Scanning protected zone raises PermissionError
        with pytest.raises(PermissionError):
            scan_scope("system-design-primer", vault_root=v_root)
