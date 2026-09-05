#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR / "scripts"))

from src.config import VAULT_ROOT, PROJECT_ROOT, discover_vault_categories
from vault_db import get_vault_db_connection, sync_db

VAULT_BASE = VAULT_ROOT

def run_script(script_name: str, args: list = None) -> bool:
    script_path = PROJECT_DIR / "scripts" / script_name
    print(f"=== Running {script_name} ===")
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
        
    proc = subprocess.run(cmd, text=True)
    if proc.returncode == 0:
        print(f"=== {script_name} completed successfully ===\n")
        return True
    else:
        print(f"=== ERROR: {script_name} failed with code {proc.returncode} ===\n", file=sys.stderr)
        return False

def discover_categories() -> list:
    return discover_vault_categories(VAULT_BASE)

def run_graphify_helper() -> bool:
    print("=== Updating Graphify Graph & KNOWLEDGE.md Index ===")
    script_path = PROJECT_DIR / "scripts" / "graphify_helper.py"
    cmd = ["uv", "tool", "run", "--python", "3.12", "--from", "graphifyy", "python", str(script_path)]
    proc = subprocess.run(cmd, text=True)
    if proc.returncode == 0:
        print("=== Graphify and KNOWLEDGE.md updated successfully ===\n")
        return True
    else:
        print(f"=== ERROR: Graphify update failed with code {proc.returncode} ===\n", file=sys.stderr)
        return False

def run_database_sync() -> bool:
    print("=== Synchronizing SQLite Index Database ===")
    try:
        conn = get_vault_db_connection()
        sync_db(VAULT_BASE, conn)
        conn.close()
        print("=== Database sync completed successfully ===\n")
        return True
    except Exception as e:
        print(f"=== ERROR: Database sync failed: {e} ===\n", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Vault Sync & Integrity Checker")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root, or 'all'")
    parser.add_argument("--normalize", action="store_true", help="Pre-flight normalization of missing headers and duplicate notes across target categories")
    args = parser.parse_args()

    print("================================================================================")
    print("VAULT SYNC & INTEGRITY CHECK")
    print("================================================================================")
    
    categories = []
    if args.target_kb.lower() == "all":
        categories = discover_categories()
        print(f"Auto-discovered categories: {categories}\n")
    else:
        categories = [args.target_kb]

    # Pre-flight normalization if requested
    if args.normalize:
        print("=== Running Pre-flight Note Normalization ===")
        for category in categories:
            raw_dir = VAULT_BASE / category / "raw"
            if raw_dir.exists():
                for subfolder in [f for f in raw_dir.iterdir() if f.is_dir() and not f.name.startswith((".", "_"))]:
                    run_script("normalize_notes.py", ["--target", str(subfolder), "--fix"])
        print("=== Pre-flight Note Normalization Complete ===\n")

    # 0. Sync SQLite database index
    if not run_database_sync():
        sys.exit(1)
    print("================================================================================")
        
    for category in categories:
        print(f"--- Processing Category: {category} ---")
        # 1. Update Master Plan
        if not run_script("update_master_plan.py", ["--target-kb", category]):
            sys.exit(1)
            
        # 2. Run Vault Linter
        if not run_script("vault_linter.py", ["--target-kb", category]):
            sys.exit(1)
            
    # 3. Rebuild Graphify Index and KNOWLEDGE.md
    if not run_graphify_helper():
        sys.exit(1)
        
    print("================================================================================")
    print("Sync and integrity check finished successfully!")
    print("================================================================================")

if __name__ == "__main__":
    main()

