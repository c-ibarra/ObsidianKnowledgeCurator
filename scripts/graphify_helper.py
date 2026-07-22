#!/usr/bin/env python3
import os
import json
from pathlib import Path
import networkx as nx
from networkx.readwrite import json_graph

from graphify.extractors.markdown import extract_markdown
from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import to_json

PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Obsidian")))
OUTPUT_DIR = PROJECT_DIR / "graphify-out"
GRAPH_JSON_PATH = OUTPUT_DIR / "graph.json"

def _relativize_path(abs_path: Path) -> str:
    """Make an absolute vault path relative to the vault root."""
    try:
        return str(abs_path.relative_to(VAULT_BASE))
    except ValueError:
        return str(abs_path)

def init_graph():
    """Build the Graphify graph for the entire vault structurally."""
    if GRAPH_JSON_PATH.exists():
        return
        
    print("Initializing Graphify Knowledge Graph structurally...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_nodes = []
    all_edges = []
    
    # Crawl the entire vault
    for root, dirs, files in os.walk(VAULT_BASE):
        if any(ignored in root for ignored in [".git", ".obsidian", ".agents"]):
            continue
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                res = extract_markdown(file_path)
                all_nodes.extend(res.get("nodes", []))
                all_edges.extend(res.get("edges", []))
                
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
    print(f"Graphify initialized: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

def update_note_in_graph(note_path: Path):
    """Incremental update: re-extract a note and update graph.json structurally."""
    init_graph()
    
    rel_path_str = _relativize_path(note_path)
    print(f"Updating graph.json for: {rel_path_str}")
    
    # 1. Load existing graph nodes and edges
    try:
        with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read existing graph.json ({e}). Re-initializing.")
        GRAPH_JSON_PATH.unlink(missing_ok=True)
        init_graph()
        return

    # NetworkX serializes edges as "links" or "edges"
    existing_edges = existing_data.get("links") or existing_data.get("edges") or []
    existing_nodes = existing_data.get("nodes") or []
    
    # 2. Filter out old nodes and edges originating from this source file
    filtered_nodes = [n for n in existing_nodes if n.get("source_file") != rel_path_str]
    filtered_edges = [e for e in existing_edges if e.get("source_file") != rel_path_str]
    
    # 3. Extract new nodes and edges
    res = extract_markdown(note_path)
    new_nodes = res.get("nodes", [])
    new_edges = res.get("edges", [])
    
    # 4. Merge
    merged_nodes = filtered_nodes + new_nodes
    merged_edges = filtered_edges + new_edges
    
    extraction = {
        "nodes": merged_nodes,
        "edges": merged_edges,
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0
    }
    
    # 5. Rebuild Graph & Cluster
    G = build_from_json(extraction, root=VAULT_BASE, directed=False)
    communities = cluster(G)
    
    to_json(G, communities, str(GRAPH_JSON_PATH), force=True)
    print(f"Graph updated. Active nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
    build_knowledge_md()

def remove_note_from_graph(note_path: Path):
    """Remove a note and its edges from graph.json structurally."""
    if not GRAPH_JSON_PATH.exists():
        return
        
    rel_path_str = _relativize_path(note_path)
    print(f"Removing from graph.json: {rel_path_str}")
    
    try:
        with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read existing graph.json ({e}).")
        return

    existing_edges = existing_data.get("links") or existing_data.get("edges") or []
    existing_nodes = existing_data.get("nodes") or []
    
    filtered_nodes = [n for n in existing_nodes if n.get("source_file") != rel_path_str]
    filtered_edges = [e for e in existing_edges if e.get("source_file") != rel_path_str]
    
    extraction = {
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0
    }
    
    G = build_from_json(extraction, root=VAULT_BASE, directed=False)
    communities = cluster(G)
    
    to_json(G, communities, str(GRAPH_JSON_PATH), force=True)
    print(f"Note removed. Graph nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
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
            # Generate the relative path URL
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

