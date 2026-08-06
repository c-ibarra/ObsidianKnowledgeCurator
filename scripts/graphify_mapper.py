#!/usr/bin/env python3
"""
GraphifyMapper: Hybrid zero-token local context mapper for Obsidian Knowledge Curator.
Uses graphify-out/graph.json to dynamically infer target raw/ categories and match
existing wiki/ concept notes, minimizing LLM token consumption and latency.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

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
GRAPH_JSON_PATH = PROJECT_DIR / "graphify-out" / "graph.json"

def get_available_raw_categories() -> List[str]:
    """Scan vault raw/ subdirectories to build the active category list."""
    raw_dir = VAULT_BASE / "dataScienceKnowledgeBase" / "AI Engineer" / "raw"
    if not raw_dir.exists():
        return []
    
    categories = []
    for item in raw_dir.iterdir():
        if item.is_dir() and not item.name.startswith((".", "_")) and item.name not in ("temp", "report"):
            categories.append(item.name)
    return sorted(categories)

def extract_text_tokens(text: str) -> set:
    """Extract normalized lowercase tokens from title and snippet."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = clean.split()
    # Filter common stop words
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "from", "up", "about", "into", "through", "after", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did", "this", "that",
        "these", "those", "how", "what", "why", "when", "where", "who", "which", "de", "la",
        "el", "en", "y", "del", "los", "las", "un", "una", "por", "para", "con"
    }
    return {w for w in words if len(w) > 2 and w not in stopwords}

def map_context_with_graphify(title: str, text_snippet: str = "") -> Dict[str, Any]:
    """
    Query graphify-out/graph.json locally to predict:
    1. The target category folder under raw/
    2. Existing wiki concept notes that match the text
    3. Match confidence score (0.0 to 1.0)
    """
    categories = get_available_raw_categories()
    combined_text = f"{title} {text_snippet}"
    input_tokens = extract_text_tokens(combined_text)
    
    existing_concepts = []
    category_scores: Dict[str, float] = {cat: 0.0 for cat in categories}
    
    if GRAPH_JSON_PATH.exists():
        try:
            with open(GRAPH_JSON_PATH, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
                
            nodes = graph_data.get("nodes", [])
            for node in nodes:
                node_label = node.get("label", "")
                source_file = node.get("source_file", "")
                
                # Check for wiki concept match
                if "wiki/" in source_file or "/wiki/" in source_file:
                    concept_tokens = extract_text_tokens(node_label)
                    if concept_tokens and concept_tokens.issubset(input_tokens):
                        existing_concepts.append(node_label)
                    elif concept_tokens and len(concept_tokens.intersection(input_tokens)) >= max(1, len(concept_tokens) - 1):
                        existing_concepts.append(node_label)
                
                # Calculate category relevance from raw file paths in graph
                for cat in categories:
                    if f"/raw/{cat}/" in source_file or f"raw/{cat}/" in source_file:
                        node_text_tokens = extract_text_tokens(f"{node_label} {source_file}")
                        overlap = len(input_tokens.intersection(node_text_tokens))
                        if overlap > 0:
                            category_scores[cat] += overlap
        except Exception as err:
            print(f"[GraphifyMapper Warning] Error reading graph.json: {err}", file=sys.stderr)
            
    # Also score categories directly by name keyword overlap
    for cat in categories:
        cat_tokens = extract_text_tokens(cat)
        overlap = len(input_tokens.intersection(cat_tokens))
        category_scores[cat] += overlap * 3.0

    # Pick best category
    best_category = "AI Safety & Governance"  # Default fallback
    highest_score = 0.0
    for cat, score in category_scores.items():
        if score > highest_score:
            highest_score = score
            best_category = cat
            
    confidence = min(1.0, highest_score / 5.0) if highest_score > 0 else 0.5
    
    # Deduplicate concepts
    unique_concepts = sorted(list(set(existing_concepts)))
    
    target_raw_path = f"dataScienceKnowledgeBase/AI Engineer/raw/{best_category}/"
    
    return {
        "suggested_category": best_category,
        "target_raw_path": target_raw_path,
        "existing_wiki_concepts": unique_concepts,
        "confidence": round(confidence, 2),
        "source": "graphify_local"
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Graphify Context Mapper")
    parser.add_argument("--title", required=True, help="Title of the content")
    parser.add_argument("--snippet", default="", help="Text snippet or summary")
    args = parser.parse_args()
    
    result = map_context_with_graphify(args.title, args.snippet)
    print(json.dumps(result, indent=2, ensure_ascii=False))
