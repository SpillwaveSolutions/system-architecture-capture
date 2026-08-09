#!/usr/bin/env python3
"""Unified architecture scan — packages, containers, IaC, K8s, CI/CD, identity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_scan_packages import scan_packages  # noqa: E402
from sac_scan_containers import scan_containers  # noqa: E402
from sac_scan_iac import scan_iac  # noqa: E402
from sac_scan_k8s import scan_k8s  # noqa: E402
from sac_scan_cicd import scan_cicd  # noqa: E402
from sac_scan_identity import scan_identity  # noqa: E402


def full_scan(root: Path, *, domains: list[str] | None = None) -> dict:
    want = set(domains or ["packages", "containers", "iac", "k8s", "cicd", "identity"])
    result: dict = {"root": str(root), "domains": sorted(want)}
    if "packages" in want:
        result["packages"] = scan_packages(root)
    if "containers" in want:
        result["containers"] = scan_containers(root)
    if "iac" in want:
        result["iac"] = scan_iac(root)
    if "k8s" in want:
        result["k8s"] = scan_k8s(root)
    if "cicd" in want:
        result["cicd"] = scan_cicd(root)
    if "identity" in want:
        result["identity"] = scan_identity(root)
    # summary counts
    summary = {}
    for k, v in result.items():
        if k in ("root", "domains"):
            continue
        if isinstance(v, list):
            summary[k] = len(v)
        elif isinstance(v, dict) and "count" in v:
            summary[k] = v["count"]
        elif isinstance(v, dict):
            summary[k] = {sk: (len(sv) if isinstance(sv, list) else sv) for sk, sv in v.items() if sk != "count"}
    result["summary"] = summary
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Full architecture scan")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--domains",
        default="packages,containers,iac,k8s,cicd,identity",
        help="Comma-separated domain list",
    )
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    data = full_scan(root, domains=domains)
    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"Scan root: {root}")
        for k, v in data.get("summary", {}).items():
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
