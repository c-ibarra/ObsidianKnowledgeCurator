from __future__ import annotations

from src.agent_tools.sanitizer import sanitize_text


def sanitize_extracted_text(text: str) -> str:
    """Limpia el texto extraído removiendo caracteres invisibles, nulos y secuencias corruptas."""
    return sanitize_text(text)
