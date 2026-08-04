#!/usr/bin/env python3
import os
import re
import sys
import argparse
from pathlib import Path

def normalize_heading(heading: str) -> str:
    """Normalize heading for comparison (remove emojis, hashes, and lowercase)."""
    # Remove markdown formatting and non-alphanumeric chars (excluding spaces)
    cleaned = re.sub(r'[^\w\s-]', '', heading)
    return cleaned.lower().strip()

def parse_sections(text: str) -> list:
    """
    Split markdown text into sections.
    Returns a list of dictionaries: {"header": str, "body_lines": list[str]}
    """
    sections = []
    current_header = ""
    current_lines = []
    
    for line in text.splitlines():
        # Match H1 (#), H2 (##), or H3 (###) headers
        if line.strip().startswith("#"):
            if current_header or current_lines:
                sections.append({
                    "header": current_header,
                    "body_lines": current_lines
                })
            current_header = line
            current_lines = []
        else:
            current_lines.append(line)
            
    if current_header or current_lines:
        sections.append({
            "header": current_header,
            "body_lines": current_lines
        })
        
    return sections

def merge_metadata_blockquote(old_lines: list, new_lines: list) -> list:
    """Merge title blockquote lines, keeping tags and updating dates."""
    old_text = "\n".join(old_lines)
    new_text = "\n".join(new_lines)
    
    # 1. Parse tags
    tags_pattern = re.compile(r'Tags\s*:\s*(.*)', re.IGNORECASE)
    old_tags = set()
    new_tags = set()
    
    old_tags_match = tags_pattern.search(old_text)
    if old_tags_match:
        old_tags = set(re.findall(r'#[\w\-\/]+', old_tags_match.group(1)))
        
    new_tags_match = tags_pattern.search(new_text)
    if new_tags_match:
        new_tags = set(re.findall(r'#[\w\-\/]+', new_tags_match.group(1)))
        
    merged_tags = old_tags.union(new_tags)
    
    # 2. Extract and update date (prefer new processed date)
    date_pattern = re.compile(r'(Processed|Procesado)\s*:\s*([\d\-\/]+)', re.IGNORECASE)
    new_date_match = date_pattern.search(new_text)
    new_date_str = ""
    if new_date_match:
        new_date_str = f"{new_date_match.group(1)}: {new_date_match.group(2)}"
        
    # Reconstruct old blockquote but replace/merge tags and dates
    merged_lines = []
    for line in old_lines:
        stripped = line.strip()
        # If it is the Tags line, replace with merged tags
        if stripped.startswith(">") and tags_pattern.search(stripped):
            if merged_tags:
                tags_str = " ".join(sorted(merged_tags))
                merged_lines.append(f"> Tags: {tags_str}")
            else:
                merged_lines.append(line)
        # If it is the Processed date line, replace with new date
        elif stripped.startswith(">") and date_pattern.search(stripped) and new_date_str:
            merged_lines.append(f"> {new_date_str}")
        else:
            merged_lines.append(line)
            
    return merged_lines

def merge_key_takeaways(old_lines: list, new_lines: list) -> list:
    """Merge takeaways, keeping existing items and appending new ones sequentially."""
    items = []
    seen = set()
    
    def extract_items(lines):
        extracted = []
        for line in lines:
            stripped = line.strip()
            # Match list items starting with numbers (1. ), bullets (- ), or stars (* )
            match = re.match(r'^(?:\d+\.|\-|\*)\s*(.*)', stripped)
            if match:
                item_content = match.group(1).strip()
                if item_content:
                    extracted.append(item_content)
        return extracted
        
    old_items = extract_items(old_lines)
    new_items = extract_items(new_lines)
    
    # Retain old items in order
    for item in old_items:
        norm_item = item.lower()
        if norm_item not in seen:
            seen.add(norm_item)
            items.append(item)
            
    # Append new unique items
    for item in new_items:
        norm_item = item.lower()
        if norm_item not in seen:
            seen.add(norm_item)
            items.append(item)
            
    # Format sequentially: 1. Item 1, 2. Item 2...
    result_lines = []
    for idx, item in enumerate(items, 1):
        result_lines.append(f"{idx}. {item}")
        
    # Preserve any non-list introductory/concluding lines from old section
    intro_lines = []
    for line in old_lines:
        if line.strip() and not re.match(r'^(?:\d+\.|\-|\*)\s*', line.strip()):
            intro_lines.append(line)
            
    return intro_lines + result_lines

