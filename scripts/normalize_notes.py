#!/usr/bin/env python3
"""CLI utility to audit, deduplicate, and normalize Obsidian vault notes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR / "scripts"))

from src.config import VAULT_ROOT
from src.agent_tools.note_normalizer import NoteNormalizer


def main():
    parser = argparse.ArgumentParser(
        description="Audit, deduplicate, and normalize note headers across Obsidian categories."
    )
    parser.add_argument(
        "--target",
        "-t",
        required=True,
        help="Target folder path (relative to VAULT_ROOT or absolute path)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply modifications: archive duplicates/stubs and inject canonical headers",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Atomically synchronize SQLite database and update Master Plan after fixing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate run without modifying or moving any files (default if --fix not specified)",
    )

    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.is_absolute():
        target_path = VAULT_ROOT / target_path

    if not target_path.exists() or not target_path.is_dir():
        print(f"❌ Error: Target directory does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    is_dry_run = args.dry_run or (not args.fix)

    print("=" * 80)
    print("OKC NOTE NORMALIZER & IMPORT SANITIZER")
    print("=" * 80)
    print(f"Target Directory: {target_path}")
    print(f"Mode: {'🔍 AUDIT ONLY (Dry Run)' if is_dry_run else '⚡ EXECUTE FIXES'}")
    print(f"Atomic Sync: {'Enabled' if args.sync else 'Disabled'}")
    print("-" * 80)

    normalizer = NoteNormalizer(target_dir=target_path, dry_run=is_dry_run, auto_sync=args.sync)
    report = normalizer.run()

    total_scanned = (
        len(report["canonical"])
        + len(report["normalized"])
        + len(report["duplicates"])
        + len(report["stubs"])
    )

    print(f"Notes Scanned: {total_scanned}")
    print(f"  🟢 Canonical (Compliant):      {len(report['canonical'])}")
    print(f"  🟡 Missing Header (Fixed/Need): {len(report['normalized'])}")
    print(f"  🟠 Exact Duplicates:           {len(report['duplicates'])}")
    print(f"  🔴 Empty Stubs:                {len(report['stubs'])}")

    if report["duplicates"]:
        print("\n[!] Exact Duplicates Detected:")
        for dup, orig in report["duplicates"]:
            action = "Archived to _archive/" if not is_dry_run else "Would archive to _archive/"
            print(f"  - {dup.name} (duplicate of {orig.name}) -> {action}")

    if report["stubs"]:
        print("\n[!] Empty Stubs Detected (< 50 bytes):")
        for stub in report["stubs"]:
            action = "Archived to _archive/" if not is_dry_run else "Would archive to _archive/"
            print(f"  - {stub.name} -> {action}")

    if report["normalized"]:
        print(f"\n[!] Headers {'Injected' if not is_dry_run else 'Missing (Run with --fix to inject)'}:")
        for f in report["normalized"][:10]:
            print(f"  - {f.name}")
        if len(report["normalized"]) > 10:
            print(f"  ... and {len(report['normalized']) - 10} more.")

    print("\n" + "=" * 80)
    if is_dry_run and (report["normalized"] or report["duplicates"] or report["stubs"]):
        print("💡 Recommendations found. Run with `--fix --sync` to apply changes safely.")
    else:
        print("✅ Normalization completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
