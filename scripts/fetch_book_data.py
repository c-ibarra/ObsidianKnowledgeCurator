#!/usr/bin/env python3
"""Script de ingesta de libros y preparación de datos temporales para okc-bookSummary."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# Insertar la raíz del proyecto para importar src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent_tools.book_ingestion.engine import BookIngestionService
from src.agent_tools.book_ingestion.sanitize import sanitize_extracted_text


def cleanup_temp() -> None:
    temp_dir = Path("temp")
    if temp_dir.exists():
        for file in temp_dir.glob("*"):
            if file.is_file():
                file.unlink()
        print("🧹 Archivos temporales eliminados correctamente de temp/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and prepare non-fiction book data")
    parser.add_argument("--input", help="Ruta al archivo del libro (PDF, EPUB, DOCX, TXT, MD)")
    parser.add_argument("--slug", default="non-fiction-book", help="Slug identificador del libro")
    parser.add_argument("--clean", action="store_true", help="Limpiar archivos temporales de temp/")
    args = parser.parse_args()

    if args.clean:
        cleanup_temp()
        sys.exit(0)

    if not args.input:
        print("❌ Error: Se requiere el argumento --input o --clean.")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: El archivo de entrada '{input_path}' no existe.")
        sys.exit(1)

    print(f"📖 Leyendo e ingiriendo libro: {input_path.name}")
    raw_text = input_path.read_text(encoding="utf-8", errors="ignore")
    clean_text = sanitize_extracted_text(raw_text)

    service = BookIngestionService()
    chapters = service.detect_chapters(clean_text)
    total_tokens = service.estimate_tokens(clean_text)

    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    try:
        from scripts.graphify_mapper import map_context_with_graphify
        graphify_ctx = map_context_with_graphify(input_path.stem, clean_text[:2000])
    except Exception as err:
        graphify_ctx = {"suggested_category": "AI Safety & Governance", "error": str(err)}

    json_data = {
        "slug": args.slug,
        "filename": input_path.name,
        "total_tokens": total_tokens,
        "chapters_count": len(chapters),
        "chapters": chapters,
        "graphify_context": graphify_ctx
    }

    (temp_dir / "fetched_book_data.json").write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    (temp_dir / "fetched_book_data.txt").write_text(clean_text, encoding="utf-8")

    print(f"✓ Ingesta completada con éxito. Se detectaron {len(chapters)} capítulos y ~{total_tokens:,} tokens.")
    print("  - Datos estructurados guardados en: temp/fetched_book_data.json")
    print("  - Texto limpio guardado en: temp/fetched_book_data.txt")


if __name__ == "__main__":
    main()

