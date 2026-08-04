from __future__ import annotations

import pytest
from pathlib import Path
from src.agent_tools.book_ingestion.engine import BookIngestionService, estimate_tokens, chapter_number
from src.agent_tools.book_ingestion.sanitize import sanitize_extracted_text
from tools.validate_skill import validate_skill
from tools.scan_generated_skill import scan_dir


def test_sanitize_extracted_text():
    raw = "Hello\x00 World!\r\n\r\nThis is a test\u200B string."
    clean = sanitize_extracted_text(raw)
    assert "\x00" not in clean
    assert "\r" not in clean
    assert "\u200B" not in clean
    assert "Hello World!" in clean


def test_chapter_number_detection():
    assert chapter_number("Chapter 1: Principles of System Design") == 1
    assert chapter_number("Capítulo 5: Arquitectura de Software") == 5
    assert chapter_number("Chapter IV: Hexagonal Architecture") == 4
    assert chapter_number("This is normal prose text") is None


def test_book_ingestion_service():
    sample_text = """
Chapter 1: Introduction to AI Engineering
AI engineering is the practice of designing scalable systems.
Figure 1.1: System Architecture Diagram

Chapter 2: Context Management and Prompt Design
Context management is essential for long-context models.
"""
    service = BookIngestionService()
    chapters = service.detect_chapters(sample_text)
    assert len(chapters) == 2
    assert chapters[0]["number"] == 1
    assert len(chapters[0]["figures_detected"]) == 1
    assert "Figure 1.1" in chapters[0]["figures_detected"][0]
    assert chapters[1]["number"] == 2


def test_validate_and_scan_skill(tmp_path: Path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text(
        "---\nname: test-skill\ndescription: A test skill for validation.\n---\n# Test Skill\nContent goes here.",
        encoding="utf-8"
    )
    assert validate_skill(skill_file) is True
    findings = scan_dir(tmp_path)
    assert len(findings) == 0
