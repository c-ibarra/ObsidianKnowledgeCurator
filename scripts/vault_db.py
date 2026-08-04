#!/usr/bin/env python3
import os
import re
import sqlite3
from pathlib import Path

# Add project root and scripts directories to python path
PROJECT_DIR = Path(__file__).parent.parent
DB_PATH = PROJECT_DIR / "graphify-out" / "vault_index.db"

# Ignored vault directory names
IGNORED_DIR_NAMES = {".git", ".obsidian", ".agents"}

def get_vault_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create a SQLite connection to the index database with WAL mode enabled."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    # Enable WAL mode for concurrency and performance
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db(conn: sqlite3.Connection):
    """Initialize DB schema if it doesn't exist."""
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            extension TEXT NOT NULL,
            mtime REAL NOT NULL,
            size INTEGER NOT NULL,
            content TEXT,
            is_document INTEGER NOT NULL,
            title TEXT,
            author TEXT,
            pub_date TEXT,
            type TEXT,
            category TEXT
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            source_path TEXT,
            target_name TEXT,
            FOREIGN KEY(source_path) REFERENCES files(path) ON DELETE CASCADE
        );
        """)
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_path);
        """)
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_name);
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS contradictions (
            file_path TEXT,
            line_num INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY(file_path) REFERENCES files(path) ON DELETE CASCADE
        );
        """)
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_contradictions_file ON contradictions(file_path);
        """)

def clean_creator(creator_raw: str) -> str:
    """Clean markdown links and formatting from author names."""
    if not creator_raw:
        return "Unknown"
    creator = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', creator_raw)
    creator = creator.replace("**", "").replace("__", "").strip()
    if " — " in creator:
        creator = creator.split(" — ")[-1].strip()
    return creator

def parse_note_metadata(content: str, rel_path: Path) -> dict:
    """Extract metadata (title, author, pub_date, type, category) and relationships."""
    lines = content.splitlines()
    title = None
    blockquote_lines = []
    in_blockquote = False
    contradictions = []

    # 1. Parse title, blockquote, and contradictions
    for line_idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        elif stripped.startswith(">"):
            in_blockquote = True
            blockquote_lines.append(stripped[1:].strip())
        elif in_blockquote and not stripped.startswith(">") and stripped != "":
            in_blockquote = False # End of blockquote
            
        if "[!contradiction]" in line:
            contradictions.append((line_idx, stripped))

    # 2. Extract links
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    raw_links = link_pattern.findall(content)
    links = []
    for link in raw_links:
        target = link.split('|')[0].strip()
        target = target.split('#')[0].strip()
        if target:
            links.append(target)

    # 3. Parse blockquote metadata
    author = "Unknown"
    pub_date = "Year 2026"
    content_type = "video"

    for line in blockquote_lines:
        if match := re.search(r'\b(?:Channel/Author|Canal/Autor)\s*:\s*(.*)', line, re.IGNORECASE):
            author = clean_creator(match.group(1))
        elif match := re.search(r'\b(?:Channel|Canal)\s*:\s*(.*)', line, re.IGNORECASE):
            author = clean_creator(match.group(1))
        elif match := re.search(r'\b(?:Author|Autor)\s*:\s*(.*)', line, re.IGNORECASE):
            author = clean_creator(match.group(1))
        elif line.startswith("**") and " — " in line:
            creator_raw = line.split(" — ")[0].replace("**", "").replace("__", "").strip()
            author = clean_creator(creator_raw)
            
        if match := re.search(r'\b(?:Published|Publicado)\s*:\s*(.*)', line, re.IGNORECASE):
            pub_date = match.group(1).replace("**", "").replace("~", "").strip()
        elif match := re.search(r'\b(?:Date|Fecha)\s*:\s*(.*)', line, re.IGNORECASE):
            pub_date = match.group(1).replace("**", "").strip()
            
        if match := re.search(r'\b(?:Type|Tipo)\s*:\s*(.*)', line, re.IGNORECASE):
            content_type = match.group(1).replace("**", "").strip()

    # Determine category based on parent directories
    category = "General"
    if len(rel_path.parts) > 1:
        # Check if under dataScienceKnowledgeBase/AI Engineer
        parts = rel_path.parts
        if "dataScienceKnowledgeBase" in parts:
            idx = parts.index("dataScienceKnowledgeBase")
            if idx + 2 < len(parts):
                category = parts[idx + 2] # The category under dataScienceKnowledgeBase/AI Engineer/
            elif idx + 1 < len(parts):
                category = parts[idx + 1]
        elif "software engineer" in parts:
            idx = parts.index("software engineer")
            if idx + 1 < len(parts):
                category = parts[idx + 1]

    return {
        "title": title or rel_path.stem,
        "author": author,
        "pub_date": pub_date,
        "type": content_type,
        "category": category,
        "links": list(set(links)),
        "contradictions": contradictions
    }

