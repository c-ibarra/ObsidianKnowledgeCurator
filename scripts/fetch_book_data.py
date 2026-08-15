#!/usr/bin/env python3
"""Book ingestion and temporary staging script for okc-bookSummary."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# Insert project root to import src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent_tools.book_ingestion.engine import BookIngestionService
from src.agent_tools.book_ingestion.sanitize import sanitize_extracted_text


def cleanup_temp() -> None:
    temp_dir = Path("temp")
    if temp_dir.exists():
        for file in temp_dir.glob("*"):
            if file.is_file():
                file.unlink()
        print("🧹 Temporary staging files successfully removed from temp/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and prepare non-fiction book data")
    parser.add_argument("--input", help="Path to book file (PDF, EPUB, DOCX, TXT, MD)")
    parser.add_argument("--slug", default="non-fiction-book", help="Identifier slug for the book")
    parser.add_argument("--clean", action="store_true", help="Clean temporary staging files in temp/")
    args = parser.parse_args()

    if args.clean:
        cleanup_temp()
        sys.exit(0)

    if not args.input:
        print("❌ Error: Argument --input or --clean is required.")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input file '{input_path}' does not exist.")
        sys.exit(1)

    print(f"📖 Reading and ingesting book: {input_path.name}")
    ext = input_path.suffix.lower().lstrip(".")

    # Attempt extraction using anydoc_engine for rich formats (PDF, EPUB, DOCX)
    try:
        from src.agent_tools.anydoc_engine import convert_document_to_markdown, is_anydoc_available
        if is_anydoc_available() and ext in ("pdf", "epub", "docx", "odt", "rtf"):
            res = convert_document_to_markdown(input_path, slug=args.slug)
            if res.get("success") and res.get("markdown"):
                raw_text = res["markdown"]
                print(f"  - Extraction completed via engine: {res.get('engine')}")
            else:
                raw_text = input_path.read_text(encoding="utf-8", errors="ignore")
        else:
            raw_text = input_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as err:
        print(f"  - Fallback to direct reading due to error: {err}")
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

    print(f"✓ Ingestion completed successfully. Detected {len(chapters)} chapters and ~{total_tokens:,} tokens.")
    print("  - Structured data saved to: temp/fetched_book_data.json")
    print("  - Clean text saved to: temp/fetched_book_data.txt")


if __name__ == "__main__":
    main()
