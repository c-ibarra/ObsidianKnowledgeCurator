#!/usr/bin/env python3
"""Setup wizard and environment configurator for Obsidian Knowledge Curator (OKC).

Supports both interactive terminal prompts and non-interactive Antigravity agent execution (/okc-setup).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / ".env.template"
ENV_PATH = PROJECT_ROOT / ".env"

# List of critical CLI tools and their purpose
SYSTEM_DEPENDENCIES = {
    "uv": {
        "desc": "Fast Python package and virtualenv manager",
        "install_hint": "curl -LsSf https://astral.sh/uv/install.sh | sh",
        "critical": True,
    },
    "obsidian": {
        "desc": "Obsidian CLI for note and daily commands",
        "install_hint": "Install Obsidian Shell plugin or brew install obsidian-cli",
        "critical": False,
    },
    "yt-dlp": {
        "desc": "YouTube audio/video downloader for transcript extraction",
        "install_hint": "brew install yt-dlp",
        "critical": True,
    },
    "buzz": {
        "desc": "Local Whisper transcription engine (Buzz CLI)",
        "install_hint": "brew install buzz-captions or check local Buzz installation",
        "critical": False,
    },
    "ffmpeg": {
        "desc": "Audio/video stream processor and format converter",
        "install_hint": "brew install ffmpeg",
        "critical": False,
    },
}


def load_existing_env() -> Dict[str, str]:
    """Reads existing .env file into a dictionary without modifying os.environ."""
    env_vars: Dict[str, str] = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    key, val = stripped.split("=", 1)
                    env_vars[key.strip()] = val.strip().strip('"').strip("'")
    return env_vars


def check_dependencies() -> Dict[str, bool]:
    """Checks presence of required system binaries on PATH."""
    print("\n================================================================================")
    print("🔍 SYSTEM DEPENDENCY CHECK")
    print("================================================================================")
    results: Dict[str, bool] = {}
    
    for tool_name, info in SYSTEM_DEPENDENCIES.items():
        bin_path = shutil.which(tool_name)
        if bin_path:
            print(f"  ✅ {tool_name:<10} : Found ({bin_path})")
            results[tool_name] = True
        else:
            status = "⚠️ Optional missing" if not info["critical"] else "❌ Required missing"
            print(f"  {status:<18} {tool_name:<10} : {info['desc']}")
            print(f"     Hint: {info['install_hint']}")
            results[tool_name] = False
            
    print("================================================================================\n")
    return results


def detect_obsidian_cli() -> str:
    """Finds obsidian CLI executable path."""
    which_path = shutil.which("obsidian")
    if which_path:
        return which_path

    common_paths = [
        "/opt/homebrew/bin/obsidian",
        "/usr/local/bin/obsidian",
        Path.home() / ".local/bin/obsidian",
    ]
    for p in common_paths:
        p_obj = Path(p)
        if p_obj.exists() and os.access(p_obj, os.X_OK):
            return str(p_obj)

    return "/opt/homebrew/bin/obsidian"


def detect_default_vault_path(existing_vars: Dict[str, str]) -> str:
    """Detects most likely Obsidian Vault location."""
    # 1. Existing .env value
    if existing_vars.get("VAULT_ROOT") and Path(existing_vars["VAULT_ROOT"]).exists():
        return existing_vars["VAULT_ROOT"]
    if existing_vars.get("OBSIDIAN_VAULT_PATH") and Path(existing_vars["OBSIDIAN_VAULT_PATH"]).exists():
        return existing_vars["OBSIDIAN_VAULT_PATH"]

    # 2. Standard documents folder
    docs_obsidian = Path.home() / "Documents" / "Obsidian"
    if docs_obsidian.exists():
        return str(docs_obsidian)

    home_obsidian = Path.home() / "Obsidian"
    if home_obsidian.exists():
        return str(home_obsidian)

    return str(docs_obsidian)


def prompt_user(question: str, default: str) -> str:
    """Prompts the user interactively with a default fallback."""
    try:
        val = input(f"{question} [{default}]: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default value.")
        return default


def generate_env_content(config: Dict[str, str]) -> str:
    """Generates clean .env content based on template formatting and user config."""
    template_content = ""
    if TEMPLATE_PATH.exists():
        template_content = TEMPLATE_PATH.read_text(encoding="utf-8")
    else:
        # Fallback raw template
        template_content = """# Workspace & Obsidian Vault Parameters
