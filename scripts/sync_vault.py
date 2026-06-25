#!/usr/bin/env python3
import sys
import subprocess
import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

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

def main():
    parser = argparse.ArgumentParser(description="Vault Sync & Integrity Checker")
    parser.add_argument("--target-kb", default="dataScienceKnowledgeBase/AI Engineer", help="Target knowledge base folder relative to vault root")
    args = parser.parse_args()

    print("================================================================================")
    print("VAULT SYNC & INTEGRITY CHECK")
    print("================================================================================")
    
    # 1. Update Master Plan
    if not run_script("update_master_plan.py", ["--target-kb", args.target_kb]):
        sys.exit(1)
        
    # 2. Run Vault Linter
    if not run_script("vault_linter.py", ["--target-kb", args.target_kb]):
        sys.exit(1)
        
    print("================================================================================")
    print("Sync and integrity check finished successfully!")
    print("================================================================================")

if __name__ == "__main__":
    main()
