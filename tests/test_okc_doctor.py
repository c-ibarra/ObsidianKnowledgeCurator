#!/usr/bin/env python3
"""Tests for scripts/okc_doctor.py's `_fetch_daemon_graph_stats`: parsing
graphify-daemon's `graph_stats` MCP response, and falling back to None
(so check_graphify falls back to the legacy graph.json read) when the
daemon is unreachable or misconfigured.

No live daemon required.
"""
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR / "scripts"))

import okc_doctor as doctor


def test_returns_none_without_api_key():
    original_key = doctor.GRAPHIFY_DAEMON_API_KEY
    try:
        doctor.GRAPHIFY_DAEMON_API_KEY = ""
        assert doctor._fetch_daemon_graph_stats() is None
    finally:
        doctor.GRAPHIFY_DAEMON_API_KEY = original_key
    print("test_returns_none_without_api_key: PASS")


def test_returns_none_when_daemon_unreachable():
    # An unreachable local port -- no mocking needed, this genuinely fails
    # fast (connection refused) rather than needing the real daemon up.
    original_url = doctor.GRAPHIFY_DAEMON_URL
    original_key = doctor.GRAPHIFY_DAEMON_API_KEY
    try:
        doctor.GRAPHIFY_DAEMON_URL = "http://127.0.0.1:1"
        doctor.GRAPHIFY_DAEMON_API_KEY = "irrelevant-for-this-test"
        assert doctor._fetch_daemon_graph_stats() is None
    finally:
        doctor.GRAPHIFY_DAEMON_URL = original_url
        doctor.GRAPHIFY_DAEMON_API_KEY = original_key
    print("test_returns_none_when_daemon_unreachable: PASS")


def _fake_sse_response(text_field: str) -> str:
    import json as _json

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"content": [{"text": text_field, "type": "text"}], "isError": False},
    }
    return f"event: message\r\ndata: {_json.dumps(payload)}\r\n\r\n"


def test_parses_nodes_and_edges_from_sse_body():
    # Reproduces the exact body shape graphify-daemon returns (verified
    # live against the real daemon: `event: message\r\ndata: {...}\r\n\r\n`,
    # content-type text/event-stream).
    body = _fake_sse_response("Nodes: 21070\nEdges: 21915\nCommunities: 0\nEXTRACTED: 100%\n")

    class FakeResponse:
        text = body

        def raise_for_status(self):
            pass

    original_post = doctor.requests.post
    try:
        doctor.requests.post = lambda *a, **k: FakeResponse()
        doctor.GRAPHIFY_DAEMON_API_KEY = "fake-key-for-this-test"
        result = doctor._fetch_daemon_graph_stats()
        assert result == (21070, 21915)
    finally:
        doctor.requests.post = original_post
    print("test_parses_nodes_and_edges_from_sse_body: PASS")


def test_returns_none_on_unparsable_body():
    class FakeResponse:
        text = "not an sse body at all"

        def raise_for_status(self):
            pass

    original_post = doctor.requests.post
    try:
        doctor.requests.post = lambda *a, **k: FakeResponse()
        doctor.GRAPHIFY_DAEMON_API_KEY = "fake-key-for-this-test"
        assert doctor._fetch_daemon_graph_stats() is None
    finally:
        doctor.requests.post = original_post
    print("test_returns_none_on_unparsable_body: PASS")


def test_resolve_graphify_source_local_backend_skips_daemon():
    with tempfile.TemporaryDirectory() as tmp:
        graph_file = Path(tmp) / "graph.json"
        graph_file.write_text('{"nodes": [{"id": "a"}], "links": []}')

        original_backend = doctor.GRAPHIFY_BACKEND
        original_post = doctor.requests.post

        def _fail_if_called(*a, **k):
            raise AssertionError("requests.post should never be called in local mode")

        try:
            doctor.GRAPHIFY_BACKEND = "local"
            doctor.requests.post = _fail_if_called
            report = doctor.DoctorReport()
            doctor._resolve_graphify_source(report, graph_file)
            assert report.graph_nodes == 1
            assert report.graph_source == "legacy"
        finally:
            doctor.GRAPHIFY_BACKEND = original_backend
            doctor.requests.post = original_post
    print("test_resolve_graphify_source_local_backend_skips_daemon: PASS")


