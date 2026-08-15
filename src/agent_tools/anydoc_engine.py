"""Centralized module for multi-format document conversion using AnyDoc with asset handling and fallbacks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

# Attempt to import anydoc
ANYDOC_AVAILABLE = False
try:
    import anydoc
    ANYDOC_AVAILABLE = True
except ImportError:
    ANYDOC_AVAILABLE = False

SUPPORTED_EXTENSIONS = {
    "doc", "docx", "odt", "pdf", "ppt", "pptx",
    "rtf", "epub", "xlsx", "ods", "odp", "csv"
}


def is_anydoc_available() -> bool:
    """Returns True if the firecrawl-anydoc library is installed and usable."""
    return ANYDOC_AVAILABLE


def resolve_vault_root(provided_vault_root: Path | str | None = None) -> Path | None:
    """Resolves the root path of the Obsidian Vault."""
    if provided_vault_root:
        p = Path(provided_vault_root)
        if p.exists():
            return p

    env_root = os.getenv("VAULT_ROOT")
    if env_root and Path(env_root).exists():
        return Path(env_root)

    # Fallback to known default vault path
    default_vault = Path("/Users/carlosibarra/Library/Mobile Documents/iCloud~md~obsidian/Documents/KnowledgeVault")
    if default_vault.exists():
        return default_vault

    return None


def extract_images_from_anydoc(document: Any, vault_root: Path | None, slug: str) -> list[str]:
    """Extracts embedded images from the anydoc Document object and saves them into assets/images/."""
    if not vault_root or not hasattr(document, "assets") or not document.assets:
        return []

    images_dir = vault_root / "assets" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    saved_images: list[str] = []

    for idx, asset in enumerate(document.assets, start=1):
        media_type = getattr(asset, "media_type", "") or ""
        data = getattr(asset, "data", b"")

        if not data or not media_type.startswith("image/"):
            continue

        ext = "png"
        if "jpeg" in media_type or "jpg" in media_type:
            ext = "jpg"
        elif "webp" in media_type:
            ext = "webp"
        elif "gif" in media_type:
            ext = "gif"
        elif "svg" in media_type:
            ext = "svg"

        image_name = f"{slug}-img-{idx}.{ext}"
        target_path = images_dir / image_name
        target_path.write_bytes(data)
        saved_images.append(image_name)

    return saved_images


def fallback_pdf_extraction(file_path: Path) -> str:
    """Extracts text from a PDF using pypdf if anydoc did not yield sufficient text."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n\n".join(text_parts)
    except Exception as err:
        return f"[PDF Fallback Error: {err}]"


def convert_document_to_markdown(
    file_path: Path,
    vault_root: Path | str | None = None,
    slug: str = "document"
) -> dict[str, Any]:
    """
    Converts a document to Markdown using AnyDoc with asset extraction and fallbacks.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            "success": False,
            "error": f"The file '{file_path}' does not exist.",
            "markdown": "",
            "engine": "none",
            "extracted_images": []
        }

    ext = file_path.suffix.lower().lstrip(".")
    resolved_vault = resolve_vault_root(vault_root)

    # 1. Attempt processing with AnyDoc
    if ANYDOC_AVAILABLE and ext in SUPPORTED_EXTENSIONS:
        try:
            file_bytes = file_path.read_bytes()
            markdown = anydoc.to_markdown_bytes(file_bytes, ext)
            document = anydoc.to_document(file_bytes, ext)

            saved_images = extract_images_from_anydoc(document, resolved_vault, slug)

            # Special case: Scanned PDF returning < 100 chars from anydoc
            if ext == "pdf" and len(markdown.strip()) < 100:
                fallback_text = fallback_pdf_extraction(file_path)
                if len(fallback_text.strip()) > len(markdown.strip()):
                    markdown = (
                        f"> [!NOTE]\n> Text extracted via pypdf/OCR fallback (PDF had limited native text in AnyDoc).\n\n"
                        + fallback_text
                    )
                    return {
                        "success": True,
                        "markdown": markdown,
                        "engine": "anydoc+pypdf_fallback",
                        "extracted_images": saved_images,
                        "char_count": len(markdown)
                    }

            # Append references to extracted images if present
            if saved_images:
                img_embeds = "\n\n## 📷 Extracted Resources and Images\n" + "\n".join(
                    [f"![[{img}]]" for img in saved_images]
                )
                markdown += img_embeds

            return {
                "success": True,
                "markdown": markdown,
                "engine": "anydoc",
                "extracted_images": saved_images,
                "char_count": len(markdown)
            }
        except Exception as err:
            # Fallback on anydoc exception
            if ext == "pdf":
                fallback_text = fallback_pdf_extraction(file_path)
                return {
                    "success": True,
                    "markdown": fallback_text,
                    "engine": "pypdf_fallback_error",
                    "extracted_images": [],
                    "char_count": len(fallback_text),
                    "warning": f"AnyDoc failed ({err}); pypdf was used."
                }
            return {
                "success": False,
                "error": f"Error processing with AnyDoc: {err}",
                "markdown": "",
                "engine": "anydoc_error",
                "extracted_images": []
            }

    # 2. Fallback for plain formats (txt, md) or when anydoc is unavailable
    if ext in ("txt", "md"):
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return {
            "success": True,
            "markdown": text,
            "engine": "raw_reader",
            "extracted_images": [],
            "char_count": len(text)
        }

    if ext == "pdf":
        fallback_text = fallback_pdf_extraction(file_path)
        return {
            "success": True,
            "markdown": fallback_text,
            "engine": "pypdf_only",
            "extracted_images": [],
            "char_count": len(fallback_text)
        }

    return {
        "success": False,
        "error": f"File format '{ext}' not supported without AnyDoc.",
        "markdown": "",
        "engine": "none",
        "extracted_images": []
    }
