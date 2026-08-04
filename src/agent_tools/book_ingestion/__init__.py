"""Módulo de ingesta de libros y documentos para ObsidianKnowledgeCurator."""

from src.agent_tools.book_ingestion.engine import BookIngestionService
from src.agent_tools.book_ingestion.sanitize import sanitize_extracted_text

__all__ = ["BookIngestionService", "sanitize_extracted_text"]
