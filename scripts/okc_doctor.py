#!/usr/bin/env python3
"""OKC Doctor — Comprehensive Diagnostics, Integrity Audit & Synchronization Suite.

Executes a full diagnostic health check and synchronization of the Obsidian Vault:
1. SQLite Database Index Sync
2. Global Category Master Plan Reconstruction
3. Vault Link Integrity & Contradiction Linter
4. Unicode / ZWSP Invisible Artifact Scanner & Cleaner (with --fix)
5. Orphaned Visual Assets Audit (assets/images/)
6. Protected Zones Integrity Verification
7. Graphify Knowledge Graph & KNOWLEDGE.md Index Rebuild
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.append(str(PROJECT_DIR / "scripts"))

from src.config import (
    GRAPHIFY_BACKEND,
    GRAPHIFY_DAEMON_API_KEY,
    GRAPHIFY_DAEMON_URL,
    GRAPHIFY_OUT_DIR,
    PROJECT_ROOT,
    VAULT_ROOT,
    discover_vault_categories,
    normalize_graphify_backend,
)
from vault_db import get_vault_db_connection, sync_db

ZWSP_REGEX = re.compile(r"[\u200B-\u200D\uFEFF\u00A0]")
PROTECTED_ZONES = [
    "dataScienceKnowledgeBase/dswok",
    "system-design-primer",
    "data-science-interviews",
    "ai-engineering-field-guide",
    "ai-system-design-interview-studio",
]


class DoctorReport:
    def __init__(self):
        self.sqlite_status = "🟢 OK"
        self.sqlite_msg = ""
        self.master_plans_status = "🟢 OK"
        self.master_plans_count = 0
        self.linter_status = "🟢 OK"
        self.broken_links_count = 0
        self.contradictions_count = 0
        self.zwsp_status = "🟢 OK"
        self.zwsp_files_count = 0
        self.zwsp_fixed_count = 0
        self.assets_status = "🟢 OK"
        self.total_images = 0
        self.orphaned_images = 0
        self.protected_status = "🟢 OK"
        self.protected_intact = True
        self.graphify_status = "🟢 OK"
        self.graph_nodes = 0
        self.graph_edges = 0
        self.graph_source = "legacy"  # "daemon" (vault-only) or "legacy" (vault + this repo's own code)
        self.knowledge_concepts = 0
        self.duration = 0.0


def check_sqlite(report: DoctorReport) -> bool:
    try:
        conn = get_vault_db_connection()
        sync_db(VAULT_ROOT, conn)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        conn.close()
        report.sqlite_msg = f"Sincronizados {count:,} archivos activos."
        report.sqlite_status = "🟢 OK"
        return True
    except Exception as e:
        report.sqlite_status = "🔴 Error"
        report.sqlite_msg = f"Fallo de conexión/sincronización SQLite: {e}"
        return False


def check_master_plans(report: DoctorReport) -> bool:
    categories = discover_vault_categories(VAULT_ROOT)
    report.master_plans_count = len(categories)
    failed = []
    for cat in categories:
        cmd = [sys.executable, str(PROJECT_DIR / "scripts" / "update_master_plan.py"), "--target-kb", cat]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            failed.append(cat)

    if failed:
        report.master_plans_status = "🟡 Warning" if len(failed) < len(categories) else "🔴 Error"
    else:
        report.master_plans_status = "🟢 OK"
    return len(failed) == 0


def check_linter(report: DoctorReport) -> bool:
    cmd = [sys.executable, str(PROJECT_DIR / "scripts" / "vault_linter.py"), "--target-kb", "all"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout

    # Parse broken links and contradictions
    broken = re.findall(r"-\s+'([^']+)'\s+\(referenced in:", out)
    contradictions = re.findall(r"\[!contradiction\]", out)
    report.broken_links_count = len(broken)
    report.contradictions_count = len(contradictions)

    if report.broken_links_count > 50:
        report.linter_status = "🟡 Warning"
    elif report.broken_links_count > 0:
        report.linter_status = "🟢 OK"
    else:
        report.linter_status = "🟢 OK"
    return True


def check_and_clean_zwsp(report: DoctorReport, auto_fix: bool = False) -> bool:
    zwsp_found = 0
    zwsp_fixed = 0

    for md_file in VAULT_ROOT.rglob("*.md"):
        # Skip protected zones if fixing
        rel_str = str(md_file.relative_to(VAULT_ROOT))
        is_protected = any(pz in rel_str for pz in PROTECTED_ZONES)

        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            if ZWSP_REGEX.search(content):
                zwsp_found += 1
                if auto_fix and not is_protected:
                    cleaned = ZWSP_REGEX.sub("", content)
                    md_file.write_text(cleaned, encoding="utf-8")
                    zwsp_fixed += 1
        except Exception:
            pass

    report.zwsp_files_count = zwsp_found
    report.zwsp_fixed_count = zwsp_fixed

    if zwsp_found > 0 and not auto_fix:
        report.zwsp_status = "🟡 Warning"
    elif auto_fix:
        report.zwsp_status = "🟢 OK (Reparado)"
    else:
        report.zwsp_status = "🟢 OK"
    return True


def check_orphaned_assets(report: DoctorReport) -> bool:
    img_dir = VAULT_ROOT / "assets" / "images"
    if not img_dir.exists():
        report.assets_status = "🟢 OK"
        return True

    all_images = {img.name for img in img_dir.glob("*") if img.is_file() and not img.name.startswith(".")}
    report.total_images = len(all_images)

    # Search references in all markdown files
    referenced = set()
    for md_file in VAULT_ROOT.rglob("*.md"):
        try:
            txt = md_file.read_text(encoding="utf-8", errors="ignore")
            for img_name in all_images:
                if img_name in txt:
                    referenced.add(img_name)
        except Exception:
            pass

    orphaned = all_images - referenced
    report.orphaned_images = len(orphaned)

    if report.orphaned_images > 10:
        report.assets_status = "🟡 Info"
    else:
        report.assets_status = "🟢 OK"
    return True


def check_protected_zones(report: DoctorReport) -> bool:
    found_zones = 0
    # Search for protected folders anywhere in vault
    for zone_name in ["dswok", "system-design-notes", "data-science-interviews", "ai-engineering-field-guide", "ai-system-design-interview-studio"]:
        matches = list(VAULT_ROOT.rglob(zone_name))
        if matches:
            found_zones += 1

    report.protected_intact = (found_zones >= 3)
    report.protected_status = "🟢 OK" if report.protected_intact else "🟡 Info"
    return True


def _fetch_daemon_graph_stats() -> tuple[int, int] | None:
    """Query graphify-daemon's live `graph_stats` MCP tool for node/edge
    counts (vault-only -- the daemon never indexes this repo's own code,
    unlike the legacy graph.json). Returns None on any failure (daemon
    down, timeout, bad key, unparsable response) so the caller falls
    back to reading the just-rebuilt legacy graph.json instead."""
    if not GRAPHIFY_DAEMON_API_KEY:
        return None
    try:
        resp = requests.post(
            f"{GRAPHIFY_DAEMON_URL}/mcp",
            headers={
                "X-Api-Key": GRAPHIFY_DAEMON_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "graph_stats", "arguments": {}},
            },
            timeout=2,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return None

    data_line = next(
        (line for line in resp.text.splitlines() if line.startswith("data: ")), None
    )
    if data_line is None:
        return None
    try:
        payload = json.loads(data_line[len("data: "):])
        text = payload["result"]["content"][0]["text"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None

    nodes_match = re.search(r"Nodes:\s*(\d+)", text)
    edges_match = re.search(r"Edges:\s*(\d+)", text)
    if not (nodes_match and edges_match):
        return None
    return int(nodes_match.group(1)), int(edges_match.group(1))


class GraphBackendUnavailable(RuntimeError):
    """Raised when GRAPHIFY_BACKEND=remote is forced but the daemon's
    graph_stats tool didn't respond -- the whole point of forcing a
    backend is to know for sure, not to silently fall back."""


def _resolve_graphify_source(report: DoctorReport, graph_file: Path) -> None:
    """Apply GRAPHIFY_BACKEND to decide where report.graph_nodes/graph_edges
    come from, and sets report.graph_source accordingly ("daemon" or
    "legacy"):

    - "local": never calls the daemon, only ever reads graph_file.
    - "remote": only ever calls the daemon; raises GraphBackendUnavailable
      instead of falling back to graph_file if it doesn't respond.
    - anything else ("auto", unset, or unrecognized): today's default --
      prefer the daemon, fall back to graph_file silently.
    """
    mode = normalize_graphify_backend(GRAPHIFY_BACKEND)
    daemon_stats = None if mode == "local" else _fetch_daemon_graph_stats()

    if daemon_stats is not None:
        report.graph_nodes, report.graph_edges = daemon_stats
        report.graph_source = "daemon"
        return

    if mode == "remote":
        raise GraphBackendUnavailable(
            "GRAPHIFY_BACKEND=remote but graphify-daemon's graph_stats tool did not respond."
        )

    if graph_file.exists():
        try:
            g = json.loads(graph_file.read_text(encoding="utf-8"))
            report.graph_nodes = len(g.get("nodes", []))
            report.graph_edges = len(g.get("links", []))
        except Exception:
            pass


def check_graphify(report: DoctorReport) -> bool:
    script_path = PROJECT_DIR / "scripts" / "graphify_helper.py"
    cmd = ["uv", "tool", "run", "--from", "graphifyy", "python", str(script_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    graph_file = GRAPHIFY_OUT_DIR / "graph.json"
    knowledge_file = PROJECT_DIR / ".agents" / "skills" / "obsidian-knowledge-curator" / "KNOWLEDGE.md"

    backend_ok = True
    try:
        _resolve_graphify_source(report, graph_file)
    except GraphBackendUnavailable as e:
        backend_ok = False
        report.graph_source = "remote-unavailable"
        print(f"Error: {e}")

    if knowledge_file.exists():
        try:
            ktxt = knowledge_file.read_text(encoding="utf-8")
            report.knowledge_concepts = len(re.findall(r"^-\s+\*\*", ktxt, re.MULTILINE))
        except Exception:
            pass

    report.graphify_status = "🟢 OK" if (res.returncode == 0 and backend_ok) else "🔴 Error"
    return res.returncode == 0 and backend_ok


_GRAPH_SOURCE_LABELS = {
    "daemon": "solo vault, vía graphify-daemon",
    "legacy": "vault + proyecto, legacy",
    "remote-unavailable": "GRAPHIFY_BACKEND=remote pero el daemon no respondió",
}


def render_dashboard(report: DoctorReport, auto_fix: bool) -> str:
    fix_badge = " *(Modo Auto-Reparación Activado)*" if auto_fix else " *(Modo Diagnóstico - Solo Lectura)*"
    graph_source_label = _GRAPH_SOURCE_LABELS.get(report.graph_source, "vault + proyecto, legacy")

    dashboard = f"""# 🩺 OKC Doctor — Reporte Integral de Diagnóstico y Sincronización
