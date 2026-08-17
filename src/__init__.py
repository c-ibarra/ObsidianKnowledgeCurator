"""Obsidian Knowledge Curator (OKC) package."""

from src.config import (
    PROJECT_ROOT,
    VAULT_ROOT,
    OBSIDIAN_VAULT_PATH,
    ASSETS_IMAGES_DIR,
    GRAPHIFY_OUT_DIR,
    TEMP_DIR,
    REPORT_DIR,
    SKILLS_DIR,
    SCRIPTS_DIR,
    OBSIDIAN_CLI_PATH,
    get_vault_root,
    get_assets_images_dir,
    get_temp_dir,
    discover_vault_categories,
    relativize_path,
)

__all__ = [
    "PROJECT_ROOT",
    "VAULT_ROOT",
    "OBSIDIAN_VAULT_PATH",
    "ASSETS_IMAGES_DIR",
    "GRAPHIFY_OUT_DIR",
    "TEMP_DIR",
    "REPORT_DIR",
    "SKILLS_DIR",
    "SCRIPTS_DIR",
    "OBSIDIAN_CLI_PATH",
    "get_vault_root",
    "get_assets_images_dir",
    "get_temp_dir",
    "discover_vault_categories",
    "relativize_path",
]
