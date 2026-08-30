#!/usr/bin/env python3
"""Full-text search over SAC knowledge concepts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import (  # noqa: E402
    find_rg,
    iter_concepts,
    parse_frontmatter,
    resolve_knowledge_root,
    rg_list_files,
)


def search(bundle: Path, query: str, *, limit: int = 20, use_rg: bool | None = None) -> dict:
    terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t]
    results = []
    files = iter_concepts(bundle)
    engine = "scan"
    if use_rg is not False:
        hits = rg_list_files(bundle, terms, ignore_case=True)
        if hits is not None:
            engine = "rg"
            allowed = {p.resolve() for p in hits}
            files = [p for p in files if p.resolve() in allowed]
        elif use_rg is True and not find_rg():
            engine = "scan"
    for p in files:
        text = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        hay = (text).lower()
        score = 0
        for t in terms:
            if t in (fm.get("title") or "").lower():
                score += 10
            if t in (fm.get("type") or "").lower():
                score += 5
            score += hay.count(t)
        if score <= 0:
            continue
        # snippet
        idx = hay.find(terms[0]) if terms else -1
        snip = body.strip().replace("\n", " ")
        if idx >= 0:
            start = max(0, idx - 40)
            snip = text[start : start + 160].replace("\n", " ")
        results.append({
            "path": str(p.relative_to(bundle)),
            "title": fm.get("title") or p.stem,
            "type": fm.get("type"),
            "score": score,
            "snippet": snip[:200],
        })
    results.sort(key=lambda r: -r["score"])
    results = results[:limit]
    return {"query": query, "count": len(results), "engine": engine, "results": results}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Search SAC knowledge")
    p.add_argument("query")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.add_argument("--rg", action="store_true")
    p.add_argument("--no-rg", action="store_true")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    if args.rg and args.no_rg:
        print("error: --rg and --no-rg are mutually exclusive", file=sys.stderr)
        return 2
    use_rg: bool | None
    if args.no_rg:
        use_rg = False
    elif args.rg:
        use_rg = True
    else:
        use_rg = None
    result = search(bundle, args.query, limit=args.limit, use_rg=use_rg)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['count']} hit(s) for {args.query!r}")
        for r in result["results"]:
            print(f"  [{r['score']:3}] {r['type']:20} {r['title']}")
            print(f"         {r['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