def merge_flashcards(old_lines: list, new_lines: list) -> list:
    """Merge Q&A flashcards, keying on normalized question."""
    cards = {}
    
    def parse_cards(lines):
        parsed = {}
        current_q = None
        current_a_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("Q:"):
                if current_q:
                    parsed[current_q.strip()] = "\n".join(current_a_lines).strip()
                current_q = stripped[2:].strip()
                current_a_lines = []
            elif stripped.startswith("A:"):
                current_a_lines.append(stripped[2:].strip())
            elif current_q and stripped:
                current_a_lines.append(stripped)
                
        if current_q:
            parsed[current_q.strip()] = "\n".join(current_a_lines).strip()
        return parsed

    old_cards = parse_cards(old_lines)
    new_cards = parse_cards(new_lines)
    
    # Merge: keep old card values, insert new card keys
    merged = old_cards.copy()
    for q, a in new_cards.items():
        norm_q = q.lower()
        # Check if question already exists case-insensitively
        exists = False
        for old_q in merged.keys():
            if old_q.lower() == norm_q:
                exists = True
                break
        if not exists:
            merged[q] = a
            
    # Re-format Q&A blocks
    result_lines = []
    for q, a in merged.items():
        if result_lines:
            result_lines.append("") # Blank line separator
        result_lines.append(f"Q: {q}")
        result_lines.append(f"A: {a}")
        
    return result_lines

def merge_glossary(old_lines: list, new_lines: list) -> list:
    """Merge glossary, sorted alphabetically by term."""
    terms = {}
    term_pattern = re.compile(r'^\*\*(.*?)\*\*\s*:\s*(.*)')
    
    def parse_terms(lines):
        parsed = {}
        for line in lines:
            if match := term_pattern.match(line.strip()):
                parsed[match.group(1).strip()] = match.group(2).strip()
        return parsed
        
    old_terms = parse_terms(old_lines)
    new_terms = parse_terms(new_lines)
    
    # Merge terms (old overrides if exists)
    merged = new_terms.copy()
    merged.update(old_terms)
    
    # Re-format alphabetically
    result_lines = []
    for term in sorted(merged.keys(), key=lambda s: s.lower()):
        result_lines.append(f"**{term}**: {merged[term]}")
        
    return result_lines

def merge_related(old_lines: list, new_lines: list) -> list:
    """Merge related wikilinks and sort them."""
    links = set()
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    def extract_links(lines):
        for line in lines:
            for match in link_pattern.finditer(line):
                links.add(match.group(1).strip())
                
    extract_links(old_lines)
    extract_links(new_lines)
    
    result_lines = []
    for link in sorted(list(links), key=lambda s: s.lower()):
        result_lines.append(f"- [[{link}]]")
        
    return result_lines

def merge_thematic_section(old_lines: list, new_lines: list) -> list:
    """Merge thematic body lines paragraph-by-paragraph to preserve user edits."""
    
    def split_paragraphs(lines):
        paragraphs = []
        current = []
        for line in lines:
            if not line.strip():
                if current:
                    paragraphs.append(current)
                    current = []
            else:
                current.append(line)
        if current:
            paragraphs.append(current)
        return paragraphs

    old_paras = split_paragraphs(old_lines)
    new_paras = split_paragraphs(new_lines)
    
    # Helper to check if a paragraph is already present
    def is_para_present(para, pool):
        para_text = "\n".join(para).lower().strip()
        para_text_clean = re.sub(r'\s+', '', para_text)
        
        for pool_para in pool:
            pool_text = "\n".join(pool_para).lower().strip()
            pool_text_clean = re.sub(r'\s+', '', pool_text)
            if para_text_clean == pool_text_clean or para_text_clean in pool_text_clean or pool_text_clean in para_text_clean:
                return True
        return False

    merged_paras = old_paras.copy()
    
    # Append new paragraphs that aren't already represented
    for new_para in new_paras:
        if not is_para_present(new_para, merged_paras):
            merged_paras.append(new_para)
            
    # Reconstruct section
    result_lines = []
    for idx, para in enumerate(merged_paras):
        if idx > 0:
            result_lines.append("")
        result_lines.extend(para)
        
    return result_lines

