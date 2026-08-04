#!/usr/bin/env python3
import os
import re
import difflib
import urllib.parse
import argparse
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))

# ==============================================================================
# HELPERS
# ==============================================================================

def find_best_candidate(dead_link: str, candidates: set, threshold: float = 0.6) -> tuple:
    """
    Finds the best replacement candidate for a dead link using multi-strategy matching:
    1. Case-insensitive exact match
    2. Substring matching
    3. Fuzzy string matching (SequenceMatcher)
    """
    dead_link_clean = dead_link.strip()
    dead_link_lower = dead_link_clean.lower()
    
    # Strategy 1: Case-insensitive exact match
    for candidate in candidates:
        if candidate.lower() == dead_link_lower:
            return candidate, 1.0
            
    # Strategy 2: Substring matching
    substring_matches = []
    for candidate in candidates:
        candidate_lower = candidate.lower()
        if dead_link_lower in candidate_lower or candidate_lower in dead_link_lower:
            # Score is ratio of shorter length to longer length
            score = min(len(dead_link_clean), len(candidate)) / max(len(dead_link_clean), len(candidate))
            if score >= threshold:
                substring_matches.append((candidate, score))
    if substring_matches:
        substring_matches.sort(key=lambda x: x[1], reverse=True)
        return substring_matches[0]
        
    # Strategy 3: Fuzzy sequence matching
    best_candidate = None
    best_score = 0.0
    for candidate in candidates:
        score = difflib.SequenceMatcher(None, dead_link_lower, candidate.lower()).ratio()
        if score > best_score:
            best_score = score
            best_candidate = candidate
            
    if best_score >= threshold:
        return best_candidate, best_score
        
    return None, 0.0

def format_note_link(note_name: str, abs_path: Path) -> str:
    """
    Formats a note name with clickable file:// and obsidian:// links for console.
    """
    if not abs_path or not abs_path.exists():
        return f"'{note_name}'"
    file_uri = abs_path.as_uri()
    try:
        rel_to_vault = abs_path.relative_to(VAULT_BASE)
        # URL encode each part to form a valid URI
        encoded_parts = [urllib.parse.quote(part) for part in rel_to_vault.parts]
        encoded_rel = "/".join(encoded_parts)
        obsidian_uri = f"obsidian://open?vault=Obsidian&file={encoded_rel}"
        return f"'{note_name}' [IDE: {file_uri} | Obsidian: {obsidian_uri}]"
    except Exception:
        return f"'{note_name}' [IDE: {file_uri}]"

# ==============================================================================
# LINTER LOGIC
# ==============================================================================

