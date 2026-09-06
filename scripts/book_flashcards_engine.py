#!/usr/bin/env python3
"""High-Density Active Recall (HDAR) Book Flashcard Engine.

A generalized, end-to-end framework for extracting books (EPUB),
segmenting chapters and semantic sections, validating atomic flashcards,
and synchronizing multi-format study decks to Obsidian and Anki.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    pass

BASE_OUTPUT_DIR = Path("output")
ANKI_URL = "http://127.0.0.1:8765"
DEFAULT_MODEL = "Basic (optional reversed card)"

class AnkiBridge:
    """Handles communication with local Anki instance via AnkiConnect."""

    @staticmethod
    def is_available() -> bool:
        try:
            req = urllib.request.Request(
                ANKI_URL,
                data=json.dumps({"action": "version", "version": 6}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("result") is not None
        except Exception:
            return False

    @staticmethod
    def invoke(action: str, **params) -> Any:
        payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
        req = urllib.request.Request(ANKI_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("error"):
                raise RuntimeError(f"AnkiConnect error: {res['error']}")
            return res.get("result")

    @classmethod
    def store_media(cls, file_path: Path) -> bool:
        if not file_path.exists():
            return False
        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("ascii")
        cls.invoke("storeMediaFile", filename=file_path.name, data=b64_data)
        return True

    @classmethod
    def delete_deck_notes(cls, deck_name: str) -> int:
        note_ids = cls.invoke("findNotes", query=f'deck:"{deck_name}"')
        if not note_ids:
            return 0
        total_deleted = 0
        batch_size = 100
        for i in range(0, len(note_ids), batch_size):
            batch = note_ids[i:i + batch_size]
            cls.invoke("deleteNotes", notes=batch)
            total_deleted += len(batch)
        return total_deleted

    @classmethod
    def sync_notes(cls, deck_name: str, cards: List[Dict[str, Any]], model_name: str = DEFAULT_MODEL, batch_size: int = 50) -> int:
        notes_payload = []
        for c in cards:
            front_html = c["front"].replace("\n", "<br>")
            back_html = c["back"].replace("\n", "<br>")
            
            if c.get("media"):
                for m in c["media"]:
                    fname = Path(m).name
                    back_html += f'<br><br><img src="{fname}">'
                    
            if c.get("source_reference"):
                back_html += f'<br><br><small style="color: #888;">📖 {c["source_reference"]}</small>'

            add_reverse = "y" if c.get("allow_reverse") else ""
            tags = [t.replace(" ", "-") for t in c.get("tags", [])]
            if c.get("chapter_id"):
                tags.append(c["chapter_id"])

            notes_payload.append({
                "deckName": deck_name,
                "modelName": model_name,
                "fields": {
                    "Front": front_html,
                    "Back": back_html,
                    "Add Reverse": add_reverse
                },
                "tags": list(set(tags)),
                "options": {"allowDuplicate": False, "duplicateScope": "deck"}
            })

        total_added = 0
        for i in range(0, len(notes_payload), batch_size):
            batch = notes_payload[i:i + batch_size]
            res = cls.invoke("addNotes", notes=batch)
            total_added += sum(1 for nid in res if nid is not None)
            
        cls.invoke("sync")
        return total_added


class EpubExtractor:
    """Extracts and semantically segments an EPUB file."""

    def __init__(self, epub_path: Path, output_dir: Path):
        self.epub_path = epub_path
        self.output_dir = output_dir
        self.extracted_dir = output_dir / "extracted_book"
        self.images_dir = output_dir / "images"
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def extract_images(self, book) -> int:
        count = 0
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                fname = os.path.basename(item.get_name())
                target = self.images_dir / fname
                with open(target, "wb") as f:
                    f.write(item.get_content())
                count += 1
        return count

    def run(self) -> Dict[str, Any]:
        book = epub.read_epub(str(self.epub_path))
        title_meta = book.get_metadata("DC", "title")
        author_meta = book.get_metadata("DC", "creator")
        title = title_meta[0][0] if title_meta else self.epub_path.stem
        author = author_meta[0][0] if author_meta else "Unknown"

        images_count = self.extract_images(book)

        chapters = []
        ch_idx = 1
        for item_id, _ in book.spine:
            item = book.get_item_with_id(item_id)
            if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue
            soup = BeautifulSoup(item.get_content(), "html.parser")
            h1 = soup.find("h1")
            text = soup.get_text(separator=" ", strip=True)
            word_count = len(text.split())
            if word_count < 200:
                continue
                
            ch_title = h1.get_text(strip=True) if h1 else f"Chapter {ch_idx}"
            ch_id = f"ch{ch_idx:02d}"
            
            sections = []
            sec_idx = 0
            for h in soup.find_all(["h1", "h2", "h3"]):
                sec_title = h.get_text(strip=True)
                if sec_title:
                    sections.append({
                        "section_id": f"{ch_id}_sec{sec_idx:02d}",
                        "title": sec_title,
                        "level": int(h.name[1])
                    })
                    sec_idx += 1
                    
            ch_data = {
                "chapter_id": ch_id,
                "chapter_title": ch_title,
                "file": item.file_name,
                "total_words": word_count,
                "total_sections": max(1, len(sections)),
                "sections": sections
            }
            ch_file = self.extracted_dir / f"{ch_id}.json"
            with open(ch_file, "w", encoding="utf-8") as f:
                json.dump(ch_data, f, indent=2, ensure_ascii=False)
                
            chapters.append(ch_data)
            ch_idx += 1

        summary = {
            "title": title,
            "author": author,
            "total_chapters": len(chapters),
            "images_extracted": images_count,
            "chapters": chapters
        }
        with open(self.output_dir / "book_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        return summary


class CheckpointManager:
    """Maintains state and checkpoint for resuming multi-chapter processing."""

    def __init__(self, output_dir: Path, title: str, author: str, chapters: List[Dict[str, Any]]):
        self.output_dir = output_dir
        self.cp_file = output_dir / "checkpoint.json"
        self.chapters_dir = output_dir / "chapters"
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.data = self._load_or_init(title, author, chapters)

    def _load_or_init(self, title: str, author: str, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.cp_file.exists():
            with open(self.cp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        data = {
            "book_title": title,
            "author": author,
            "total_chapters": len(chapters),
            "status": "pending",
            "current_chapter": chapters[0]["chapter_id"] if chapters else "",
            "chapters": []
        }
        for ch in chapters:
            data["chapters"].append({
                "chapter_id": ch["chapter_id"],
                "chapter_title": ch["chapter_title"],
                "status": "pending",
                "sections_detected": ch.get("total_sections", 1),
                "sections_processed": 0,
                "cards_generated": 0,
                "cards_file": f"chapters/{ch['chapter_id']}.json"
            })
        self._save(data)
        return data

    def _save(self, data: Dict[str, Any]):
        with open(self.cp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def update_chapter(self, ch_id: str, status: str, sections_processed: int, cards_count: int):
        for ch in self.data["chapters"]:
            if ch["chapter_id"] == ch_id:
                ch["status"] = status
                ch["sections_processed"] = sections_processed
                ch["cards_generated"] = cards_count
                break
        self.data["current_chapter"] = ch_id
        if all(ch["status"] == "completed" for ch in self.data["chapters"]):
            self.data["status"] = "completed"
        self._save(self.data)


class DeckCompiler:
    """Compiles validated cards into JSON, Obsidian Markdown, Anki TSV, and Audit Report."""

    @staticmethod
    def compile(output_dir: Path, title: str, author: str) -> Dict[str, Any]:
        chapters_dir = output_dir / "chapters"
        all_cards = []
        seen = set()
        duplicates = 0
        chapter_stats = []

        ch_files = sorted(chapters_dir.glob("ch*.json"))
        for ch_file in ch_files:
            with open(ch_file, "r", encoding="utf-8") as f:
                ch_data = json.load(f)
            cards = ch_data.get("cards", [])
            valid_count = 0
            for c in cards:
                norm_q = re.sub(r"[^a-zA-Z0-9]", "", c["front"].lower())
                if norm_q in seen:
                    duplicates += 1
                    continue
                seen.add(norm_q)
                all_cards.append(c)
                valid_count += 1
            chapter_stats.append({
                "chapter_id": ch_data.get("chapter_id", ch_file.stem),
                "title": ch_data.get("chapter_title", ch_file.stem),
                "cards": valid_count
            })

        # 1. JSON Export
        full_json = {
            "book": title,
            "author": author,
            "total_cards": len(all_cards),
            "duplicates_filtered": duplicates,
            "cards": all_cards
        }
        with open(output_dir / "deck_full.json", "w", encoding="utf-8") as f:
            json.dump(full_json, f, indent=2, ensure_ascii=False)

        # 2. Obsidian Markdown Export
        with open(output_dir / "deck_full.md", "w", encoding="utf-8") as f:
            f.write(f"# Study Deck — {title}\n\n")
            f.write(f"> **Author**: {author}\n")
            f.write(f"> **Total Cards**: {len(all_cards)}\n")
            f.write(f"> **Standard**: High-Density Active Recall (HDAR)\n\n---\n\n")
            cur_ch = ""
            for c in all_cards:
                if c["chapter"] != cur_ch:
                    cur_ch = c["chapter"]
                    f.write(f"\n## {cur_ch}\n\n")
                f.write(f"### {c.get('section', 'Core Concept')}\n\n")
                f.write(f"**Q: {c['front']}**\n\n")
                f.write(f"A: {c['back']}\n\n")
                if c.get("media"):
                    for m in c["media"]:
                        f.write(f"![diagram]({m})\n\n")
                tags_str = " ".join([f"#{t}" for t in c.get("tags", [])])
                f.write(f"*Source: {c.get('source_reference', '')}* | {tags_str}\n\n---\n\n")

        # 3. Anki TSV Export
        with open(output_dir / "deck_full_anki.tsv", "w", encoding="utf-8") as f:
            for c in all_cards:
                front_html = c["front"].replace("\n", "<br>")
                back_html = c["back"].replace("\n", "<br>")
                if c.get("media"):
                    for m in c["media"]:
                        fname = Path(m).name
                        back_html += f'<br><img src="{fname}">'
                tags = " ".join(c.get("tags", []))
                f.write(f"{front_html}\t{back_html}\t{tags}\n")

        # 4. Audit Report
        with open(output_dir / "audit_report.md", "w", encoding="utf-8") as f:
            f.write(f"# Deck Audit Report — {title}\n\n")
            f.write(f"- **Author**: {author}\n")
            f.write(f"- **Total Validated Cards**: {len(all_cards)}\n")
            f.write(f"- **Duplicate Questions Eliminated**: {duplicates}\n\n")
            f.write("| Chapter | Title | Cards |\n|---|---|:---:|\n")
            for st in chapter_stats:
                f.write(f"| `{st['chapter_id']}` | {st['title']} | {st['cards']} |\n")

        return full_json


def main():
    parser = argparse.ArgumentParser(description="HDAR Book Flashcard Engine")
    parser.add_argument("--input", type=str, help="Path to input EPUB book")
    parser.add_argument("--slug", type=str, default="ai_engineering_deck", help="Slug/Folder name in output/")
    parser.add_argument("--deck", type=str, default="AI Engineer::Chip Huyen — AI Engineering", help="Target Anki deck name")
    parser.add_argument("--sync-anki", action="store_true", help="Sync compiled deck to AnkiConnect")
    parser.add_argument("--replace-deck", action="store_true", help="Delete existing notes in target deck before syncing")
    parser.add_argument("--status", action="store_true", help="Check processing status")
    parser.add_argument("--compile", action="store_true", help="Compile deck outputs")
    args = parser.parse_args()

    target_dir = BASE_OUTPUT_DIR / args.slug
    target_dir.mkdir(parents=True, exist_ok=True)

    if args.status:
        cp_file = target_dir / "checkpoint.json"
        if cp_file.exists():
            with open(cp_file, "r", encoding="utf-8") as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print(f"[!] No checkpoint found in {target_dir}")
        return

    if args.input:
        epub_path = Path(args.input)
        if not epub_path.exists():
            print(f"[!] Input file not found: {epub_path}", file=sys.stderr)
            sys.exit(1)
            
        print(f"[*] Extracting EPUB: {epub_path}...")
        extractor = EpubExtractor(epub_path, target_dir)
        summary = extractor.run()
        print(f"✅ Extracted {summary['total_chapters']} chapters and {summary['images_extracted']} images.")
        
        CheckpointManager(target_dir, summary["title"], summary["author"], summary["chapters"])
        print(f"✅ Checkpoint initialized at {target_dir / 'checkpoint.json'}")

    if args.compile or args.sync_anki:
        title = "AI Engineering"
        author = "Chip Huyen"
        sum_file = target_dir / "book_summary.json"
        if sum_file.exists():
            with open(sum_file) as f:
                s = json.load(f)
                title = s.get("title", title)
                author = s.get("author", author)

        print("[*] Compiling full deck...")
        compiled = DeckCompiler.compile(target_dir, title, author)
        print(f"✅ Compiled {compiled['total_cards']} cards in {target_dir}")

        if args.sync_anki:
            if not AnkiBridge.is_available():
                print("[!] AnkiConnect not available at http://127.0.0.1:8765. Ensure Anki is open.", file=sys.stderr)
                sys.exit(1)

            if args.replace_deck:
                print(f"[*] Clearing existing notes in deck '{args.deck}'...")
                del_count = AnkiBridge.delete_deck_notes(args.deck)
                print(f"  - Deleted {del_count} existing notes.")

            # Store media
            media_files = list((target_dir / "images").glob("*.*"))
            for m in media_files:
                AnkiBridge.store_media(m)

            print(f"[*] Syncing {len(compiled['cards'])} cards to Anki deck '{args.deck}'...")
            added = AnkiBridge.sync_notes(args.deck, compiled["cards"])
            print(f"✅ Succeeded! {added} cards added to Anki deck '{args.deck}'.")

if __name__ == "__main__":
    main()