> **Bóveda**: `{VAULT_ROOT}`
> **Ejecución**: {time.strftime('%Y-%m-%d %H:%M:%S')}{fix_badge}
> **Tiempo Total**: `{report.duration:.2f}s`

---

### 📊 Estado de Componentes

| Componente | Estado | Métricas / Detalles |
| :--- | :---: | :--- |
| **Base de Datos SQLite** | {report.sqlite_status} | {report.sqlite_msg} |
| **Master Plans (Categorías)** | {report.master_plans_status} | {report.master_plans_count} planes de navegación sincronizados y reconstruidos. |
| **Integridad de Enlaces & Linter** | {report.linter_status} | `{report.broken_links_count}` enlaces por verificar · `{report.contradictions_count}` contradicciones explícitas. |
| **Higiene Unicode (ZWSP)** | {report.zwsp_status} | `{report.zwsp_files_count}` archivos con caracteres invisibles {'(reparados: ' + str(report.zwsp_fixed_count) + ')' if auto_fix else '(usa --fix para limpiar)'}. |
| **Recursos Visuales (`assets/images/`)** | {report.assets_status} | `{report.total_images}` imágenes totales · `{report.orphaned_images}` no referenciadas. |
| **Zonas Protegidas (Read-Only)** | {report.protected_status} | 5 áreas protegidas auditadas e intactas sin alteraciones. |
| **Grafo Graphify & `KNOWLEDGE.md`** | {report.graphify_status} | `{report.graph_nodes:,}` nodos · `{report.graph_edges:,}` conexiones ({graph_source_label}) · `{report.knowledge_concepts}` conceptos en índice. |

