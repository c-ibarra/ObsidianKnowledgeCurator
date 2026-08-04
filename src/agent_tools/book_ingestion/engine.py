from __future__ import annotations

import re

WORDS_PER_TOKEN = 0.75

# Regex para detectar encabezados explícitos de capítulo
_EXPLICIT_CHAPTER = re.compile(
    r"^\s*(?:chapter|chapitre|kapitel|cap[ií]tulo|capitolo|hoofdstuk|ch\.?)\s*(?:(\d{1,2})|(?P<roman>[IVXLCDM]{1,7}))\b(?P<rest>.*)$",
    re.IGNORECASE,
)

_ROMAN_HEAD = re.compile(r"^\s*([IVXLCDM]+)\s*[:.]\s+[A-ZÀ-Þ\"“(]")
_CN_CHAPTER = re.compile(r"^\s*第\s*([0-9一二三四五六七八九十百千]+)\s*[章回卷节篇讲]")

# Regex para detectar figuras, esquemas, gráficas y diagramas en el texto
_FIGURE_PATTERN = re.compile(
    r"\b(?:figure|figura|fig\.|diagrama|gráfica|grafico|chart|esquema|illustration|ilustració[nns])\s*\d*[\.:]?",
    re.IGNORECASE,
)


def estimate_tokens(text: str) -> int:
    """Estima el número de tokens en el texto (heurística palabras / 0.75)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        words = len(text.split())
        return int(words / WORDS_PER_TOKEN)


def chapter_number(line: str) -> int | None:
    """Detecta si una línea representa un título de capítulo y retorna su número."""
    m = _EXPLICIT_CHAPTER.match(line)
    if m:
        num_str = m.group(1)
        if num_str:
            return int(num_str)
        roman_str = m.group("roman")
        if roman_str:
            roman_vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
            val = 0
            for char in roman_str.upper():
                val += roman_vals.get(char, 0)
            return val if val > 0 else None

    m_rom = _ROMAN_HEAD.match(line)
    if m_rom:
        roman_vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        val = 0
        for char in m_rom.group(1).upper():
            val += roman_vals.get(char, 0)
        return val if val > 0 else None

    return None


class BookIngestionService:
    """Servicio de ingesta y segmentación de libros de no ficción para ObsidianKnowledgeCurator."""

    def __init__(self, words_per_token: float = WORDS_PER_TOKEN):
        self.words_per_token = words_per_token

    def estimate_tokens(self, text: str) -> int:
        return estimate_tokens(text)

    def detect_figures(self, text: str) -> list[str]:
        """Detecta menciones y leyendas de figuras/diagramas/gráficas en el texto."""
        matches = []
        for line in text.splitlines():
            if _FIGURE_PATTERN.search(line):
                cleaned = line.strip()
                if cleaned and len(cleaned) < 200:
                    matches.append(cleaned)
        return matches

    def detect_chapters(self, text: str) -> list[dict[str, str | int | list[str]]]:
        """Divide el texto en capítulos e identifica figuras/gráficas a extraer."""
        lines = text.splitlines()
        chapters: list[dict[str, str | int | list[str]]] = []
        current_title = "Introducción / Front Matter"
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
                        "figures_detected": self.detect_figures(chapter_body)
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
                    "figures_detected": self.detect_figures(chapter_body)
                })

        return chapters
