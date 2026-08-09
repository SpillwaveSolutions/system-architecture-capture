#!/usr/bin/env python3
"""Progressive disclosure context packs from SAC graph."""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import concept_ref, parse_frontmatter, resolve_knowledge_root  # noqa: E402
from sac_graph import load_graph, adjacency, mermaid  # noqa: E402


def pack(bundle: Path, start: str, *, hops: int = 2, max_nodes: int = 20, tiny: bool = False) -> dict:
    if tiny:
        hops = 1
        max_nodes = 8
    start = concept_ref(start, "services")
    g = load_graph(bundle)
    adj = adjacency(g, directed=False)
    titles = {n["id"]: n for n in g["nodes"]}
    if start not in titles:
        # try fuzzy
        for nid in titles:
            if start.rstrip(".md") in nid or Path(start).stem in nid:
                start = nid
                break
    ordered = [start]
    seen = {start}
    q = deque([(start, 0)])
    while q and len(ordered) < max_nodes:
        cur, d = q.popleft()
        if d >= hops:
            continue
        for nxt, rel in adj.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                ordered.append(nxt)
                q.append((nxt, d + 1))
            if len(ordered) >= max_nodes:
                break
    concepts = []
    for path in ordered:
        fp = bundle / path.lstrip("/")
        if not fp.is_file():
            concepts.append({"path": path, "missing": True})
            continue
        fm, body = parse_frontmatter(fp.read_text(encoding="utf-8"))
        concepts.append({
            "path": path,
            "type": fm.get("type"),
            "title": fm.get("title"),
            "description": fm.get("description"),
            "tags": fm.get("tags") or [],
            "links": fm.get("links") or [],
            "body_preview": body.strip()[:500],
        })
    sub = {
        "nodes": [titles[p] for p in ordered if p in titles],
        "edges": [e for e in g["edges"] if e["from"] in seen and e["to"] in seen],
    }
    return {
        "start": start,
        "hops": hops,
        "node_count": len(concepts),
        "concepts": concepts,
        "mermaid": mermaid(sub, max_nodes=max_nodes),
    }


def render_markdown(pack_data: dict) -> str:
    lines = [f"# Context pack: {pack_data['start']}", "", f"Hops: {pack_data['hops']} · nodes: {pack_data['node_count']}", ""]
    for c in pack_data["concepts"]:
        if c.get("missing"):
            lines.append(f"## {c['path']} (missing)")
            continue
        lines.append(f"## {c.get('title')} (`{c.get('type')}`)")
        lines.append("")
        lines.append(f"Path: `{c['path']}`")
        if c.get("description"):
            lines.append("")
            lines.append(c["description"])
        lines.append("")
        lines.append(c.get("body_preview") or "")
        lines.append("")
    lines.append("## Graph")
    lines.append("")
    lines.append("```mermaid")
    lines.append(pack_data["mermaid"].rstrip())
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC context pack")
    p.add_argument("concept")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--hops", type=int, default=2)
    p.add_argument("--tiny", action="store_true")
    p.add_argument("--mermaid", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    data = pack(bundle, args.concept, hops=args.hops, tiny=args.tiny)
    if args.mermaid:
        print(data["mermaid"])
        return 0
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
