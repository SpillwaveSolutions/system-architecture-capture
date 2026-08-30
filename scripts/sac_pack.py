#!/usr/bin/env python3
"""Progressive disclosure context packs from SAC graph.

Bodies off unless that node is the pack root. Token budget is fail-closed
(default 1/4 of SECOND_BRAIN_WINDOW_TOKENS). Node clip is not a token budget.

Inbound/backlink discovery: ripgrep prefilter → full scan. Outbound is always
parsed from the current file. Ranking/graph identity matches a full scan.
`--no-rg` forces the linear walk. rg is optional and never installed from a hook.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import (  # noqa: E402
    concept_ref,
    find_rg,
    is_concept_path,
    iter_concepts,
    parse_frontmatter,
    resolve_knowledge_root,
    rg_list_files,
)
from sac_graph import iter_link_edges, mermaid  # noqa: E402

DEFAULT_WINDOW_TOKENS = 128_000
PACK_BUDGET_DENOMINATOR = 4


class PackBudgetError(Exception):
    def __init__(self, tokens: int, budget: int, window: int, nodes: list[str]):
        self.tokens = tokens
        self.budget = budget
        self.window = window
        self.nodes = nodes
        super().__init__(f"pack exceeds token budget ({tokens}/{budget})")


def estimate_tokens(text: str) -> int:
    """Cheap chars/4 estimator. Not a model tokenizer."""
    if not text:
        return 0
    return (len(text) + 3) // 4


def resolve_pack_budget(
    max_tokens: str | int | None = None,
    window_tokens: str | int | None = None,
) -> tuple[int, int]:
    raw_window = (
        window_tokens
        if window_tokens not in (None, "")
        else os.environ.get("SECOND_BRAIN_WINDOW_TOKENS") or ""
    )
    window = int(raw_window) if str(raw_window).strip() else DEFAULT_WINDOW_TOKENS
    if window < 1:
        raise SystemExit("error: window tokens must be >= 1")
    raw_budget = (
        max_tokens
        if max_tokens not in (None, "")
        else os.environ.get("SECOND_BRAIN_PACK_MAX_TOKENS") or ""
    )
    budget = int(raw_budget) if str(raw_budget).strip() else max(1, window // PACK_BUDGET_DENOMINATOR)
    if budget < 1:
        raise SystemExit("error: max tokens must be >= 1")
    return window, budget


def _parse_rel(bundle: Path, rel: str) -> tuple[dict, str]:
    fp = bundle / rel.lstrip("/")
    if not fp.is_file():
        return {}, ""
    try:
        return parse_frontmatter(fp.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return {}, ""


def extract_edges(
    bundle: Path,
    path: Path,
    *,
    cache: dict[str, list[tuple[str, str, str]]] | None = None,
) -> list[tuple[str, str, str]]:
    """(rel_type, tgt, label) authored on this file. Cached per pack() call."""
    key = str(path.resolve()) if path.exists() else str(path)
    if cache is not None and key in cache:
        return cache[key]
    try:
        rel = "/" + path.resolve().relative_to(bundle.resolve()).as_posix()
    except ValueError:
        rel = "/" + path.name
    fm, _body = _parse_rel(bundle, rel)
    edges = [(r, tgt, Path(tgt).stem) for _src, tgt, r in iter_link_edges(rel, fm)]
    if cache is not None:
        cache[key] = edges
    return edges


def _inbound_via_rg(
    bundle: Path,
    target: str,
    *,
    cache: dict[str, list[tuple[str, str, str]]] | None = None,
) -> list[tuple[str, str, str]] | None:
    """Files that mention `target`, parsed for real inbound edges. None = fall back."""
    needles = [target]
    if target.startswith("/"):
        needles.append(target.lstrip("/"))
    hits = rg_list_files(bundle, needles[:1], fixed_string=True, ignore_case=False)
    if hits is None:
        return None
    inbound: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for path in hits:
        if not is_concept_path(bundle, path):
            continue
        try:
            src = "/" + path.relative_to(bundle).as_posix()
        except ValueError:
            continue
        if src == target:
            continue
        for rel_type, tgt, label in extract_edges(bundle, path, cache=cache):
            if tgt != target:
                continue
            key = (rel_type, src, label)
            if key in seen:
                continue
            seen.add(key)
            inbound.append((rel_type, src, label))
    return inbound


def build_reverse_index(
    bundle: Path,
    *,
    cache: dict[str, list[tuple[str, str, str]]] | None = None,
) -> dict[str, list[tuple[str, str, str]]]:
    """Map each target path to the edges that point at it.

    pack() used to walk an undirected load_graph, so inbound was free but every
    pack paid a full-bundle parse. Catalog index.md is skipped (iter_concepts)
    so directory listings do not drag the whole folder into the pack.
    """
    index: dict[str, list[tuple[str, str, str]]] = {}
    for path in iter_concepts(bundle):
        src = "/" + path.relative_to(bundle).as_posix()
        for rel_type, tgt, label in extract_edges(bundle, path, cache=cache):
            index.setdefault(tgt, []).append((rel_type, src, label))
    return index


class ReverseIndex:
    """Inbound edges: rg → full scan. No SQLite rung in SAC yet."""

    def __init__(
        self,
        bundle: Path,
        *,
        cache: dict[str, list[tuple[str, str, str]]] | None = None,
        use_rg: bool | None = None,
    ):
        self.bundle = bundle
        self.cache = cache if cache is not None else {}
        self._full: dict[str, list[tuple[str, str, str]]] | None = None
        self._memo: dict[str, list[tuple[str, str, str]]] = {}
        if use_rg is False:
            self._rg = False
        else:
            self._rg = bool(find_rg())

    @property
    def engine(self) -> str:
        return "rg" if self._rg else "scan"

    def get(self, target: str, default: list | None = None) -> list[tuple[str, str, str]]:
        if target in self._memo:
            return self._memo[target]
        if self._rg:
            found = _inbound_via_rg(self.bundle, target, cache=self.cache)
            if found is not None:
                self._memo[target] = found
                return found
            self._rg = False
        if self._full is None:
            self._full = build_reverse_index(self.bundle, cache=self.cache)
        edges = self._full.get(target, default or [])
        self._memo[target] = edges
        return edges


def _resolve_start(bundle: Path, start: str) -> str:
    start = concept_ref(start, "services")
    fp = bundle / start.lstrip("/")
    if fp.is_file():
        return start
    stem = Path(start).stem
    needle = start.rstrip(".md")
    for p in iter_concepts(bundle):
        rel = "/" + p.relative_to(bundle).as_posix()
        if p.stem == stem or needle in rel:
            return rel
    return start


def pack(
    bundle: Path,
    start: str,
    *,
    hops: int = 2,
    max_nodes: int = 20,
    tiny: bool = False,
    use_rg: bool | None = None,
) -> dict:
    if tiny:
        hops = 1
        max_nodes = 8
    start = _resolve_start(bundle, start)
    parse_cache: dict[str, list[tuple[str, str, str]]] = {}
    inbound = ReverseIndex(bundle, cache=parse_cache, use_rg=use_rg)

    ordered = [start]
    seen = {start}
    q = deque([(start, 0)])
    edge_list: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    node_meta: dict[str, dict] = {}

    while q and len(ordered) < max_nodes:
        cur, d = q.popleft()
        fp = bundle / cur.lstrip("/")
        fm, body = _parse_rel(bundle, cur)
        if fp.is_file():
            node_meta[cur] = {
                "id": cur,
                "path": cur,
                "type": fm.get("type") or "Concept",
                "title": fm.get("title") or Path(cur).stem,
                "tags": fm.get("tags") or [],
                "status": fm.get("status"),
                "description": fm.get("description"),
                "links": fm.get("links") or [],
                "body": body,
            }
        if d >= hops or not fp.is_file():
            continue
        neighbours: list[tuple[str, str, str, str]] = [
            (cur, tgt, rel_type, label)
            for rel_type, tgt, label in extract_edges(bundle, fp, cache=parse_cache)
        ]
        neighbours += [
            (src, cur, rel_type, label)
            for rel_type, src, label in inbound.get(cur, [])
        ]
        for src, tgt, rel_type, label in neighbours:
            key = (src, tgt, rel_type)
            if key not in seen_edges:
                seen_edges.add(key)
                edge_list.append({"from": src, "to": tgt, "rel": rel_type, "label": label})
            other = tgt if src == cur else src
            if other not in seen:
                seen.add(other)
                ordered.append(other)
                q.append((other, d + 1))
                if len(ordered) >= max_nodes:
                    break

    concepts = []
    mermaid_nodes = []
    for path in ordered:
        meta = node_meta.get(path)
        fp = bundle / path.lstrip("/")
        if meta is None and not fp.is_file():
            concepts.append({"path": path, "missing": True})
            continue
        if meta is None:
            fm, body = _parse_rel(bundle, path)
            meta = {
                "id": path,
                "path": path,
                "type": fm.get("type") or "Concept",
                "title": fm.get("title") or Path(path).stem,
                "tags": fm.get("tags") or [],
                "status": fm.get("status"),
                "description": fm.get("description"),
                "links": fm.get("links") or [],
                "body": body,
            }
        is_root = path == start
        concepts.append(
            {
                "path": path,
                "type": meta.get("type"),
                "title": meta.get("title"),
                "description": meta.get("description"),
                "tags": meta.get("tags") or [],
                "links": meta.get("links") or [],
                "body": meta.get("body") if is_root else "",
            }
        )
        mermaid_nodes.append(
            {
                "id": path,
                "path": path,
                "type": meta.get("type") or "Concept",
                "title": meta.get("title") or Path(path).stem,
                "tags": meta.get("tags") or [],
                "status": meta.get("status"),
            }
        )

    ids = {n["id"] for n in mermaid_nodes}
    sub = {
        "nodes": mermaid_nodes,
        "edges": [e for e in edge_list if e["from"] in ids and e["to"] in ids],
    }
    return {
        "start": start,
        "hops": hops,
        "max_nodes": max_nodes,
        "node_count": len(concepts),
        "concepts": concepts,
        "mermaid": mermaid(sub, max_nodes=max_nodes),
        "reverse_index": inbound.engine,
        "excluded_note": (
            "Nodes beyond hops/max_nodes omitted for progressive disclosure. "
            "Node clip is not a token budget."
        ),
    }


def render_markdown(
    pack_data: dict,
    *,
    tokens: int | None = None,
    budget: int | None = None,
) -> str:
    start = pack_data["start"]
    token_bit = f"Tokens: {tokens}/{budget} | " if tokens is not None and budget is not None else ""
    lines = [
        f"# Context pack: {start}",
        "",
        f"{token_bit}Hops: {pack_data['hops']} · nodes: {pack_data['node_count']}",
        "",
    ]
    for c in pack_data["concepts"]:
        if c.get("missing"):
            lines.append(f"## {c['path']} (missing)")
            lines.append("")
            continue
        is_root = c["path"] == start
        lines.append(f"## {c.get('title')} (`{c.get('type')}`)")
        lines.append("")
        lines.append(f"Path: `{c['path']}`")
        if is_root:
            body = (c.get("body") or "").strip()
            if body:
                lines.append("")
                lines.append(body)
        elif c.get("description"):
            lines.append("")
            lines.append(str(c["description"]))
        lines.append("")
    lines.append("## Graph")
    lines.append("")
    lines.append("```mermaid")
    lines.append(pack_data["mermaid"].rstrip())
    lines.append("```")
    lines.append("")
    if pack_data.get("excluded_note"):
        lines.append(f"_{pack_data['excluded_note']}_")
        lines.append("")
    return "\n".join(lines)


def finalize_markdown(
    pack_data: dict,
    *,
    max_tokens: str | int | None = None,
    window_tokens: str | int | None = None,
) -> tuple[str, dict[str, int]]:
    """Render the pack and fail closed if it exceeds the token budget.

    Bodies off unless that node is the pack root. Node clip is not a token budget.
    """
    window, budget = resolve_pack_budget(max_tokens, window_tokens)
    draft = render_markdown(pack_data, tokens=0, budget=budget)
    tokens = estimate_tokens(draft)
    md = render_markdown(pack_data, tokens=tokens, budget=budget)
    tokens = estimate_tokens(md)
    meta = {"tokens": tokens, "budget": budget, "window": window}
    if tokens > budget:
        raise PackBudgetError(
            tokens, budget, window, [c.get("path", "") for c in pack_data["concepts"]]
        )
    return md, meta


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC context pack")
    p.add_argument("concept")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--hops", type=int, default=2)
    p.add_argument("--max-nodes", type=int, default=20)
    p.add_argument("--max-tokens", default="")
    p.add_argument("--window-tokens", default="")
    p.add_argument("--tiny", action="store_true")
    p.add_argument("--mermaid", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", default=None, help="Directory or file to write pack markdown")
    p.add_argument(
        "--rg",
        action="store_true",
        help="Use ripgrep to find inbound edges (default when rg is on PATH)",
    )
    p.add_argument(
        "--no-rg",
        action="store_true",
        help="Disable ripgrep; full-scan inbound (same graph, slower)",
    )
    args = p.parse_args(argv)
    if args.rg and args.no_rg:
        print("error: --rg and --no-rg are mutually exclusive", file=sys.stderr)
        return 2
    use_rg: bool | None
    if args.no_rg:
        use_rg = False
    elif args.rg:
        use_rg = True
        if not find_rg():
            print(
                "sac_pack: rg not found; falling back to scan. "
                "Install ripgrep or pass --no-rg.",
                file=sys.stderr,
            )
    else:
        use_rg = None
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    data = pack(
        bundle,
        args.concept,
        hops=args.hops,
        max_nodes=args.max_nodes,
        tiny=args.tiny,
        use_rg=use_rg,
    )
    try:
        if args.mermaid:
            window, budget = resolve_pack_budget(args.max_tokens, args.window_tokens)
            tokens = estimate_tokens(data["mermaid"])
            if tokens > budget:
                raise PackBudgetError(
                    tokens, budget, window, [c.get("path", "") for c in data["concepts"]]
                )
            print(data["mermaid"])
            return 0
        md, meta = finalize_markdown(
            data, max_tokens=args.max_tokens, window_tokens=args.window_tokens
        )
    except PackBudgetError as exc:
        payload = {
            "error": "pack exceeds token budget",
            "tokens": exc.tokens,
            "budget": exc.budget,
            "window": exc.window,
            "nodes": exc.nodes,
            "hint": "narrow --hops / --tiny; node clip is not a token budget",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"error: pack exceeds token budget ({exc.tokens}/{exc.budget})",
                file=sys.stderr,
            )
        return 1

    data.update(meta)

    if args.write:
        out = Path(args.write)
        if out.is_dir() or str(args.write).endswith("/"):
            out.mkdir(parents=True, exist_ok=True)
            slug = Path(str(data["start"])).stem + ("-tiny" if args.tiny else "")
            out = out / f"{slug}-pack.md"
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"Wrote {out}")

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    elif not args.write:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
