#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root and scripts directory to python path
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR / "scripts"))

from safe_merge import safe_merge_markdown

def test_metadata_merge():
    old_note = """# Test Title
> **Author — Descriptive Title**
> Source: Youtube video
> Processed: 10-06-2026
> Tags: #no-read-yet #architecture
"""
    new_note = """# Test Title
> **Author — Descriptive Title**
> Source: Youtube video
> Processed: 30-07-2026
> Tags: #no-read-yet #design
"""
    result = safe_merge_markdown(old_note, new_note)
    assert "Processed: 30-07-2026" in result
    assert "#architecture" in result
    assert "#design" in result
    assert "#no-read-yet" in result
    print("test_metadata_merge: PASS")

def test_takeaways_merge():
    old_note = """## 📌 Key Takeaways
1. First takeaway item.
2. Second takeaway item.
"""
    new_note = """## 📌 Key Takeaways
1. Second takeaway item.
2. Third takeaway item.
"""
    result = safe_merge_markdown(old_note, new_note)
    assert "1. First takeaway item." in result
    assert "2. Second takeaway item." in result
    assert "3. Third takeaway item." in result
    print("test_takeaways_merge: PASS")

def test_flashcards_merge():
    old_note = """## Flashcards
Q: What is Hexagonal Architecture?
A: An architectural pattern that decouples business logic from external ports.
"""
    new_note = """## Flashcards
Q: What is Hexagonal Architecture?
A: Decoupled ports and adapters.
Q: What is DDD?
A: Domain-Driven Design.
"""
    result = safe_merge_markdown(old_note, new_note)
    assert "Q: What is Hexagonal Architecture?" in result
    assert "A: An architectural pattern that decouples business logic from external ports." in result
    assert "Q: What is DDD?" in result
    assert "A: Domain-Driven Design." in result
    print("test_flashcards_merge: PASS")

def test_glossary_merge():
    old_note = """## Glossary
**Ports**: Interfaces defining interactions.
**Adapters**: Implementation details.
"""
    new_note = """## Glossary
**Adapters**: Updated adapters definition.
**Domain**: The business domain.
"""
    result = safe_merge_markdown(old_note, new_note)
    # Alphabetically sorted: Adapters, Domain, Ports
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    glossary_idx = lines.index("## Glossary")
    assert lines[glossary_idx + 1] == "**Adapters**: Implementation details."  # Preserved old definition
    assert lines[glossary_idx + 2] == "**Domain**: The business domain."
    assert lines[glossary_idx + 3] == "**Ports**: Interfaces defining interactions."
    print("test_glossary_merge: PASS")

def test_related_merge():
    old_note = """## Related
- [[DDD]]
- [[PortAdapter]]
"""
    new_note = """## Related
- [[PortAdapter]]
- [[CleanArchitecture]]
"""
    result = safe_merge_markdown(old_note, new_note)
    # Sorted: CleanArchitecture, DDD, PortAdapter
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    idx = lines.index("## Related")
    assert lines[idx + 1] == "- [[CleanArchitecture]]"
    assert lines[idx + 2] == "- [[DDD]]"
    assert lines[idx + 3] == "- [[PortAdapter]]"
    print("test_related_merge: PASS")

def test_thematic_merge():
    old_note = """## 1. Concept Introduction
This is the original paragraph explaining the concept.
Here is some user custom text added later.

This paragraph stays the same.
"""
    new_note = """## 1. Concept Introduction
This is the original paragraph explaining the concept.

Here is a new paragraph from the update source content.
"""
    result = safe_merge_markdown(old_note, new_note)
    assert "Here is some user custom text added later." in result
    assert "Here is a new paragraph from the update source content." in result
    print("test_thematic_merge: PASS")

def main():
    print("=== RUNNING SAFE-MERGE UNIT TESTS ===")
    test_metadata_merge()
    test_takeaways_merge()
    test_flashcards_merge()
    test_glossary_merge()
    test_related_merge()
    test_thematic_merge()
    print("=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    main()
