#!/usr/bin/env python3
"""Materialize multi-repo scan results and optional ticket/wiki digests into SAC."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import ensure_bundle, resolve_knowledge_root  # noqa: E402
from sac_capture import capture_scan  # noqa: E402
from sac_scan import full_scan  # noqa: E402


def materialize_repos(bundle: Path, repos: list[Path], system_name: str) -> dict:
    ensure_bundle(bundle, system_name)
    total = {"created": 0, "updated": 0, "skipped": 0, "refused": 0, "repos": []}
    for repo in repos:
        scan = full_scan(repo)
        stats = capture_scan(bundle, scan, system_name=system_name)
        total["repos"].append({"root": str(repo), "summary": scan.get("summary"), "stats": stats})
        for k in ("created", "updated", "skipped", "refused"):
            total[k] += stats.get(k, 0)
    return total


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Materialize architecture knowledge from repos")
    p.add_argument("--repo", default=".", help="Knowledge host repo")
    p.add_argument("--bundle", default=None)
    p.add_argument("--system", default="System")
    p.add_argument("--scan-root", action="append", default=[], help="Code root(s) to scan (repeatable)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    host = Path(args.repo).resolve()
    bundle = resolve_knowledge_root(host, args.bundle)
    roots = [Path(r).resolve() for r in (args.scan_root or [str(host)])]
    result = materialize_repos(bundle, roots, args.system)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Materialized into {bundle}")
        print(
            f"created={result['created']} updated={result['updated']} "
            f"skipped={result['skipped']} refused={result['refused']}"
        )
        for r in result["repos"]:
            print(f"  {r['root']}: {r['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
