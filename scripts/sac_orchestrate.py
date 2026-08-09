#!/usr/bin/env python3
"""Top-level reverse-engineering orchestrator.

Point at one or more git repo roots (or a monorepo) and produce a full SAC knowledge bundle.
Agent hosts invoke this as the deterministic backbone of the architecture-orchestrator agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import ensure_bundle, resolve_knowledge_root, append_log  # noqa: E402
from sac_materialize import materialize_repos  # noqa: E402
from sac_graph import load_graph  # noqa: E402
from sac_validate import validate_bundle  # noqa: E402


PHASES = [
    "init-bundle",
    "scan-packages",
    "scan-containers",
    "scan-iac",
    "scan-k8s",
    "scan-cicd",
    "scan-identity",
    "capture",
    "graph",
    "validate",
]


def orchestrate(
    host_repo: Path,
    scan_roots: list[Path],
    *,
    system_name: str,
    bundle_name: str | None,
    wiki: Path | None = None,
    tickets: Path | None = None,
) -> dict:
    bundle = resolve_knowledge_root(host_repo, bundle_name)
    ensure_bundle(bundle, system_name)
    phases_done = ["init-bundle"]
    mat = materialize_repos(bundle, scan_roots, system_name)
    phases_done.extend(["scan-*", "capture"])
    if wiki and wiki.exists():
        from sac_ingest_wiki import ingest_dir
        mat["wiki"] = ingest_dir(bundle, wiki)
        phases_done.append("ingest-wiki")
    if tickets and tickets.exists():
        from sac_ingest_tickets import ingest_tickets
        mat["tickets"] = ingest_tickets(bundle, json.loads(tickets.read_text(encoding="utf-8")))
        phases_done.append("ingest-tickets")
    graph = load_graph(bundle)
    phases_done.append("graph")
    validation = validate_bundle(bundle)
    phases_done.append("validate")
    append_log(bundle, f"Orchestrate complete: nodes={graph['node_count']} edges={graph['edge_count']}")
    return {
        "bundle": str(bundle),
        "system": system_name,
        "phases": phases_done,
        "materialize": mat,
        "graph": {"node_count": graph["node_count"], "edge_count": graph["edge_count"]},
        "validation": {
            "ok": validation["ok"],
            "errors": validation["errors"],
            "warnings": validation["warnings"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC reverse-engineering orchestrator")
    p.add_argument("--repo", default=".", help="Knowledge host repo")
    p.add_argument("--bundle", default=None)
    p.add_argument("--system", default="System")
    p.add_argument("--scan-root", action="append", default=[], help="Repo root(s) to reverse-engineer")
    p.add_argument("--wiki", default=None, help="Wiki markdown export path")
    p.add_argument("--tickets", default=None, help="Tickets JSON export path")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    host = Path(args.repo).resolve()
    roots = [Path(r).resolve() for r in (args.scan_root or [str(host)])]
    result = orchestrate(
        host,
        roots,
        system_name=args.system,
        bundle_name=args.bundle,
        wiki=Path(args.wiki) if args.wiki else None,
        tickets=Path(args.tickets) if args.tickets else None,
    )
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"System Architecture Capture complete")
        print(f"  bundle:  {result['bundle']}")
        print(f"  system:  {result['system']}")
        print(f"  graph:   {result['graph']}")
        print(f"  valid:   {result['validation']}")
        print(f"  phases:  {', '.join(result['phases'])}")
    return 0 if result["validation"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