def upsert_file_in_db(file_path: Path, vault_base: Path, conn: sqlite3.Connection):
    """Insert or update a file's record in the SQLite database, parsing if it's a document."""
    try:
        rel_path = file_path.relative_to(vault_base)
        rel_path_str = str(rel_path)
    except ValueError:
        rel_path_str = str(file_path)
        rel_path = Path(file_path)

    stat = file_path.stat()
    mtime = stat.st_mtime
    size = stat.st_size
    suffix = file_path.suffix.lower()
    
    is_doc = 1 if suffix == ".md" else 0
    name = file_path.name
    if is_doc:
        name = file_path.stem
        
    content = None
    title, author, pub_date, content_type, category = None, None, None, None, None
    links, contradictions = [], []

    if is_doc:
        try:
            content = file_path.read_text(encoding="utf-8")
            meta = parse_note_metadata(content, rel_path)
            title = meta["title"]
            author = meta["author"]
            pub_date = meta["pub_date"]
            content_type = meta["type"]
            category = meta["category"]
            links = meta["links"]
            contradictions = meta["contradictions"]
        except Exception as e:
            print(f"Error parsing metadata for {rel_path_str}: {e}")

    with conn:
        # Delete old links and contradictions to prevent orphans (ON DELETE CASCADE will handle it, but we cleanup manually to be safe)
        conn.execute("DELETE FROM links WHERE source_path = ?", (rel_path_str,))
        conn.execute("DELETE FROM contradictions WHERE file_path = ?", (rel_path_str,))

        conn.execute("""
        INSERT INTO files (path, name, extension, mtime, size, content, is_document, title, author, pub_date, type, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            name=excluded.name,
            extension=excluded.extension,
            mtime=excluded.mtime,
            size=excluded.size,
            content=excluded.content,
            is_document=excluded.is_document,
            title=excluded.title,
            author=excluded.author,
            pub_date=excluded.pub_date,
            type=excluded.type,
            category=excluded.category
        """, (rel_path_str, name, suffix, mtime, size, content, is_doc, title, author, pub_date, content_type, category))

        # Insert links
        if links:
            conn.executemany("INSERT INTO links (source_path, target_name) VALUES (?, ?)",
                             [(rel_path_str, link) for link in links])
        
        # Insert contradictions
        if contradictions:
            conn.executemany("INSERT INTO contradictions (file_path, line_num, text) VALUES (?, ?, ?)",
                             [(rel_path_str, line, text) for line, text in contradictions])

def delete_file_from_db(file_path: Path, vault_base: Path, conn: sqlite3.Connection):
    """Delete a file from the SQLite database."""
    try:
        rel_path = file_path.relative_to(vault_base)
        rel_path_str = str(rel_path)
    except ValueError:
        rel_path_str = str(file_path)

    with conn:
        conn.execute("DELETE FROM files WHERE path = ?", (rel_path_str,))

def sync_db(vault_base: Path, conn: sqlite3.Connection):
    """Incrementally synchronize files in the vault base with the SQLite database."""
    init_db(conn)
    
    # 1. Fetch current database entries
    cursor = conn.cursor()
    cursor.execute("SELECT path, mtime FROM files")
    db_files = {row[0]: row[1] for row in cursor.fetchall()}
    
    disk_files = {}
    
    # 2. Crawl vault directories
    print(f"Scanning vault for SQLite index: {vault_base}")
    for root, dirs, files_in_dir in os.walk(vault_base):
        # Filter ignored directories
        parts = Path(root).parts
        if any(part in IGNORED_DIR_NAMES for part in parts):
            continue
            
        for file in files_in_dir:
            file_path = Path(root) / file
            # Index markdown documents and media assets
            suffix = file_path.suffix.lower()
            if suffix == ".md" or suffix in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.svg'):
                try:
                    rel_path = file_path.relative_to(vault_base)
                    rel_path_str = str(rel_path)
                    mtime = file_path.stat().st_mtime
                    disk_files[rel_path_str] = (file_path, mtime)
                except Exception as e:
                    print(f"Error reading stats for {file_path}: {e}")

    # 3. Determine changes
    db_paths = set(db_files.keys())
    disk_paths = set(disk_files.keys())
    
    stale_paths = db_paths - disk_paths
    new_paths = disk_paths - db_paths
    modified_paths = {p for p in disk_paths & db_paths if disk_files[p][1] != db_files[p]}
    
    # 4. Apply deletions
    if stale_paths:
        print(f"Deleting {len(stale_paths)} stale entries from SQLite index...")
        with conn:
            cursor.executemany("DELETE FROM files WHERE path = ?", [(p,) for p in stale_paths])
            
    # 5. Apply insertions and updates
    to_update = new_paths.union(modified_paths)
    if to_update:
        print(f"Indexing {len(to_update)} new/modified files in SQLite index...")
        for p in to_update:
            file_path = disk_files[p][0]
            upsert_file_in_db(file_path, vault_base, conn)
            
    print(f"SQLite index sync complete. Active files: {len(disk_files)}.")

if __name__ == "__main__":
    # Test connection and sync
    from graphify_helper import load_env
    load_env()
    vault_path = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))
    connection = get_vault_db_connection()
    sync_db(vault_path, connection)
    connection.close()
