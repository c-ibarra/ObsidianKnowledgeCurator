"""Central configuration module for Obsidian Knowledge Curator (OKC).

Serves as the single source of truth for repository paths, Obsidian Vault locations,
environment settings, and shared utility paths.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Project Workspace Root: /Users/carlosibarra/projects/obsidianKnowledgeCurator
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env(env_path: Optional[Path] = None) -> None:
    """Loads variables from .env into os.environ without overriding explicit system vars."""
    target_env = env_path or (PROJECT_ROOT / ".env")
    if not target_env.exists():
        return

    with open(target_env, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key, val = stripped.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Do not override existing env vars if already set explicitly in environment
                if key and key not in os.environ:
                    os.environ[key] = val


# Initial environment load
load_env()


def resolve_vault_root() -> Path:
    """Resolves the root path of the Obsidian Vault in order of precedence:

    1. VAULT_ROOT env var
    2. OBSIDIAN_VAULT_PATH env var
    3. ~/Documents/Obsidian (standard new path)
    4. ~/Obsidian (classic fallback)
    """
    env_vault = os.environ.get("VAULT_ROOT") or os.environ.get("OBSIDIAN_VAULT_PATH")
    if env_vault:
        p = Path(env_vault).expanduser().resolve()
        if p.exists():
            return p
        # If specified path does not exist yet on filesystem, still return it as Path object
        return p

    doc_obsidian = Path.home() / "Documents" / "Obsidian"
    if doc_obsidian.exists():
        return doc_obsidian.resolve()

    home_obsidian = Path.home() / "Obsidian"
    if home_obsidian.exists():
        return home_obsidian.resolve()

    # Default fallback
    return doc_obsidian


# Core Directory Constants
VAULT_ROOT: Path = resolve_vault_root()
OBSIDIAN_VAULT_PATH: Path = VAULT_ROOT
ASSETS_IMAGES_DIR: Path = VAULT_ROOT / "assets" / "images"
GRAPHIFY_OUT_DIR: Path = PROJECT_ROOT / "graphify-out"
TEMP_DIR: Path = PROJECT_ROOT / "temp"
REPORT_DIR: Path = PROJECT_ROOT / "report"
SKILLS_DIR: Path = PROJECT_ROOT / ".agents" / "skills"
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"

# Obsidian CLI Path
OBSIDIAN_CLI_PATH: str = os.environ.get("OBSIDIAN_CLI_PATH", "/opt/homebrew/bin/obsidian")


def get_vault_root() -> Path:
    """Returns the current resolved VAULT_ROOT Path."""
    return VAULT_ROOT


def get_assets_images_dir() -> Path:
    """Returns and ensures existence of the assets/images directory."""
    ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    return ASSETS_IMAGES_DIR


def get_temp_dir() -> Path:
    """Returns and ensures existence of the project temporary directory."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def discover_vault_categories(vault_path: Optional[Path] = None) -> list[str]:
    """Scans for directories under VAULT_ROOT that contain a 'raw' subdirectory,

    excluding protected zones and hidden directories.
    """
    root_vault = vault_path or VAULT_ROOT
    if not root_vault.exists():
        return []

    categories = []
    ignored_patterns = {
        "dswok",
        "system-design-primer",
        "data-science-interviews",
        "ai-engineering-field-guide",
        "ai-system-design-interview-studio",
        ".git",
        ".obsidian",
        ".agents",
        ".trash",
        ".claudian",
        ".smart-env",
    }

    for root, dirs, _files in os.walk(root_vault):
        if any(ignored in root for ignored in ignored_patterns):
            continue
        if "raw" in dirs:
            rel_path = Path(root).relative_to(root_vault)
            categories.append(str(rel_path))

    return sorted(categories)


def relativize_path(abs_path: Path, vault_base: Optional[Path] = None) -> str:
    """Make an absolute path relative to either vault root or project root."""
    v_base = vault_base or VAULT_ROOT
    try:
        return f"vault://{abs_path.resolve().relative_to(v_base.resolve())}"
    except ValueError:
        try:
            return f"project://{abs_path.resolve().relative_to(PROJECT_ROOT.resolve())}"
        except ValueError:
            return str(abs_path)
