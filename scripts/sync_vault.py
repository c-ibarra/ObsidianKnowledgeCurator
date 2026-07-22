#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

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
    categories = []
    # Scan for directories under VAULT_BASE that contain a 'raw' subdirectory
    for root, dirs, files in os.walk(VAULT_BASE):
        if any(ignored in root for ignored in ["dswok", ".git", ".obsidian", ".agents"]):
            continue
        if "raw" in dirs:
            rel_path = Path(root).relative_to(VAULT_BASE)
            categories.append(str(rel_path))
    return sorted(categories)

def run_graphify_helper() -> bool:
    print("=== Updating Graphify Graph & KNOWLEDGE.md Index ===")
    script_path = PROJECT_DIR / "scripts" / "graphify_helper.py"
    cmd = ["uv", "tool", "run", "--from", "graphifyy", "python", str(script_path)]
    proc = subprocess.run(cmd, text=True)
    if proc.returncode == 0:
        print("=== Graphify and KNOWLEDGE.md updated successfully ===\n")
        return True
    else:
        print(f"=== ERROR: Graphify update failed with code {proc.returncode} ===\n", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Vault Sync & Integrity Checker")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root, or 'all'")
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

