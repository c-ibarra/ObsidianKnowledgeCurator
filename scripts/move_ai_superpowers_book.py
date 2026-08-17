import os
import shutil
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import VAULT_ROOT

SRC_BOOK_MAIN = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Books/Kai-Fu Lee — Superpotencias de la Inteligencia Artificial.md"
SRC_BOOK_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/raw/Books/Kai-Fu Lee — Superpotencias de la Inteligencia Artificial"
SRC_WIKI_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/AI Engineer/wiki"

DEST_BOOKS_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/Machine Learning/raw/books"
DEST_BOOK_MAIN = DEST_BOOKS_DIR / "Kai-Fu Lee — Superpotencias de la Inteligencia Artificial.md"
DEST_BOOK_DIR = DEST_BOOKS_DIR / "Kai-Fu Lee — Superpotencias de la Inteligencia Artificial"
DEST_WIKI_DIR = VAULT_ROOT / "dataScienceKnowledgeBase/Machine Learning/wiki"

os.makedirs(DEST_BOOKS_DIR, exist_ok=True)
os.makedirs(DEST_WIKI_DIR, exist_ok=True)

# 1. Move Master Note
if SRC_BOOK_MAIN.exists():
    shutil.move(str(SRC_BOOK_MAIN), str(DEST_BOOK_MAIN))
    print(f"✓ Moved Master Note to: {DEST_BOOK_MAIN.relative_to(VAULT_ROOT)}")

# 2. Move Book Subfolder
if SRC_BOOK_DIR.exists():
    if DEST_BOOK_DIR.exists():
        shutil.rmtree(DEST_BOOK_DIR)
    shutil.move(str(SRC_BOOK_DIR), str(DEST_BOOK_DIR))
    print(f"✓ Moved Book Subfolder to: {DEST_BOOK_DIR.relative_to(VAULT_ROOT)}")

# 3. Move Wiki Concepts
concepts = [
    "MomentoSputnik.md",
    "EmprendedoresGladiadores.md",
    "CuatroOlasIA.md",
    "ModeloOMO.md",
    "EstipendioInversionSocial.md",
    "SimbiosisHombreMaquina.md"
]

for concept in concepts:
    src_c = SRC_WIKI_DIR / concept
    dest_c = DEST_WIKI_DIR / concept
    if src_c.exists():
        shutil.move(str(src_c), str(dest_c))
        print(f"✓ Moved Wiki Concept '{concept}' to: {dest_c.relative_to(VAULT_ROOT)}")

print("\n🚀 Migration to Machine Learning/raw/books completed successfully!")
