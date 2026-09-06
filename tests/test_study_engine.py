"""End-to-end tests for run_create_deck in engine.py."""

import tempfile
from pathlib import Path
import pytest

from src.agent_tools.flashcards.engine import run_create_deck
from src.agent_tools.flashcards.models import StudyRequest
from src.agent_tools.flashcards.store import StudyStore


def test_run_create_deck_e2e():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_root = Path(tmpdir)
        # Create a sample raw note
        note_dir = v_root / "dataScienceKnowledgeBase" / "AI Engineer" / "raw" / "LLM Architecture"
        note_dir.mkdir(parents=True, exist_ok=True)
        sample_file = note_dir / "Attention Mechanism.md"
        sample_file.write_text(
            """# Attention Mechanism in Transformers

> **Vaswani et al. — Attention Is All You Need**
> Channel/Author: Research · Date: June 2017
> Type: paper
> Processed: 05-09-2026
> Tags: #no-read-yet

## 📌 Key Takeaways
1. **Self-Attention**: Computes query-key-value interactions across all tokens simultaneously.
2. **Multi-Head Scaling**: Allows attending to information from different representation subspaces.

## 1. Mathematical Formulation
Scaled Dot-Product Attention is computed via:
$$Attention(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$

## 2. Core Definitions
- **Query Vector**: Represents the current token seeking context from preceding or surrounding tokens.
- **Key Vector**: Represents tokens offering matching information.
""",
            encoding="utf-8",
        )

        db_path = v_root / "study.db"
        store = StudyStore(db_path=db_path)

        req = StudyRequest(
            action="create",
            source_path=str(note_dir),
            deck_name="Transformers Attention",
        )

        results = run_create_deck(
            request=req,
            store=store,
            vault_root=v_root,
            sync_anki=False,  # Skip actual Anki HTTP calls in unit test
        )

        assert results["deck_name"] == "Transformers Attention"
        assert results["documents_scanned"] == 1
        assert results["units_extracted"] >= 2
        assert results["cards_created"] >= 2
        assert Path(results["vault_deck_path"]).exists()

        # Check content in generated deck file
        deck_text = Path(results["vault_deck_path"]).read_text(encoding="utf-8")
        assert "# Study Deck — Transformers Attention" in deck_text
        assert "## Flashcards" in deck_text
        assert "<!-- id: " in deck_text
        assert "unit: " in deck_text
