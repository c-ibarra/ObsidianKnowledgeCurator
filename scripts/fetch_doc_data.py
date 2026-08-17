#!/usr/bin/env python3
"""Multi-format document ingestion and temporary staging script using AnyDoc (/okc-doc)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Insert project root to import src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import PROJECT_ROOT, VAULT_ROOT, TEMP_DIR
from src.agent_tools.anydoc_engine import convert_document_to_markdown, is_anydoc_available


def cleanup_temp() -> None:
    temp_dir = TEMP_DIR
    if temp_dir.exists():
        for file in temp_dir.glob("*"):
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        print("🧹 Temporary staging files successfully removed from temp/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and prepare office/PDF/EPUB document data using AnyDoc")
    parser.add_argument("--input", help="Path to document file (.docx, .pptx, .xlsx, .epub, .pdf, .csv, .odt, .rtf, .txt)")
    parser.add_argument("--slug", default="office-document", help="Identifier slug for the document")
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

    print(f"📄 Processing document with AnyDoc: {input_path.name}")
    result = convert_document_to_markdown(input_path, slug=args.slug)

    if not result.get("success"):
        print(f"❌ Error processing document: {result.get('error')}")
        sys.exit(1)

    markdown_content = result.get("markdown", "")
    extracted_images = result.get("extracted_images", [])
    engine_used = result.get("engine", "unknown")
    estimated_tokens = len(markdown_content) // 4

    temp_dir = TEMP_DIR
    temp_dir.mkdir(exist_ok=True)

    try:
        from scripts.graphify_mapper import map_context_with_graphify
        graphify_ctx = map_context_with_graphify(input_path.stem, markdown_content[:2000])
    except Exception as err:
        graphify_ctx = {"suggested_category": "AI Engineer", "error": str(err)}

    json_data = {
        "slug": args.slug,
        "filename": input_path.name,
        "extension": input_path.suffix.lower().lstrip("."),
        "estimated_tokens": estimated_tokens,
        "engine_used": engine_used,
        "extracted_images": extracted_images,
        "graphify_context": graphify_ctx
    }

    (temp_dir / "fetched_data.json").write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    (temp_dir / "fetched_data.txt").write_text(markdown_content, encoding="utf-8")

    print(f"✓ Document processed successfully ({engine_used}). ~{estimated_tokens:,} tokens.")
    if extracted_images:
        print(f"  - 📷 Extracted images ({len(extracted_images)}): {', '.join(extracted_images)}")
    print("  - Structured data saved to: temp/fetched_data.json")
    print("  - Processed text saved to: temp/fetched_data.txt")


if __name__ == "__main__":
    main()
