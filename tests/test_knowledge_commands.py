#!/usr/bin/env python3
"""Tests for scripts/knowledge_commands.py's graphify-daemon integration:
`_resolve_source_file` (the vault:// vs no-scheme addressing difference
between the legacy graphify_helper.py graph.json and graphify-daemon's)
and `_load_graph_data`'s daemon-first/legacy-fallback behavior.

No live daemon required -- these test the pure resolution/fallback logic
against synthetic files.
"""
import json
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR / "scripts"))

import knowledge_commands as kc


def test_resolve_source_file_vault_scheme():
    fs_path, obsidian_uri, rel_path_str = kc._resolve_source_file("vault://notes/foo.md")
    assert fs_path == kc.VAULT_BASE / "notes/foo.md"
    assert rel_path_str == "notes/foo.md"
    assert obsidian_uri.startswith("obsidian://open?vault=")
    print("test_resolve_source_file_vault_scheme: PASS")


def test_resolve_source_file_project_scheme():
    fs_path, obsidian_uri, rel_path_str = kc._resolve_source_file("project://scripts/okc_doctor.py")
    assert fs_path == kc.PROJECT_DIR / "scripts/okc_doctor.py"
    assert rel_path_str == "scripts/okc_doctor.py"
    assert obsidian_uri == f"file://{fs_path}"
    print("test_resolve_source_file_project_scheme: PASS")


def test_resolve_source_file_bare_daemon_scheme():
    # graphify-daemon's graph.json is vault-only and omits the scheme
    # prefix entirely -- every source_file it emits is already
    # vault-relative, same as a `vault://`-prefixed legacy one.
    fs_path, obsidian_uri, rel_path_str = kc._resolve_source_file("2026-08-19.md")
    assert fs_path == kc.VAULT_BASE / "2026-08-19.md"
    assert rel_path_str == "2026-08-19.md"
    assert obsidian_uri.startswith("obsidian://open?vault=")
    print("test_resolve_source_file_bare_daemon_scheme: PASS")


def test_load_graph_data_prefers_daemon_when_present():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "daemon_graph.json"
        daemon_graph.write_text(json.dumps({"nodes": [{"label": "from-daemon"}], "links": []}))

        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            data, path = kc._load_graph_data()
            assert path == daemon_graph
            assert data["nodes"][0]["label"] == "from-daemon"
        finally:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_prefers_daemon_when_present: PASS")


def test_load_graph_data_falls_back_to_legacy_when_daemon_missing():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "does_not_exist.json"
        legacy_dir = tmp_path / "graphify-out"
        legacy_dir.mkdir()
        legacy_graph = legacy_dir / "graph.json"
        legacy_graph.write_text(json.dumps({"nodes": [{"label": "from-legacy"}], "links": []}))

        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            data, path = kc._load_graph_data()
            assert path == legacy_graph
            assert data["nodes"][0]["label"] == "from-legacy"
        finally:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_falls_back_to_legacy_when_daemon_missing: PASS")


def test_load_graph_data_returns_none_when_neither_exists():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "does_not_exist.json"

        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            data, path = kc._load_graph_data()
            assert data is None
            assert path is None
        finally:
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_returns_none_when_neither_exists: PASS")


def test_load_graph_data_local_backend_never_reads_daemon():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "daemon_graph.json"
        daemon_graph.write_text(json.dumps({"nodes": [{"label": "from-daemon"}], "links": []}))
        legacy_dir = tmp_path / "graphify-out"
        legacy_dir.mkdir()
        legacy_graph = legacy_dir / "graph.json"
        legacy_graph.write_text(json.dumps({"nodes": [{"label": "from-legacy"}], "links": []}))

        original_backend = kc.GRAPHIFY_BACKEND
        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_BACKEND = "local"
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            data, path = kc._load_graph_data()
            assert path == legacy_graph
            assert data["nodes"][0]["label"] == "from-legacy"
        finally:
            kc.GRAPHIFY_BACKEND = original_backend
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_local_backend_never_reads_daemon: PASS")


def test_load_graph_data_remote_backend_uses_daemon_when_present():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "daemon_graph.json"
        daemon_graph.write_text(json.dumps({"nodes": [{"label": "from-daemon"}], "links": []}))

        original_backend = kc.GRAPHIFY_BACKEND
        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_BACKEND = "remote"
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            data, path = kc._load_graph_data()
            assert path == daemon_graph
            assert data["nodes"][0]["label"] == "from-daemon"
        finally:
            kc.GRAPHIFY_BACKEND = original_backend
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_remote_backend_uses_daemon_when_present: PASS")


def test_load_graph_data_remote_backend_raises_instead_of_falling_back():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        daemon_graph = tmp_path / "does_not_exist.json"
        legacy_dir = tmp_path / "graphify-out"
        legacy_dir.mkdir()
        (legacy_dir / "graph.json").write_text(json.dumps({"nodes": [{"label": "from-legacy"}], "links": []}))

        original_backend = kc.GRAPHIFY_BACKEND
        original_daemon_path = kc.GRAPHIFY_DAEMON_GRAPH_JSON
        original_project_dir = kc.PROJECT_DIR
        try:
            kc.GRAPHIFY_BACKEND = "remote"
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = daemon_graph
            kc.PROJECT_DIR = tmp_path
            try:
                kc._load_graph_data()
            except kc.GraphBackendUnavailable:
                pass
            else:
                raise AssertionError("expected GraphBackendUnavailable, no exception was raised")
        finally:
            kc.GRAPHIFY_BACKEND = original_backend
            kc.GRAPHIFY_DAEMON_GRAPH_JSON = original_daemon_path
            kc.PROJECT_DIR = original_project_dir
    print("test_load_graph_data_remote_backend_raises_instead_of_falling_back: PASS")


def main():
    print("=== RUNNING KNOWLEDGE_COMMANDS GRAPHIFY-DAEMON INTEGRATION TESTS ===")
    test_resolve_source_file_vault_scheme()
    test_resolve_source_file_project_scheme()
    test_resolve_source_file_bare_daemon_scheme()
    test_load_graph_data_prefers_daemon_when_present()
    test_load_graph_data_falls_back_to_legacy_when_daemon_missing()
    test_load_graph_data_returns_none_when_neither_exists()
    test_load_graph_data_local_backend_never_reads_daemon()
    test_load_graph_data_remote_backend_uses_daemon_when_present()
    test_load_graph_data_remote_backend_raises_instead_of_falling_back()
    print("=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    main()
