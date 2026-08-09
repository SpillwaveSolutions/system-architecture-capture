#!/usr/bin/env python3
"""Build dependency / dataflow graph from SAC knowledge bundle."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import iter_concepts, parse_frontmatter, resolve_knowledge_root  # noqa: E402


def load_graph(bundle: Path) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    by_path: dict[str, dict[str, Any]] = {}
    for p in iter_concepts(bundle):
        rel = "/" + str(p.relative_to(bundle)).replace("\\", "/")
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        node = {
            "id": rel,
            "path": rel,
            "type": fm.get("type") or "Concept",
            "title": fm.get("title") or p.stem,
            "tags": fm.get("tags") or [],
            "status": fm.get("status"),
        }
        nodes.append(node)
        by_path[rel] = node
        for link in fm.get("links") or []:
            if not isinstance(link, dict):
                continue
            tgt = link.get("target")
            rel_type = link.get("rel") or "related_to"
            if not tgt:
                continue
            if not str(tgt).startswith("/"):
                tgt = "/" + str(tgt)
            edges.append({"from": rel, "to": tgt, "rel": rel_type})
    return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


def adjacency(graph: dict[str, Any], *, directed: bool = True) -> dict[str, list[tuple[str, str]]]:
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for e in graph["edges"]:
        adj[e["from"]].append((e["to"], e["rel"]))
        if not directed:
            adj[e["to"]].append((e["from"], e["rel"]))
    return adj


def mermaid(graph: dict[str, Any], *, max_nodes: int = 40) -> str:
    nodes = graph["nodes"][:max_nodes]
    ids = {n["id"] for n in nodes}
    lines = ["flowchart LR"]
    def nid(path: str) -> str:
        return "n" + str(abs(hash(path)) % 10_000_000)
    for n in nodes:
        label = (n["title"] or n["id"])[:40].replace('"', "'")
        t = n["type"]
        shape_l, shape_r = "[", "]"
        if t in ("Service", "System"):
            shape_l, shape_r = "([", "])"
        elif t in ("Database", "Cache", "ObjectStorage", "SearchIndex", "DataWarehouse", "DataLake", "VectorStore", "DataStore", "MessageQueue", "Event", "EventStream", "Topic"):
            shape_l, shape_r = "[(", ")]"
        elif t in ("InfrastructureStack", "Pipeline"):
            shape_l, shape_r = "{{", "}}"
        lines.append(f'  {nid(n["id"])}{shape_l}"{label}"{shape_r}')
    for e in graph["edges"]:
        if e["from"] in ids and e["to"] in ids:
            lines.append(f'  {nid(e["from"])} -->|{e["rel"]}| {nid(e["to"])}')
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC graph tools")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--mermaid", action="store_true")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    g = load_graph(bundle)
    if args.mermaid:
        print(mermaid(g))
        return 0
    if args.json:
        print(json.dumps(g, indent=2))
    else:
        print(f"nodes={g['node_count']} edges={g['edge_count']}")
        for e in g["edges"][:30]:
            print(f"  {e['from']} -[{e['rel']}]-> {e['to']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
