#!/usr/bin/env python3
"""Advisory scan for prompt injection and unsafe authority in generated skills."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_CONTENT_RULES = (
    (
        "prompt.ignore_previous",
        re.compile(
            r"\bignore\s+(?:(?:all|any|the)\s+)?(?:previous|prior)\s+"
            r"(?:instructions?|prompts?|rules?|messages?)\b",
            re.IGNORECASE,
        ),
        "contains an instruction-override phrase",
    ),
    (
        "prompt.disregard_system",
        re.compile(r"\bdisregard\s+(?:the\s+)?(?:system|developer)\b", re.IGNORECASE),
        "contains a system-instruction override phrase",
    ),
    (
        "prompt.role_reassignment",
        re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
        "contains a role-reassignment phrase",
    ),
    (
        "prompt.system_tag",
        re.compile(r"<\s*/?\s*system\b[^>]*>", re.IGNORECASE),
        "contains a system-message tag",
    ),
)


def scan_dir(skill_dir: Path) -> list[str]:
    findings = []
    if not skill_dir.exists():
        return [f"Directorio {skill_dir} no existe."]

    for path in skill_dir.rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for rule_id, pattern, msg in _CONTENT_RULES:
            for idx, line in enumerate(content.splitlines(), start=1):
                if pattern.search(line):
                    findings.append(f"[{path.name}:{idx}] {rule_id}: {msg}")

    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Escáner de seguridad para skills")
    parser.add_argument("path", help="Ruta al directorio de la skill")
    args = parser.parse_args()

    findings = scan_dir(Path(args.path))
    if findings:
        print("⚠️ Advertencias de Seguridad Encontradas:")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✓ Escaneo de seguridad completado: 0 hallazgos sospechosos.")
        sys.exit(0)
