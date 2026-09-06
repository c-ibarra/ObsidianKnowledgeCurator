"""Source document scanning and AST structural parsing for Study Decks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple

from markdown_it import MarkdownIt

from src.config import (
    ASSETS_IMAGES_DIR,
    PROTECTED_ZONES,
    VAULT_ROOT,
    relativize_path,
)
from src.agent_tools.flashcards.models import (
    SectionNode,
    SourceDocument,
    SourceSpan,
)

# Standard markdown-it parser
_MD_PARSER = MarkdownIt("commonmark")

# Regex helpers for Obsidian-specific syntax
_WIKILINK_REGEX = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")
_EMBED_IMAGE_REGEX = re.compile(r"!\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")
_MD_IMAGE_REGEX = re.compile(r"!\[.*?\]\((.*?)\)")


def scan_scope(
    source_path_str: str,
    vault_root: Optional[Path] = None,
    allow_files: bool = True,
) -> List[Path]:
    """Scans and validates target Markdown files within the vault scope.

    Strictly excludes protected zones and hidden directories.
    """
    v_root = vault_root or VAULT_ROOT
    raw_path = Path(source_path_str)
    target = raw_path if raw_path.is_absolute() else (v_root / raw_path)
    target = target.resolve()

    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist in vault: {target}")

    # Enforce that target is inside vault_root
    try:
        rel = target.relative_to(v_root.resolve())
    except ValueError:
        raise PermissionError(f"Target path {target} is outside VAULT_ROOT {v_root}")

    # Check protected zones
    rel_str = str(rel)
    for protected in PROTECTED_ZONES:
        if protected in rel_str or rel_str == protected:
            raise PermissionError(f"Access denied: '{rel_str}' is within protected zone '{protected}'")

    if target.is_file():
        if target.suffix.lower() == ".md":
            return [target]
        return []

    # Target is a directory: traverse recursively
    ignored_patterns = {
        ".git",
        ".obsidian",
        ".agents",
        ".trash",
        ".claudian",
        ".smart-env",
        "_archive",
    }

    found_files: List[Path] = []
    for root, dirs, files in os.walk(target):
        # Filter out hidden or ignored directories
        dirs[:] = [
            d for d in dirs
            if d not in ignored_patterns
            and not d.startswith(".")
            and not any(pz in d for pz in PROTECTED_ZONES)
        ]

        # Double check root relative to vault
        root_path = Path(root)
        try:
            r_rel = str(root_path.relative_to(v_root.resolve()))
        except ValueError:
            continue

        if any(pz in r_rel for pz in PROTECTED_ZONES):
            continue

        for f in sorted(files):
            if f.endswith(".md") and not f.startswith("."):
                found_files.append(root_path / f)

    return sorted(found_files)


def extract_media_references(text: str) -> List[str]:
    """Extracts all image filenames or relative paths referenced in markdown text."""
    refs: Set[str] = set()
    # Embeds: ![[image.png]] or ![[image.png|600]]
    for m in _EMBED_IMAGE_REGEX.finditer(text):
        target = m.group(1).strip()
        if any(target.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            refs.add(target)

    # Standard Markdown images: ![alt](path/image.png)
    for m in _MD_IMAGE_REGEX.finditer(text):
        target = m.group(1).strip()
        if any(target.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            refs.add(target)

    return sorted(list(refs))


def resolve_media_path(ref: str, doc_path: Path, vault_root: Optional[Path] = None) -> Optional[Path]:
    """Resolves an image reference to an existing file on disk."""
    v_root = vault_root or VAULT_ROOT
    clean_name = Path(ref).name

    # 1. Check in assets/images/study directory
    p_study = v_root / "assets" / "images" / "study" / clean_name
    if p_study.exists():
        return p_study.resolve()

    # 2. Check in assets/images directory directly
    p1 = v_root / "assets" / "images" / clean_name
    if p1.exists():
        return p1.resolve()

    # 3. Check relative to vault root
    p2 = v_root / ref
    if p2.exists():
        return p2.resolve()

    # 4. Check relative to current document folder
    p3 = doc_path.parent / ref
    if p3.exists():
        return p3.resolve()

    return None


def parse_markdown_document(
    doc_path: Path,
    vault_root: Optional[Path] = None,
) -> Tuple[SourceDocument, List[SectionNode], List[SourceSpan]]:
    """Parses a Markdown file using markdown-it-py AST.

    Extracts structural sections, paragraphs, tables, formulas, and code fences into verifiable SourceSpans.
    """
    v_root = vault_root or VAULT_ROOT
    content_bytes = doc_path.read_bytes()
    text = content_bytes.decode("utf-8", errors="replace")
    mtime = doc_path.stat().st_mtime

    rel_vault_path = str(doc_path.resolve().relative_to(v_root.resolve()))
    doc = SourceDocument.create(
        vault_path=rel_vault_path,
        content_bytes=content_bytes,
        mtime=mtime,
        title=doc_path.stem,
    )

    tokens = _MD_PARSER.parse(text)
    lines = text.splitlines()

    sections: List[SectionNode] = []
    spans: List[SourceSpan] = []

    heading_stack: List[Tuple[int, str, str]] = []  # (level, text, section_id)
    current_heading_path = doc.title or "Root"
    current_section_id = f"sec_{doc.document_id[:8]}_root"

    # Default root section
    root_section = SectionNode(
        section_id=current_section_id,
        document_id=doc.document_id,
        heading_text=doc.title or "Root",
        heading_level=0,
    )
    sections.append(root_section)

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Headings
        if token.type == "heading_open":
            level = int(token.tag[1:]) if len(token.tag) > 1 and token.tag[1:].isdigit() else 1
            inline_token = tokens[i + 1] if i + 1 < len(tokens) and tokens[i + 1].type == "inline" else None
            h_text = inline_token.content.strip() if inline_token else f"Heading {level}"

            # Pop stack for deeper or equal levels
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()

            parent_sec_id = heading_stack[-1][2] if heading_stack else root_section.section_id
            sec_id = f"sec_{doc.document_id[:8]}_{len(sections)}"
            heading_stack.append((level, h_text, sec_id))

            current_heading_path = " / ".join([h[1] for h in heading_stack])
            current_section_id = sec_id

            new_sec = SectionNode(
                section_id=sec_id,
                document_id=doc.document_id,
                heading_text=h_text,
                heading_level=level,
                parent_section_id=parent_sec_id,
            )
            sections.append(new_sec)
            i += 2  # Skip inline and heading_close
            continue

        # Content blocks with line mappings
        if token.type in ("paragraph_open", "fence", "code_block", "table_open", "blockquote_open"):
            if token.map:
                start_l, end_l = token.map
                span_text = "\n".join(lines[start_l:end_l]).strip()
                if span_text:
                    # Ignore canonical blockquote metadata header (> **Author...) from generating flashcards
                    if token.type == "blockquote_open" and ("Author" in span_text or "Tags:" in span_text):
                        pass
                    # Ignore existing ## Flashcards section if present to avoid re-ingesting legacy generated text
                    elif "## Flashcards" in current_heading_path:
                        pass
                    else:
                        span = SourceSpan.create(
                            document_id=doc.document_id,
                            heading_path=current_heading_path,
                            start_line=start_l + 1,
                            end_line=end_l,
                            text=span_text,
                        )
                        spans.append(span)
                        # Attach span to corresponding section
                        for sec in sections:
                            if sec.section_id == current_section_id:
                                sec.spans.append(span)
                                break

        i += 1

    return doc, sections, spans
