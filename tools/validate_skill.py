#!/usr/bin/env python3
"""Audit a SKILL.md against Agent Skills rules for host compatibility."""

from __future__ import annotations

import argparse
import re
import sys
import yaml
from pathlib import Path

CLAUDE_CODE_TOOLS = {
    "Bash", "Read", "Write", "Edit", "Glob", "Grep",
    "WebFetch", "WebSearch", "NotebookEdit", "Task", "TodoWrite",
}


def validate_skill(skill_file: Path) -> bool:
    """Valida la sintaxis del Frontmatter YAML en SKILL.md y campos obligatorios."""
    if not skill_file.exists():
        print(f"❌ Error: El archivo {skill_file} no existe.")
        return False

    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        print("❌ Error: Falta el encabezado YAML Frontmatter ('---').")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print("❌ Error: Frontmatter mal formado.")
        return False

    try:
        frontmatter = yaml.safe_load(parts[1])
    except Exception as e:
        print(f"❌ Error parseando YAML: {e}")
        return False

    if not isinstance(frontmatter, dict):
        print("❌ Error: Frontmatter debe ser un mapa YAML.")
        return False

    if "name" not in frontmatter:
        print("❌ Error: Campo obligatorio 'name' ausente en Frontmatter.")
        return False

    if "description" not in frontmatter:
        print("❌ Error: Campo obligatorio 'description' ausente en Frontmatter.")
        return False

    print(f"✓ SKILL.md es válido para la skill '{frontmatter['name']}'.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validador de SKILL.md")
    parser.add_argument("path", help="Ruta a SKILL.md")
    args = parser.parse_args()

    success = validate_skill(Path(args.path))
    sys.exit(0 if success else 1)