VAULT_ROOT="{VAULT_ROOT}"
OBSIDIAN_VAULT_PATH="{OBSIDIAN_VAULT_PATH}"
OBSIDIAN_CLI_PATH="{OBSIDIAN_CLI_PATH}"

# Ingestion & Scoring Limits
MAX_TRANSCRIPT_CHARS={MAX_TRANSCRIPT_CHARS}
CONTEXT_DEGRADATION_THRESHOLD={CONTEXT_DEGRADATION_THRESHOLD}
MIN_TECHNICAL_SCORE={MIN_TECHNICAL_SCORE}

# Logging & Environment Control
ENV="{ENV}"
LOG_LEVEL="{LOG_LEVEL}"
UV_PROJECT_ENVIRONMENT="{UV_PROJECT_ENVIRONMENT}"

# LLM Providers & Hybrid Engine Configuration
DENSITY_GRADER_PROVIDER="{DENSITY_GRADER_PROVIDER}"
GEMINI_API_KEY="{GEMINI_API_KEY}"
OLLAMA_HOST="{OLLAMA_HOST}"
OLLAMA_MODEL="{OLLAMA_MODEL}"
"""

    # Replace or format parameters
    lines = template_content.splitlines()
    output_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, _ = stripped.split("=", 1)
            key = key.strip()
            if key in config:
                val = config[key]
                # Quote strings with spaces or paths
                if any(c in val for c in ["/", " ", ":", "http"]) and not val.isdigit() and not val.startswith('"'):
                    val = f'"{val}"'
                output_lines.append(f"{key}={val}")
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    return "\n".join(output_lines) + "\n"


def run_sync_pipeline() -> bool:
    """Runs sync_vault.py to build SQLite index and Graphify."""
    print("\n🚀 Running initial vault sync and Graphify index build...")
    sync_script = PROJECT_ROOT / "scripts" / "sync_vault.py"
    cmd = ["uv", "run", "python", str(sync_script), "--target-kb", "all"]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return proc.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Obsidian Knowledge Curator (OKC) — Project Setup Wizard"
    )
    parser.add_argument("--vault-path", help="Absolute path to the Obsidian Vault directory")
    parser.add_argument("--cli-path", help="Path to obsidian CLI executable")
    parser.add_argument("--gemini-key", help="Gemini API Key for LLM operations")
    parser.add_argument("--provider", choices=["gemini", "ollama"], help="Density grader provider")
    parser.add_argument("--non-interactive", action="store_true", help="Run in headless non-interactive mode")
    parser.add_argument("--check-deps", action="store_true", help="Check system dependencies and exit")
    parser.add_argument("--sync", action="store_true", help="Run vault sync and Graphify rebuild after setup")

    args = parser.parse_args()

    # 1. Dependency check only
    if args.check_deps:
        check_dependencies()
        sys.exit(0)

    print("================================================================================")
    print("🛠️  OBSIDIAN KNOWLEDGE CURATOR — SETUP WIZARD")
    print("================================================================================")

    # 2. Check dependencies
    dep_results = check_dependencies()

    existing_vars = load_existing_env()
    detected_vault = detect_default_vault_path(existing_vars)
    detected_cli = detect_obsidian_cli()

    config: Dict[str, str] = {
        "VAULT_ROOT": existing_vars.get("VAULT_ROOT", detected_vault),
        "OBSIDIAN_VAULT_PATH": existing_vars.get("OBSIDIAN_VAULT_PATH", detected_vault),
        "OBSIDIAN_CLI_PATH": existing_vars.get("OBSIDIAN_CLI_PATH", detected_cli),
        "MAX_TRANSCRIPT_CHARS": existing_vars.get("MAX_TRANSCRIPT_CHARS", "50000"),
        "CONTEXT_DEGRADATION_THRESHOLD": existing_vars.get("CONTEXT_DEGRADATION_THRESHOLD", "0.40"),
        "MIN_TECHNICAL_SCORE": existing_vars.get("MIN_TECHNICAL_SCORE", "60"),
        "ENV": existing_vars.get("ENV", "development"),
        "LOG_LEVEL": existing_vars.get("LOG_LEVEL", "INFO"),
        "UV_PROJECT_ENVIRONMENT": existing_vars.get("UV_PROJECT_ENVIRONMENT", "obsidianKnowledgeCurator"),
        "DENSITY_GRADER_PROVIDER": existing_vars.get("DENSITY_GRADER_PROVIDER", "gemini"),
        "GEMINI_API_KEY": existing_vars.get("GEMINI_API_KEY", ""),
        "OLLAMA_HOST": existing_vars.get("OLLAMA_HOST", "http://localhost:11434"),
        "OLLAMA_MODEL": existing_vars.get("OLLAMA_MODEL", "llama3.2"),
    }

    # Override with CLI args if provided
    if args.vault_path:
        config["VAULT_ROOT"] = str(Path(args.vault_path).expanduser().resolve())
        config["OBSIDIAN_VAULT_PATH"] = config["VAULT_ROOT"]
    if args.cli_path:
        config["OBSIDIAN_CLI_PATH"] = args.cli_path
    if args.gemini_key:
        config["GEMINI_API_KEY"] = args.gemini_key
    if args.provider:
        config["DENSITY_GRADER_PROVIDER"] = args.provider

    # Interactive mode prompts
    if not args.non_interactive:
        print("Please review and configure the settings (Press Enter to accept defaults):\n")
        
        vault_input = prompt_user("1. Obsidian Vault Path (VAULT_ROOT)", config["VAULT_ROOT"])
        config["VAULT_ROOT"] = str(Path(vault_input).expanduser().resolve())
        config["OBSIDIAN_VAULT_PATH"] = config["VAULT_ROOT"]

        cli_input = prompt_user("2. Obsidian CLI Path (OBSIDIAN_CLI_PATH)", config["OBSIDIAN_CLI_PATH"])
        config["OBSIDIAN_CLI_PATH"] = cli_input

        provider_input = prompt_user("3. Density Grader Provider (gemini | ollama)", config["DENSITY_GRADER_PROVIDER"])
        config["DENSITY_GRADER_PROVIDER"] = provider_input.lower()

        if config["DENSITY_GRADER_PROVIDER"] == "gemini":
            gemini_input = prompt_user("4. GEMINI_API_KEY (optional if set in system env)", config["GEMINI_API_KEY"])
            config["GEMINI_API_KEY"] = gemini_input
        else:
            ollama_host = prompt_user("4. Ollama Host URL", config["OLLAMA_HOST"])
            config["OLLAMA_HOST"] = ollama_host
            ollama_model = prompt_user("5. Ollama Model Name", config["OLLAMA_MODEL"])
            config["OLLAMA_MODEL"] = ollama_model

    # Validate Vault directory existence
    vault_path_obj = Path(config["VAULT_ROOT"])
    if not vault_path_obj.exists():
        print(f"\n⚠️  Notice: Vault directory does not exist yet at: {vault_path_obj}")
        if not args.non_interactive:
            create_choice = prompt_user("Do you want to create this directory now? (y/n)", "y")
            if create_choice.lower() in ("y", "yes"):
                vault_path_obj.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created Vault directory at: {vault_path_obj}")

    # Write .env file
    env_content = generate_env_content(config)
    ENV_PATH.write_text(env_content, encoding="utf-8")
    print(f"\n✅ Successfully generated/updated private configuration at: {ENV_PATH}")

    # Update graphify root if vault exists
    if vault_path_obj.exists():
        graphify_root_file = PROJECT_ROOT / "graphify-out" / ".graphify_root"
        graphify_root_file.parent.mkdir(parents=True, exist_ok=True)
        graphify_root_file.write_text(str(vault_path_obj), encoding="utf-8")

    # Run sync if requested
    if args.sync:
        run_sync_pipeline()
    elif not args.non_interactive:
        sync_choice = prompt_user("\nDo you want to run an initial Vault Sync and Graphify build now? (y/n)", "y")
        if sync_choice.lower() in ("y", "yes"):
            run_sync_pipeline()

    print("\n================================================================================")
    print("🎉 SETUP COMPLETE!")
    print("  - Vault Root       :", config["VAULT_ROOT"])
    print("  - LLM Provider     :", config["DENSITY_GRADER_PROVIDER"])
    print("  - CLI Executable   :", config["OBSIDIAN_CLI_PATH"])
    print("  - Private Env File :", ENV_PATH)
    print("================================================================================\n")


if __name__ == "__main__":
    main()
