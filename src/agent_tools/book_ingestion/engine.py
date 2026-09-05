from __future__ import annotations

import re
from typing import Any

WORDS_PER_TOKEN = 0.75

# Regex to detect explicit chapter titles
_EXPLICIT_CHAPTER = re.compile(
    r"^\s*(?:chapter|chapitre|kapitel|cap[ií]tulo|capitolo|hoofdstuk|ch\.?)\s*(?:(\d{1,2})|(?P<roman>[IVXLCDM]{1,7}))\b(?P<rest>.*)$",
    re.IGNORECASE,
)

_ROMAN_HEAD = re.compile(r"^\s*([IVXLCDM]+)\s*[:.]\s+[A-ZÀ-Þ\"“(]")
_CN_CHAPTER = re.compile(r"^\s*第\s*([0-9一二三四五六七八九十百千]+)\s*[章回卷节篇讲]")

# Regex to detect figures, charts, and diagrams in text
_FIGURE_PATTERN = re.compile(
    r"\b(?:figure|figura|fig\.|diagrama|gráfica|grafico|chart|esquema|illustration|ilustració[nns])\s*\d*[\.:]?",
    re.IGNORECASE,
)

# Regex for Markdown H1 and H2 headers (# or ##)
_MARKDOWN_HEADER = re.compile(r"^(?:#{1,2})\s+(.+)$")


def estimate_tokens(text: str) -> int:
    """Estimates token count in text (words / 0.75 heuristic)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        words = len(text.split())
        return int(words / WORDS_PER_TOKEN)


def _parse_roman(roman_str: str) -> int | None:
    roman_vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = roman_str.upper()
    val = 0
    prev_val = 0
    for char in reversed(s):
        curr = roman_vals.get(char, 0)
        if curr >= prev_val:
            val += curr
        else:
            val -= curr
        prev_val = curr
    return val if val > 0 else None


def chapter_number(line: str) -> int | None:
    """Detects whether a line represents an explicit chapter title and returns its number."""
    m = _EXPLICIT_CHAPTER.match(line)
    if m:
        num_str = m.group(1)
        if num_str:
            return int(num_str)
        roman_str = m.group("roman")
        if roman_str:
            return _parse_roman(roman_str)

    m_rom = _ROMAN_HEAD.match(line)
    if m_rom:
        return _parse_roman(m_rom.group(1))

    return None


class BookIngestionService:
    """Intelligent ingestion and segmentation service for non-fiction books and documents."""

    def __init__(self, words_per_token: float = WORDS_PER_TOKEN):
        self.words_per_token = words_per_token

    def estimate_tokens(self, text: str) -> int:
        return estimate_tokens(text)

    def detect_figures(self, text: str) -> list[str]:
        """Detects mentions and captions of figures/diagrams/charts in text."""
        matches = []
        for line in text.splitlines():
            if _FIGURE_PATTERN.search(line):
                cleaned = line.strip()
                if cleaned and len(cleaned) < 200:
                    matches.append(cleaned)
        return matches

    def _split_by_explicit_chapters(self, lines: list[str]) -> list[dict[str, Any]]:
        """Segmentation based on explicit chapter keywords (Chapter X, Capítulo Y)."""
        chapters: list[dict[str, Any]] = []
        current_title = "Introduction / Front Matter"
        current_lines: list[str] = []

        for line in lines:
            num = chapter_number(line)
            if num is not None and current_lines:
                chapter_body = "\n".join(current_lines).strip()
                if chapter_body:
                    chapters.append({
                        "number": len(chapters) + 1,
                        "title": current_title,
                        "content": chapter_body,
                        "tokens": estimate_tokens(chapter_body),
                        "figures_detected": self.detect_figures(chapter_body),
                        "segmentation_type": "explicit_chapter"
                    })
                current_title = line.strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            chapter_body = "\n".join(current_lines).strip()
            if chapter_body:
                chapters.append({
                    "number": len(chapters) + 1,
                    "title": current_title,
                    "content": chapter_body,
                    "tokens": estimate_tokens(chapter_body),
                    "figures_detected": self.detect_figures(chapter_body),
                    "segmentation_type": "explicit_chapter"
                })

        return chapters

    def _split_by_markdown_headers(self, lines: list[str]) -> list[dict[str, Any]]:
        """Segmentation based on Markdown headers (# or ##)."""
        chapters: list[dict[str, Any]] = []
        current_title = "Initial Section / Introduction"
        current_lines: list[str] = []

        for line in lines:
            m = _MARKDOWN_HEADER.match(line)
            if m and current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    chapters.append({
                        "number": len(chapters) + 1,
                        "title": current_title,
                        "content": body,
                        "tokens": estimate_tokens(body),
                        "figures_detected": self.detect_figures(body),
                        "segmentation_type": "markdown_header"
                    })
                current_title = m.group(1).strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            body = "\n".join(current_lines).strip()
            if body:
                chapters.append({
                    "number": len(chapters) + 1,
                    "title": current_title,
                    "content": body,
                    "tokens": estimate_tokens(body),
                    "figures_detected": self.detect_figures(body),
                    "segmentation_type": "markdown_header"
                })

        return chapters

    def _split_by_word_chunks(self, text: str, target_words: int = 2000) -> list[dict[str, Any]]:
        """Fallback: Word-count chunking (~2,000 words per chapter/section)."""
        paragraphs = text.split("\n\n")
        chapters: list[dict[str, Any]] = []
        current_paragraphs: list[str] = []
        current_word_count = 0

        for para in paragraphs:
            words = len(para.split())
            if current_word_count + words >= target_words and current_paragraphs:
                body = "\n\n".join(current_paragraphs).strip()
                c_num = len(chapters) + 1
                chapters.append({
                    "number": c_num,
                    "title": f"Section {c_num:02d}",
                    "content": body,
                    "tokens": estimate_tokens(body),
                    "figures_detected": self.detect_figures(body),
                    "segmentation_type": "word_chunk"
                })
                current_paragraphs = [para]
                current_word_count = words
            else:
                current_paragraphs.append(para)
                current_word_count += words

        if current_paragraphs:
            body = "\n\n".join(current_paragraphs).strip()
            if body:
                c_num = len(chapters) + 1
                chapters.append({
                    "number": c_num,
                    "title": f"Section {c_num:02d}",
                    "content": body,
                    "tokens": estimate_tokens(body),
                    "figures_detected": self.detect_figures(body),
                    "segmentation_type": "word_chunk"
                })

        return chapters

    def detect_chapters(self, text: str) -> list[dict[str, Any]]:
        """
        Segments text into chapters or thematic sections.
        Multilevel strategy:
        1. Explicit chapter headers ("Chapter X", "Capítulo Y").
        2. Markdown headers (# or ##) if explicit chapters are absent.
        3. Word-count chunks (~2,000 words) if text is continuous.
        """
        lines = text.splitlines()

        # 1. Try explicit headers
        explicit_chapters = self._split_by_explicit_chapters(lines)
        if len(explicit_chapters) >= 2:
            return explicit_chapters

        # 2. Try Markdown headers
        md_chapters = self._split_by_markdown_headers(lines)
        if len(md_chapters) >= 2:
            return md_chapters

        # 3. Fallback to word-count chunks
        return self._split_by_word_chunks(text, target_words=2000)
