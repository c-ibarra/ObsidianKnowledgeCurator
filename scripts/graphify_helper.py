#!/usr/bin/env python3
import os
import json
import urllib.parse
from pathlib import Path
import networkx as nx
from networkx.readwrite import json_graph

from graphify.extractors.markdown import extract_markdown
from graphify.extract import extract_python
from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import to_json

PROJECT_DIR = Path(__file__).parent.parent

def load_env():
    env_path = PROJECT_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val

load_env()
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))
OUTPUT_DIR = PROJECT_DIR / "graphify-out"
GRAPH_JSON_PATH = OUTPUT_DIR / "graph.json"
CACHE_PATH = OUTPUT_DIR / "graph_cache.json"

def _relativize_path(abs_path: Path) -> str:
    """Make an absolute path relative to either vault root or project root."""
    try:
        return f"vault://{abs_path.relative_to(VAULT_BASE)}"
    except ValueError:
        try:
            return f"project://{abs_path.relative_to(PROJECT_DIR)}"
        except ValueError:
            return str(abs_path)

def _should_ignore_project_path(path: Path) -> bool:
    """Check if a project path directory should be ignored."""
    parts = path.parts
    ignored = {
        ".git", ".venv", "venv", "env", ".claude", ".gemini", "__pycache__", 
        "node_modules", "temp", "report", "graphify-out"
    }
    return any(part in ignored for part in parts)

def _should_ignore_vault_path(path: Path) -> bool:
    """Check if a vault path directory should be ignored."""
    parts = path.parts
    ignored = {".git", ".obsidian", ".agents"}
    return any(part in ignored for part in parts)

def _extract_file(file_path: Path):
    """Run the appropriate extractor based on the file suffix."""
    suffix = file_path.suffix.lower()
    rel_path_str = _relativize_path(file_path)
    
    if suffix == ".md":
        try:
            res = extract_markdown(file_path)
            # Ensure nodes and edges have correct source_file field
            nodes = res.get("nodes", [])
            edges = res.get("edges", [])
            for n in nodes:
                n["source_file"] = rel_path_str
            for e in edges:
                e["source_file"] = rel_path_str
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            print(f"Error extracting markdown file {file_path}: {e}")
            return {"nodes": [], "edges": []}
            
    elif suffix == ".py":
        try:
            res = extract_python(file_path)
            nodes = res.get("nodes", [])
            edges = res.get("edges", [])
            for n in nodes:
                n["source_file"] = rel_path_str
            for e in edges:
                e["source_file"] = rel_path_str
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            print(f"Error extracting python file {file_path}: {e}")
            return {"nodes": [], "edges": []}
            
    return {"nodes": [], "edges": []}

def load_cache():
    """Load the AST extraction cache."""
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_cache(cache):
    """Save the AST extraction cache."""
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

