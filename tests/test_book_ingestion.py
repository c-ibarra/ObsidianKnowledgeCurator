import unittest
from pathlib import Path
import tempfile
from src.agent_tools.book_ingestion.engine import BookIngestionService, estimate_tokens, chapter_number
from src.agent_tools.book_ingestion.sanitize import sanitize_extracted_text
from tools.validate_skill import validate_skill
from tools.scan_generated_skill import scan_dir


class TestBookIngestion(unittest.TestCase):
    def test_sanitize_extracted_text(self):
        raw = "Hello\x00 World!\r\n\r\nThis is a test\u200B string."
        clean = sanitize_extracted_text(raw)
        self.assertNotIn("\x00", clean)
        self.assertNotIn("\r", clean)
        self.assertNotIn("\u200B", clean)
        self.assertIn("Hello World!", clean)

    def test_chapter_number_detection(self):
        self.assertEqual(chapter_number("Chapter 1: Principles of System Design"), 1)
        self.assertEqual(chapter_number("Capítulo 5: Arquitectura de Software"), 5)
        self.assertEqual(chapter_number("Chapter IV: Hexagonal Architecture"), 4)
        self.assertIsNone(chapter_number("This is normal prose text"))

    def test_book_ingestion_service(self):
        sample_text = """
Chapter 1: Introduction to AI Engineering
AI engineering is the practice of designing scalable systems.
Figure 1.1: System Architecture Diagram

Chapter 2: Context Management and Prompt Design
Context management is essential for long-context models.
"""
        service = BookIngestionService()
        chapters = service.detect_chapters(sample_text)
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0]["number"], 1)
        self.assertEqual(len(chapters[0]["figures_detected"]), 1)
        self.assertIn("Figure 1.1", chapters[0]["figures_detected"][0])
        self.assertEqual(chapters[1]["number"], 2)

    def test_validate_and_scan_skill(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            skill_file = tmp_path / "SKILL.md"
            skill_file.write_text(
                "---\nname: test-skill\ndescription: A test skill for validation.\n---\n# Test Skill\nContent goes here.",
                encoding="utf-8"
            )
            self.assertTrue(validate_skill(skill_file))
            findings = scan_dir(tmp_path)
            self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()

