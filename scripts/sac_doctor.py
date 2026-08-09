#!/usr/bin/env python3
"""One-screen health check for SAC knowledge bundles."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import iter_concepts, parse_frontmatter, resolve_knowledge_root  # noqa: E402
from sac_validate import validate_bundle  # noqa: E402


def doctor(bundle: Path) -> dict:
    v = validate_bundle(bundle)
    types: Counter[str] = Counter()
    thin = []
    for p in iter_concepts(bundle):
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        t = fm.get("type") or "?"
        types[t] += 1
        links = fm.get("links") or []
        if len(body.strip()) < 40 or not links:
            thin.append({"path": str(p.relative_to(bundle)), "type": t, "title": fm.get("title"), "chars": len(body), "links": len(links) if isinstance(links, list) else 0})
    return {
        "bundle": str(bundle),
        "node_count": v["node_count"],
        "edge_count": v["edge_count"],
        "errors": v["errors"],
        "warnings": v["warnings"],
        "types": dict(types.most_common()),
        "thin_concepts": thin[:30],
        "issues": v["issues"][:50],
        "ok": v["ok"] and v["node_count"] > 0,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC doctor")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    result = doctor(bundle)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"SAC Doctor — {bundle}")
        print(f"  nodes={result['node_count']} edges={result['edge_count']} errors={result['errors']} warnings={result['warnings']}")
        print("  types:", ", ".join(f"{k}:{v}" for k, v in list(result["types"].items())[:12]))
        if result["thin_concepts"]:
            print(f"  thin concepts: {len(result['thin_concepts'])}")
        for i in result["issues"][:15]:
            print(f"  [{i['severity']}] {i['message']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
