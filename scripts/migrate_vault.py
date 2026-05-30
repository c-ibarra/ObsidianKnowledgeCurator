#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PROJECT_DIR = Path(__file__).parent.parent
VAULT_BASE = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/carlosibarra/Library/CloudStorage/OneDrive-Personal/Obsidian"))
AI_ENGINEER_DIR = VAULT_BASE / "dataScienceKnowledgeBase" / "AI Engineer"

PROTECTED_DIRS = ["dswok"]
ZONE_DIRS = ["raw", "wiki", "dev"]
# Files to keep at the root of AI Engineer
ROOT_FILES_TO_KEEP = ["Master Plan — AI Engineering Curated Series.md"]

def setup_zones(dry_run: bool):
    """Creates the standard zone directories if they don't exist."""
    for zone in ZONE_DIRS:
        zone_path = AI_ENGINEER_DIR / zone
        if not zone_path.exists():
            if dry_run:
                print(f"[DRY-RUN] Would create directory: {zone_path}")
            else:
                zone_path.mkdir(parents=True, exist_ok=True)
                print(f"[EXEC] Created directory: {zone_path}")

def migrate(dry_run: bool):
    print("=" * 80)
    print(f"VAULT MIGRATION {'(DRY RUN)' if dry_run else '(EXECUTION)'}")
    print("=" * 80)

    if not AI_ENGINEER_DIR.exists():
        print(f"Error: Target directory {AI_ENGINEER_DIR} does not exist.")
        return

    setup_zones(dry_run)
    
    raw_zone = AI_ENGINEER_DIR / "raw"
    
    moves = []
    
    for item in AI_ENGINEER_DIR.iterdir():
        # Ignore already existing zones
        if item.name in ZONE_DIRS:
            continue
            
        # Ignore protected directories
        if item.name in PROTECTED_DIRS or any(protected in str(item) for protected in PROTECTED_DIRS):
            print(f"[SKIP] Protected/Ignored: {item.name}")
            continue
            
        if item.is_dir():
            # If it's a directory, move the entire directory intact to raw/
            target_path = raw_zone / item.name
            moves.append((item, target_path))
        elif item.is_file():
            # If it's a file, check if it should stay
            if item.name in ROOT_FILES_TO_KEEP or item.name.startswith("."):
                print(f"[SKIP] Root File Kept: {item.name}")
                continue
            
            # Move loose files to raw/ as well (or perhaps wiki, but defaulting to raw for safety)
            target_path = raw_zone / item.name
            moves.append((item, target_path))

    for src, dst in moves:
        if dry_run:
            print(f"[DRY-RUN] Move:\n  From: {src}\n  To:   {dst}\n")
        else:
            # Handle cases where destination might exist
            if dst.exists():
                print(f"[WARNING] Destination {dst} already exists. Skipping {src}.")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"[EXEC] Moved: {src.name} -> raw/{src.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to move {src.name}: {e}")

    print("\nMigration pass completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Obsidian vault to Zone Architecture.")
    parser.add_argument("--execute", action="store_true", help="Actually perform the migration. If omitted, runs in dry-run mode.")
    args = parser.parse_args()
    
    migrate(dry_run=not args.execute)
