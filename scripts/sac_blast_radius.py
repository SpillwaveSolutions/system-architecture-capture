#!/usr/bin/env python3
"""Blast-radius analysis from a concept through typed edges."""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import concept_ref, resolve_knowledge_root, write_knowledge, path_for_type, slugify, append_log  # noqa: E402
from sac_graph import load_graph, adjacency  # noqa: E402


def blast_radius(graph: dict, start: str, *, hops: int = 3) -> dict:
    if not start.startswith("/"):
        start = "/" + start
    adj = adjacency(graph, directed=False)
    titles = {n["id"]: n for n in graph["nodes"]}
    visited = {start: 0}
    impact: list[dict] = []
    q = deque([start])
    while q:
        cur = q.popleft()
        d = visited[cur]
        if d >= hops:
            continue
        for nxt, rel in adj.get(cur, []):
            if nxt not in visited:
                visited[nxt] = d + 1
                node = titles.get(nxt, {"id": nxt, "title": nxt, "type": "?"})
                impact.append({
                    "path": nxt,
                    "title": node.get("title"),
                    "type": node.get("type"),
                    "hop": d + 1,
                    "via": rel,
                    "from": cur,
                })
                q.append(nxt)
    impact.sort(key=lambda x: (x["hop"], x["type"] or "", x["title"] or ""))
    return {
        "start": start,
        "hops": hops,
        "impacted_count": len(impact),
        "impacted": impact,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Blast radius analysis")
    p.add_argument("concept", help="Concept path or title")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--hops", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write BlastRadius concept")
    p.add_argument("--author", default="")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    start = concept_ref(args.concept, "services")
    g = load_graph(bundle)
    result = blast_radius(g, start, hops=args.hops)
    if args.write:
        from sac_common import resolve_author
        author = resolve_author(args.author)
        slug = slugify(f"blast-{Path(start).stem}")
        body = f"# Blast radius: {start}\n\nHops: {args.hops}\n\n## Impacted\n\n"
        body += "\n".join(
            f"- hop {i['hop']}: [{i['title']}]({i['path']}) ({i['type']}) via `{i['via']}`"
            for i in result["impacted"]
        ) + "\n"
        write_knowledge(
            bundle,
            path_for_type("BlastRadius", slug),
            {
                "type": "BlastRadius",
                "title": f"Blast radius of {Path(start).stem}",
                "description": f"{result['impacted_count']} concepts within {args.hops} hops",
                "tags": ["sac", "blast-radius"],
                "truth_state": "current",
                "verified": False,
                "source": "sac-blast-radius",
                "links": [{"target": start, "rel": "impacts"}],
            },
            body,
            author=author,
        )
        append_log(bundle, f"Blast radius for {start}: {result['impacted_count']} nodes")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Start: {start}  hops={args.hops}  impacted={result['impacted_count']}")
        for i in result["impacted"]:
            print(f"  h{i['hop']} {i['type']:20} {i['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
