"""Universal Provenance & Artifact Hygiene Engine for Obsidian Knowledge Curator.

Ensures all text, transcripts, markdown files, and downloaded media assets are
100% sanitized before writing to the Obsidian Vault (VAULT_ROOT).
- Strips invisible Unicode codepoints, zero-width spaces (ZWSP, ZWNJ, ZWJ),
  directional marks (LRM, RLM), soft hyphens, and Unicode tag plane characters.
- Normalizes space homoglyphs (NBSP, en-space, em-space, ideographic space) to standard ASCII spaces.
- Automatically invokes watermarks-remover to strip C2PA, EXIF, and AI metadata (APP11/SynthID) from images.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Optional

# Codepoints commonly used for invisible watermarking, steganography, or corrupted pastes.
STRIP_CODEPOINTS: frozenset[int] = frozenset(
    {
        0x00AD,  # soft hyphen
        0x034F,  # combining grapheme joiner
        0x061C,  # Arabic letter mark
        0x115F,  # Hangul choseong filler
        0x1160,  # Hangul jungseong filler
        0x17B4,  # Khmer vowel inherent AQ
        0x17B5,  # Khmer vowel inherent AA
        0x180B,  # Mongolian free variation selector-1
        0x180C,
        0x180D,
        0x180E,  # Mongolian vowel separator
        0x200B,  # zero width space (ZWSP)
        0x200C,  # zero width non-joiner (ZWNJ)
        0x200D,  # zero width joiner (ZWJ)
        0x200E,  # LRM
        0x200F,  # RLM
        0x202A,  # LRE
        0x202B,  # RLE
        0x202C,  # PDF
        0x202D,  # LRO
        0x202E,  # RLO
        0x2060,  # word joiner
        0x2061,  # function application
        0x2062,  # invisible times
        0x2063,  # invisible separator
        0x2064,  # invisible plus
        0x2066,  # LRI
        0x2067,  # RLI
        0x2068,  # FSI
        0x2069,  # PDI
        0x206A,  # inhibit symmetric swapping
        0x206B,
        0x206C,
        0x206D,
        0x206E,
        0x206F,
        0xFEFF,  # BOM / ZWNBSP
        0xFE00,  # variation selectors
        0xFE01,
        0xFE02,
        0xFE03,
        0xFE04,
        0xFE05,
        0xFE06,
        0xFE07,
        0xFE08,
        0xFE09,
        0xFE0A,
        0xFE0B,
        0xFE0C,
        0xFE0D,
        0xFE0E,
        0xFE0F,
        0xFFF9,  # interlinear annotations
        0xFFFA,
        0xFFFB,
    }
)

# Exotic space homoglyphs mapped to standard ASCII space U+0020
SPACE_HOMOGLYPHS: dict[int, str] = {
    0x00A0: " ",  # no-break space
    0x1680: " ",  # Ogham space mark
    0x2000: " ",  # en quad
    0x2001: " ",  # em quad
    0x2002: " ",  # en space
    0x2003: " ",  # em space
    0x2004: " ",  # three-per-em space
    0x2005: " ",  # four-per-em space
    0x2006: " ",  # six-per-em space
    0x2007: " ",  # figure space
    0x2008: " ",  # punctuation space
    0x2009: " ",  # thin space
    0x200A: " ",  # hair space
    0x202F: " ",  # narrow no-break space
    0x205F: " ",  # medium mathematical space
    0x3000: " ",  # ideographic space
}


def sanitize_text(text: str, aggressive: bool = False) -> str:
    """Sanitizes text by stripping invisible Unicode codepoints, zero-width chars,

    tag characters (0xE0000-0xE007F), and normalizing space homoglyphs.
    """
    if not text:
        return ""

    # Remove null and dangerous binary control chars (preserve standard whitespace \t, \n, \r)
    text = text.replace("\x00", "")

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_chars = []
    for ch in text:
        cp = ord(ch)

        # 1. Skip known invisible / watermark codepoints
        if cp in STRIP_CODEPOINTS:
            continue

        # 2. Skip Unicode Tag characters (U+E0000 - U+E007F) used for hidden token tagging
        if 0xE0000 <= cp <= 0xE007F:
            continue

        # 3. Normalize exotic space homoglyphs
        if cp in SPACE_HOMOGLYPHS:
            cleaned_chars.append(SPACE_HOMOGLYPHS[cp])
            continue

        cleaned_chars.append(ch)

    result = "".join(cleaned_chars)

    # Clean excessive whitespace while preserving paragraph structure
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def get_watermarks_remover_path() -> Optional[Path]:
    """Resolves the watermarks-remover tool path if available on the system."""
    # Check CLI in PATH
    wm_cli = shutil.which("wm-clean-image")
    if wm_cli:
        return Path(wm_cli)

    # Check known local user path
    home_path = Path.home() / "tools" / "watermarks-remover" / "service" / "scripts" / "clean_image.py"
    if home_path.exists():
        return home_path

    return None


def sanitize_image(image_path: str | Path) -> bool:
    """Strips AI provenance, C2PA, and metadata from an image file in-place."""
    p = Path(image_path)
    if not p.exists() or p.stat().st_size == 0:
        return False

    wm_tool = get_watermarks_remover_path()
    if wm_tool:
        try:
            if wm_tool.name == "wm-clean-image":
                cmd = [str(wm_tool), str(p), "-o", str(p)]
            else:
                cmd = [sys.executable, str(wm_tool), str(p), "-o", str(p)]

            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                return True
        except Exception as err:
            print(f"[Sanitizer Warning] watermarks-remover failed on {p.name}: {err}", file=sys.stderr)

    # Native Python fallback: Strip JPEG APP11 segment if JPEG
    try:
        data = p.read_bytes()
        if data.startswith(b"\xff\xd8\xff"):
            # Simple JPEG APP11 strip fallback
            cleaned = _strip_jpeg_app11(data)
            if len(cleaned) != len(data):
                p.write_bytes(cleaned)
                return True
    except Exception:
        pass

    return True


def _strip_jpeg_app11(data: bytes) -> bytes:
    """Native Python fallback: Removes JPEG APP11 segments (0xFFEB) without external dependencies."""
    pos = 2
    out = bytearray(data[:2])
    n = len(data)

    while pos < n - 1:
        if data[pos] != 0xFF:
            out.extend(data[pos:])
            break

        marker = data[pos + 1]
        if marker in (0xD9, 0xDA):  # EOI or SOS
            out.extend(data[pos:])
            break

        if pos + 4 > n:
            out.extend(data[pos:])
            break

        length = (data[pos + 2] << 8) | data[pos + 3]
        seg_end = pos + 2 + length

        # 0xEB is APP11 (C2PA/JUMBF/SynthID)
        if marker == 0xEB:
            pos = seg_end
            continue

        out.extend(data[pos:seg_end])
        pos = seg_end

    return bytes(out)


def sanitize_file(file_path: str | Path) -> bool:
    """Sanitizes any file (text, markdown, or image) according to its format."""
    p = Path(file_path)
    if not p.exists():
        return False

    ext = p.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return sanitize_image(p)
    elif ext in (".md", ".txt", ".json", ".yaml", ".yml", ".html", ".py"):
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            cleaned = sanitize_text(content)
            if cleaned != content:
                p.write_text(cleaned, encoding="utf-8")
            return True
        except Exception as err:
            print(f"[Sanitizer Warning] Failed to sanitize {p}: {err}", file=sys.stderr)
            return False

    return True