def run_linter(target_kb: str = "dataScienceKnowledgeBase/AI Engineer", write_changes: bool = False):
    if target_kb.lower() == "all":
        target_kb_dir = VAULT_BASE
        target_kb_name = "Entire Vault"
    else:
        target_kb_dir = VAULT_BASE / target_kb
        target_kb_name = target_kb
        
    print("=" * 80)
    print(f"VAULT HEALTH CHECK & LINTER ({target_kb_name})")
    print("=" * 80)
    
    if not target_kb_dir.exists():
        print(f"Error: Directory not found {target_kb_dir}")
        return

    all_notes = {}
    all_links = set()
    link_graph = {}
    contradictions = []
    
    # 1. Build a global catalog of all notes/files in the entire vault
    from vault_db import get_vault_db_connection
    global_note_names = set()
    global_note_paths = {}
    
    try:
        conn = get_vault_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, path FROM files WHERE path NOT LIKE '%dswok%'")
        rows = cursor.fetchall()
        for name, path_str in rows:
            global_note_names.add(name)
            global_note_paths[name] = VAULT_BASE / path_str
            
        # 2. Gather notes in target KB from database
        if target_kb.lower() == "all":
            cursor.execute("SELECT name, path, content FROM files WHERE is_document = 1 AND path NOT LIKE '%dswok%'")
        else:
            cursor.execute("""
                SELECT name, path, content FROM files 
                WHERE is_document = 1 
                  AND path LIKE ? 
                  AND path NOT LIKE '%dswok%'
            """, (f"{target_kb}/%",))
        note_rows = cursor.fetchall()
        
        for name, path_str, content in note_rows:
            file_path = VAULT_BASE / path_str
            try:
                rel_path = file_path.relative_to(target_kb_dir)
            except ValueError:
                rel_path = file_path.relative_to(VAULT_BASE)
                
            all_notes[name] = {
                "path": rel_path,
                "abs_path": file_path,
                "content": content or "",
                "incoming": [],
                "outgoing": []
            }
            
        # 3. Load contradictions from database
        if target_kb.lower() == "all":
            cursor.execute("""
                SELECT c.file_path, c.line_num, c.text, f.name 
                FROM contradictions c 
                JOIN files f ON c.file_path = f.path
                WHERE c.file_path NOT LIKE '%dswok%'
            """)
        else:
            cursor.execute("""
                SELECT c.file_path, c.line_num, c.text, f.name 
                FROM contradictions c 
                JOIN files f ON c.file_path = f.path
                WHERE c.file_path LIKE ? 
                  AND c.file_path NOT LIKE '%dswok%'
            """, (f"{target_kb}/%",))
        contra_rows = cursor.fetchall()
        for file_path_str, line_num, text, name in contra_rows:
            contradictions.append({
                "note": name,
                "abs_path": VAULT_BASE / file_path_str,
                "line_num": line_num,
                "text": text
            })
            
        # 4. Load links from database
        if target_kb.lower() == "all":
            cursor.execute("""
                SELECT l.source_path, l.target_name, f.name 
                FROM links l
                JOIN files f ON l.source_path = f.path
                WHERE l.source_path NOT LIKE '%dswok%'
            """)
        else:
            cursor.execute("""
                SELECT l.source_path, l.target_name, f.name 
                FROM links l
                JOIN files f ON l.source_path = f.path
                WHERE l.source_path LIKE ? 
                  AND l.source_path NOT LIKE '%dswok%'
            """, (f"{target_kb}/%",))
        link_rows = cursor.fetchall()
        
        for source_path_str, target_name, source_name in link_rows:
            if source_name in all_notes:
                all_notes[source_name]["outgoing"].append(target_name)
            all_links.add(target_name)
            
            if target_name in link_graph:
                link_graph[target_name].append(source_name)
            else:
                link_graph[target_name] = [source_name]
                
        # Map incoming links
        for target, sources in link_graph.items():
            if target in all_notes:
                all_notes[target]["incoming"].extend(sources)
                
        conn.close()
    except Exception as e:
        print(f"Error loading linter data from database: {e}")

    # 4. Analyze Health & Find Candidate Matches
    dead_links = []
    dead_link_suggestions = {}
    candidate_pool = set(all_notes.keys()).union(global_note_names)
    
    for target in all_links:
        # Resolve target links globally against all notes and assets in the entire vault
        if target not in all_notes and target not in global_note_names:
            dead_links.append(target)
            # Find best suggestion
            match, score = find_best_candidate(target, candidate_pool)
            if match:
                dead_link_suggestions[target] = (match, score)
            
    orphans = []
    for note_name, data in all_notes.items():
        if not data["incoming"] and not data["outgoing"] and "Master Plan" not in note_name:
            orphans.append(note_name)

    # 5. Report Results
    print(f"Total Notes Analyzed: {len(all_notes)}")
    
    print("\n[!] CONTRADICTIONS FOUND:")
    if contradictions:
        for c in contradictions:
            linked_note = format_note_link(c['note'], c['abs_path'])
            print(f"  - In {linked_note} (Line {c['line_num']}): {c['text']}")
    else:
        print("  None detected.")

    print(f"\n[!] ORPHAN NOTES ({len(orphans)}):")
    if orphans:
        for o in orphans[:10]:
            abs_p = all_notes[o]["abs_path"]
            print(f"  - {format_note_link(o, abs_p)}")
        if len(orphans) > 10:
            print(f"  ... and {len(orphans)-10} more.")
    else:
        print("  None detected.")

    print(f"\n[!] DEAD LINKS ({len(dead_links)}):")
    if dead_links:
        for d in dead_links[:15]:
            sources = link_graph.get(d, [])
            sources_formatted = [format_note_link(s, all_notes[s]["abs_path"]) for s in sources[:2] if s in all_notes]
            ref_str = f"referenced in: {', '.join(sources_formatted)}"
            
            if d in dead_link_suggestions:
                sug_name, score = dead_link_suggestions[d]
                sug_path = global_note_paths.get(sug_name)
                sug_formatted = format_note_link(sug_name, sug_path)
                print(f"  - '{d}' ({ref_str})\n    --> Suggested Fix: {sug_formatted} (Score: {score:.2f})")
            else:
                print(f"  - '{d}' ({ref_str})\n    --> Suggested Fix: None found")
        if len(dead_links) > 15:
            print(f"  ... and {len(dead_links)-15} more.")
    else:
        print("  None detected.")

    # 6. Apply Write Modifications if requested
    if write_changes and dead_link_suggestions:
        print("\n" + "=" * 80)
        print("APPLYING AUTO-CORRECTIONS TO FILES...")
        print("=" * 80)
        files_modified = 0
        links_fixed_total = 0
        
        for note_name, data in all_notes.items():
            content = data["content"]
            modified = False
            
            def replacer(match):
                nonlocal modified, links_fixed_total
                full_link = match.group(0)
                target = match.group(1).strip()
                header = match.group(2) or ""
                alias = match.group(3) or ""
                
                # Extract target name without header or alias
                target_clean = target.split('|')[0].split('#')[0].strip()
                
                if target_clean in dead_link_suggestions:
                    best_match, _ = dead_link_suggestions[target_clean]
                    new_link = f"[[{best_match}{header}{alias}]]"
                    print(f"    - In '{note_name}': replacing [[{target}]] -> {new_link}")
                    modified = True
                    links_fixed_total += 1
                    return new_link
                return full_link
            
            new_content = re.sub(r'\[\[([^\]|#]*)(#[^\]|]*)?(\|[^\]]*)?\]\]', replacer, content)
            
            if modified:
                try:
                    data["abs_path"].write_text(new_content, encoding="utf-8")
                    files_modified += 1
                except Exception as e:
                    print(f"Error writing updates to '{note_name}': {e}")
                    
        print(f"\n[x] Auto-fixed {links_fixed_total} wikilinks across {files_modified} files successfully!")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vault Health Check and Linter")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root")
    parser.add_argument("--write", action="store_true", help="Apply auto-corrections to markdown files")
    args = parser.parse_args()
    run_linter(args.target_kb, args.write)