def init_graph(force=False):
    """Build or update the Graphify graph for vault and project code incrementally."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    cache = load_cache()
    if force:
        cache = {}
        
    updated_cache = {}
    cache_modified = False
    
    # 1. Crawl Vault Base for Markdown Files
    if VAULT_BASE.exists():
        print(f"Scanning vault base for markdown: {VAULT_BASE}")
        for root, dirs, files in os.walk(VAULT_BASE):
            root_path = Path(root)
            if _should_ignore_vault_path(root_path):
                continue
            for file in files:
                if file.endswith(".md"):
                    file_path = root_path / file
                    rel_path = _relativize_path(file_path)
                    try:
                        mtime = file_path.stat().st_mtime
                        if rel_path in cache and cache[rel_path].get("mtime") == mtime:
                            updated_cache[rel_path] = cache[rel_path]
                        else:
                            print(f"Extracting {rel_path}...")
                            res = _extract_file(file_path)
                            updated_cache[rel_path] = {
                                "mtime": mtime,
                                "nodes": res.get("nodes", []),
                                "edges": res.get("edges", [])
                            }
                            cache_modified = True
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        
    # 2. Crawl Project Directory for Python Code and Markdown
    if PROJECT_DIR.exists():
        print(f"Scanning project directory for code: {PROJECT_DIR}")
        for root, dirs, files in os.walk(PROJECT_DIR):
            root_path = Path(root)
            if _should_ignore_project_path(root_path):
                continue
            for file in files:
                if file.endswith((".py", ".md")):
                    file_path = root_path / file
                    rel_path = _relativize_path(file_path)
                    try:
                        mtime = file_path.stat().st_mtime
                        if rel_path in cache and cache[rel_path].get("mtime") == mtime:
                            updated_cache[rel_path] = cache[rel_path]
                        else:
                            print(f"Extracting {rel_path}...")
                            res = _extract_file(file_path)
                            updated_cache[rel_path] = {
                                "mtime": mtime,
                                "nodes": res.get("nodes", []),
                                "edges": res.get("edges", [])
                            }
                            cache_modified = True
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    # Check if any files were deleted
    if set(cache.keys()) - set(updated_cache.keys()):
        cache_modified = True
        
    if cache_modified or not GRAPH_JSON_PATH.exists():
        print("Graph modifications detected. Rebuilding graph...")
        save_cache(updated_cache)
        
        all_nodes = []
        all_edges = []
        for file_info in updated_cache.values():
            all_nodes.extend(file_info.get("nodes", []))
            all_edges.extend(file_info.get("edges", []))
            
        extraction = {
            "nodes": all_nodes,
            "edges": all_edges,
            "hyperedges": [],
            "input_tokens": 0,
            "output_tokens": 0
        }
        
        G = build_from_json(extraction, root=VAULT_BASE, directed=False)
        communities = cluster(G)
        
        # Save the root path so other graphify subcommands know it
        (OUTPUT_DIR / ".graphify_root").write_text(str(VAULT_BASE), encoding="utf-8")
        
        # Save interpreter path
        import sys
        (OUTPUT_DIR / ".graphify_python").write_text(sys.executable, encoding="utf-8")
        
        to_json(G, communities, str(GRAPH_JSON_PATH), force=True)
        print(f"Graphify initialized/updated: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    else:
        print("No changes detected. Graphify index is up to date.")

def update_note_in_graph(note_path: Path):
    """Incremental update: re-extract a note/code and update graph.json structurally."""
    cache = load_cache()
    rel_path = _relativize_path(note_path)
    
    try:
        mtime = note_path.stat().st_mtime
        res = _extract_file(note_path)
        cache[rel_path] = {
            "mtime": mtime,
            "nodes": res.get("nodes", []),
            "edges": res.get("edges", [])
        }
        save_cache(cache)
        
        all_nodes = []
        all_edges = []
        for file_info in cache.values():
            all_nodes.extend(file_info.get("nodes", []))
            all_edges.extend(file_info.get("edges", []))
            
        extraction = {
            "nodes": all_nodes,
            "edges": all_edges,
            "hyperedges": [],
            "input_tokens": 0,
            "output_tokens": 0
        }
        
        G = build_from_json(extraction, root=VAULT_BASE, directed=False)
        communities = cluster(G)
        to_json(G, communities, str(GRAPH_JSON_PATH), force=True)
        print(f"Incremental single-file update done. Active nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
        build_knowledge_md()
    except Exception as e:
        print(f"Error during incremental update of {note_path}: {e}")

def remove_note_from_graph(note_path: Path):
    """Remove a note/code and its edges from graph.json structurally."""
    cache = load_cache()
    rel_path = _relativize_path(note_path)
    if rel_path in cache:
        del cache[rel_path]
        save_cache(cache)
        
        all_nodes = []
        all_edges = []
        for file_info in cache.values():
            all_nodes.extend(file_info.get("nodes", []))
            all_edges.extend(file_info.get("edges", []))
            
        extraction = {
            "nodes": all_nodes,
            "edges": all_edges,
            "hyperedges": [],
            "input_tokens": 0,
            "output_tokens": 0
        }
        
        G = build_from_json(extraction, root=VAULT_BASE, directed=False)
        communities = cluster(G)
        to_json(G, communities, str(GRAPH_JSON_PATH), force=True)
        print(f"Incremental single-file removal done. Active nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
        build_knowledge_md()

def build_knowledge_md():
    """Read graphify-out/graph.json and generate KNOWLEDGE.md in the skill folder."""
    if not GRAPH_JSON_PATH.exists():
        print("Warning: graph.json does not exist. Cannot build KNOWLEDGE.md.")
        return
        
    with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    nodes = data.get("nodes", [])
    
    # Filter for wiki concept pages (source_file contains '/wiki/' or 'wiki/')
    wiki_concepts = []
    for node in nodes:
        source_file = node.get("source_file", "")
        # A concept note representing the main note file
        if source_file and ("wiki/" in source_file or "/wiki/" in source_file) and node.get("file_type") in ("document", "concept"):
            # Check if this node represents the file itself (id is generated from path)
            if node.get("id").endswith(".md") or "/" not in node.get("id"):
                wiki_concepts.append(node)
                
    # Sort concepts by label
    # Deduplicate by source_file to be safe
    seen_files = set()
    unique_concepts = []
    for c in sorted(wiki_concepts, key=lambda x: x.get("label", "")):
        sf = c.get("source_file")
        if sf not in seen_files:
            seen_files.add(sf)
            unique_concepts.append(c)
            
    # Build KNOWLEDGE.md content
    lines = [
        "# Vault Knowledge Cards Index",
        "",
        "This file is automatically generated and updated by the curation scripts. It serves as a static index of all concept and entity notes compiled across the vault.",
        "",
        "## Concept Cards",
        ""
    ]
    
    if not unique_concepts:
        lines.append("*No concept cards found in the wiki zone.*")
    else:
        for c in unique_concepts:
            label = c.get("label", "")
            sf = c.get("source_file", "")
            # Clean prefixes
            if sf.startswith("vault://"):
                sf_clean = sf[len("vault://"):]
                abs_url = f"file://{VAULT_BASE}/{sf_clean}"
            elif sf.startswith("project://"):
                sf_clean = sf[len("project://"):]
                abs_url = f"file://{PROJECT_DIR}/{sf_clean}"
            else:
                abs_url = f"file://{VAULT_BASE}/{sf}"
            # Format as: - [[Concept Name]] - Path: [sf](abs_url)
            lines.append(f"- **{label}**: [[{label}]] — [Open File]({abs_url})")
            
    dest_path = PROJECT_DIR / ".agents" / "skills" / "obsidian-knowledge-curator" / "KNOWLEDGE.md"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Successfully generated KNOWLEDGE.md index with {len(unique_concepts)} concepts: {dest_path}")

if __name__ == "__main__":
    init_graph()
    build_knowledge_md()
