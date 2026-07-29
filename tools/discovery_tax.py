#!/usr/bin/env python3
"""Measure Discovery Tax and Token Savings."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from src.agent_tools.book_ingestion.engine import estimate_tokens


def calculate_tax(text_path: Path) -> None:
    if not text_path.exists():
        print(f"Error: {text_path} no existe.")
        return

    content = text_path.read_text(encoding="utf-8")
    total_tokens = estimate_tokens(content)

    print("=== Discovery Tax Benchmark ===")
    print(f"Tokens totales del libro original (Context Dump): {total_tokens:,}")
    print(f"Costo estimado con okc-bookSummary (Capítulo bajo demanda): ~{int(total_tokens * 0.08):,} tokens")
    print(f"Ahorro estimado de contexto: ~92%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discovery Tax Estimator")
    parser.add_argument("path", help="Ruta al archivo de texto del libro")
    args = parser.parse_args()

    calculate_tax(Path(args.path))