def safe_merge_markdown(old_text: str, new_text: str) -> str:
    """Semantically merges old and new markdown documents heading by heading."""
    if not old_text.strip():
        return new_text
    if not new_text.strip():
        return old_text
        
    old_sections = parse_sections(old_text)
    new_sections = parse_sections(new_text)
    
    # Map old sections by normalized heading for fast lookup
    old_by_heading = {}
    for idx, sec in enumerate(old_sections):
        norm = normalize_heading(sec["header"])
        old_by_heading[norm] = (sec, idx)
        
    # We will build the merged sections list. We keep the order of the old document.
    # We will keep track of which old sections have been merged/emitted.
    merged_sections = [None] * len(old_sections)
    emitted_new_headings = set()
    
    for new_sec in new_sections:
        new_header = new_sec["header"]
        norm = normalize_heading(new_header)
        
        if norm in old_by_heading:
            old_sec, old_idx = old_by_heading[norm]
            
            # Determine merge strategy based on heading type
            if not norm or new_header.startswith("# "):
                # Document title and metadata blockquote
                merged_body = merge_metadata_blockquote(old_sec["body_lines"], new_sec["body_lines"])
            elif "takeaway" in norm:
                merged_body = merge_key_takeaways(old_sec["body_lines"], new_sec["body_lines"])
            elif "flashcard" in norm:
                merged_body = merge_flashcards(old_sec["body_lines"], new_sec["body_lines"])
            elif "glossary" in norm:
                merged_body = merge_glossary(old_sec["body_lines"], new_sec["body_lines"])
            elif "related" in norm:
                merged_body = merge_related(old_sec["body_lines"], new_sec["body_lines"])
            else:
                # Thematic section (e.g. 1. Intro, 2. Architecture)
                merged_body = merge_thematic_section(old_sec["body_lines"], new_sec["body_lines"])
                
            merged_sections[old_idx] = {
                "header": old_sec["header"],  # Retain old header casing/emoji
                "body_lines": merged_body
            }
            emitted_new_headings.add(norm)
        else:
            # New section that wasn't in the old document.
            # We will append it to the end later.
            pass
            
    # Fill in any old sections that weren't present in the new document (preserve user sections!)
    for idx, sec in enumerate(old_sections):
        if merged_sections[idx] is None:
            merged_sections[idx] = sec
            
    # Append any brand new sections from the new document
    for new_sec in new_sections:
        norm = normalize_heading(new_sec["header"])
        if norm not in emitted_new_headings:
            merged_sections.append(new_sec)
            
    # Reassemble markdown text
    doc_blocks = []
    for sec in merged_sections:
        block = []
        if sec["header"]:
            block.append(sec["header"])
        # Ensure no trailing or leading double blank lines in body_lines
        body = "\n".join(sec["body_lines"]).strip()
        if body:
            block.append(body)
        doc_blocks.append("\n".join(block))
        
    return "\n\n".join(doc_blocks) + "\n"

def main():
    parser = argparse.ArgumentParser(description="AST-Based Semantic Markdown Safe-Merge")
    parser.add_argument("--existing", required=True, help="Path to existing markdown note")
    parser.add_argument("--new", required=True, help="Path to new markdown content file")
    parser.add_argument("--output", help="Path to output file (default: overwrite existing)")
    
    args = parser.parse_args()
    
    existing_path = Path(args.existing)
    new_path = Path(args.new)
    output_path = Path(args.output) if args.output else existing_path
    
    if not existing_path.exists():
        print(f"Error: Existing file not found: {existing_path}")
        sys.exit(1)
        
    if not new_path.exists():
        print(f"Error: New file not found: {new_path}")
        sys.exit(1)
        
    try:
        old_text = existing_path.read_text(encoding="utf-8")
        new_text = new_path.read_text(encoding="utf-8")
        
        merged_text = safe_merge_markdown(old_text, new_text)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(merged_text, encoding="utf-8")
        print(f"Successfully merged notes into: {output_path}")
    except Exception as e:
        print(f"Error merging files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