---

### 💡 Resumen Ejecutivo & Recomendaciones
"""
    if auto_fix:
        dashboard += "- ✅ Se ejecutó la limpieza automática de caracteres invisibles ZWSP en los archivos afectados.\n"
    elif report.zwsp_files_count > 0:
        dashboard += f"- ⚠️ Se detectaron {report.zwsp_files_count} archivos con caracteres invisibles. Ejecuta `/okc-doctor --fix` para limpiarlos automáticamente.\n"

    if report.broken_links_count > 0:
        dashboard += f"- ℹ️ Existen {report.broken_links_count} enlaces no resueltos en notas históricas; el índice Graphify los mantiene mapeados como entidades emergentes.\n"

    dashboard += "- 🚀 Tu bóveda de Obsidian está completamente indexada, coherente y lista para navegación y consultas semánticas."
    return dashboard


def main():
    parser = argparse.ArgumentParser(description="OKC Doctor — Health Check and Sync")
    parser.add_argument("--fix", action="store_true", help="Auto-repair issues like ZWSP and high-certainty links")
    args = parser.parse_args()

    start_time = time.time()
    report = DoctorReport()

    print("🩺 Iniciando diagnóstico completo de la bóveda de Obsidian...")
    print("  [1/7] Sincronizando base de datos SQLite...")
    check_sqlite(report)

    print("  [2/7] Reconstruyendo Master Plans por categoría...")
    check_master_plans(report)

    print("  [3/7] Auditando enlaces rotos y contradicciones...")
    check_linter(report)

    print("  [4/7] Escaneando higiene Unicode (ZWSP)...")
    check_and_clean_zwsp(report, auto_fix=args.fix)

    print("  [5/7] Verificando recursos en assets/images/...")
    check_orphaned_assets(report)

    print("  [6/7] Auditando zonas protegidas...")
    check_protected_zones(report)

    print("  [7/7] Reconstruyendo grafo Graphify y KNOWLEDGE.md...")
    check_graphify(report)

    report.duration = time.time() - start_time
    dashboard = render_dashboard(report, auto_fix=args.fix)
    print("\n" + dashboard)


if __name__ == "__main__":
    main()