def test_resolve_graphify_source_remote_backend_uses_daemon():
    with tempfile.TemporaryDirectory() as tmp:
        body = _fake_sse_response("Nodes: 5\nEdges: 3\n")

        class FakeResponse:
            text = body

            def raise_for_status(self):
                pass

        original_backend = doctor.GRAPHIFY_BACKEND
        original_post = doctor.requests.post
        original_key = doctor.GRAPHIFY_DAEMON_API_KEY
        try:
            doctor.GRAPHIFY_BACKEND = "remote"
            doctor.requests.post = lambda *a, **k: FakeResponse()
            doctor.GRAPHIFY_DAEMON_API_KEY = "fake-key-for-this-test"
            report = doctor.DoctorReport()
            doctor._resolve_graphify_source(report, Path(tmp) / "graph.json")
            assert (report.graph_nodes, report.graph_edges) == (5, 3)
            assert report.graph_source == "daemon"
        finally:
            doctor.GRAPHIFY_BACKEND = original_backend
            doctor.requests.post = original_post
            doctor.GRAPHIFY_DAEMON_API_KEY = original_key
    print("test_resolve_graphify_source_remote_backend_uses_daemon: PASS")


def test_resolve_graphify_source_remote_backend_raises_instead_of_falling_back():
    with tempfile.TemporaryDirectory() as tmp:
        graph_file = Path(tmp) / "graph.json"
        graph_file.write_text('{"nodes": [{"id": "a"}], "links": []}')

        original_backend = doctor.GRAPHIFY_BACKEND
        original_url = doctor.GRAPHIFY_DAEMON_URL
        original_key = doctor.GRAPHIFY_DAEMON_API_KEY
        try:
            doctor.GRAPHIFY_BACKEND = "remote"
            doctor.GRAPHIFY_DAEMON_URL = "http://127.0.0.1:1"
            doctor.GRAPHIFY_DAEMON_API_KEY = "irrelevant-for-this-test"
            report = doctor.DoctorReport()
            try:
                doctor._resolve_graphify_source(report, graph_file)
            except doctor.GraphBackendUnavailable:
                pass
            else:
                raise AssertionError("expected GraphBackendUnavailable, no exception was raised")
            # Must not have silently fallen back to reading graph_file.
            assert report.graph_nodes == 0
        finally:
            doctor.GRAPHIFY_BACKEND = original_backend
            doctor.GRAPHIFY_DAEMON_URL = original_url
            doctor.GRAPHIFY_DAEMON_API_KEY = original_key
    print("test_resolve_graphify_source_remote_backend_raises_instead_of_falling_back: PASS")


def test_check_orphaned_assets_detection_and_archival():
    with tempfile.TemporaryDirectory() as tmp_vault:
        vault_path = Path(tmp_vault)
        img_dir = vault_path / "assets" / "images"
        img_dir.mkdir(parents=True)

        # Create images
        (img_dir / "referenced.png").write_text("fake png 1")
        (img_dir / "orphaned.png").write_text("fake png 2")
        (img_dir / "another_orphan.jpg").write_text("fake jpg")

        # Create a note referencing referenced.png
        note_path = vault_path / "note.md"
        note_path.write_text("Here is an embed: ![[assets/images/referenced.png]]")

        original_vault = doctor.VAULT_ROOT
        try:
            doctor.VAULT_ROOT = vault_path

            # 1. Audit mode (auto_archive=False)
            report = doctor.DoctorReport()
            doctor.check_orphaned_assets(report, auto_archive=False)
            assert report.total_images == 3
            assert report.orphaned_images == 2
            assert report.archived_assets_count == 0
            assert (img_dir / "orphaned.png").exists()

            # 2. Archive mode (auto_archive=True)
            report_fix = doctor.DoctorReport()
            doctor.check_orphaned_assets(report_fix, auto_archive=True)
            assert report_fix.archived_assets_count == 2
            assert report_fix.orphaned_images == 0
            assert report_fix.total_images == 1
            assert not (img_dir / "orphaned.png").exists()
            assert (img_dir / "_archive" / "orphaned.png").exists()
            assert (img_dir / "_archive" / "another_orphan.jpg").exists()
            assert (img_dir / "referenced.png").exists()
        finally:
            doctor.VAULT_ROOT = original_vault
    print("test_check_orphaned_assets_detection_and_archival: PASS")


def main():
    print("=== RUNNING OKC_DOCTOR TESTS ===")
    test_returns_none_without_api_key()
    test_returns_none_when_daemon_unreachable()
    test_parses_nodes_and_edges_from_sse_body()
    test_returns_none_on_unparsable_body()
    test_resolve_graphify_source_local_backend_skips_daemon()
    test_resolve_graphify_source_remote_backend_uses_daemon()
    test_resolve_graphify_source_remote_backend_raises_instead_of_falling_back()
    test_check_orphaned_assets_detection_and_archival()
    print("=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    main()
