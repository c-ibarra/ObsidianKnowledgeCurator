from __future__ import annotations

import re

_INVISIBLE_CODEPOINTS = {
    0x200B,  # zero width space
    0x200C,  # zero width non-joiner
    0x200D,  # zero width joiner
    0x2060,  # word joiner
    0xFEFF,  # zero width no-break space
}


def sanitize_extracted_text(text: str) -> str:
    """Limpia el texto extraído removiendo caracteres invisibles, nulos y secuencias corruptas."""
    if not text:
        return ""

    # Remover caracteres nulos
    text = text.replace("\x00", "")

    # Normalizar saltos de línea Windows / Mac antiguos
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Filtrar codepoints invisibles
    cleaned_chars = []
    for ch in text:
        cp = ord(ch)
        if cp in _INVISIBLE_CODEPOINTS or 0xE0000 <= cp <= 0xE007F:
            continue
        cleaned_chars.append(ch)

    result = "".join(cleaned_chars)
    # Limpiar espacios consecutivos excesivos manteniendo párrafos
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()
