#!/usr/bin/env python3
"""Ingest wiki/Confluence/Notion export markdown into SAC glossary, ADRs, runbooks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import (  # noqa: E402
    append_log,
    ensure_bundle,
    path_for_type,
    refresh_catalog_index,
    resolve_knowledge_root,
    scrub_text,
    slugify,
    write_concept,
)


ADR_HINT = re.compile(r"(?i)\b(adr|architecture decision|decision record)\b")
GLOSSARY_HINT = re.compile(r"(?i)\b(glossary|terminology|definitions)\b")
RUNBOOK_HINT = re.compile(r"(?i)\b(runbook|playbook|on-?call|incident)\b")


def classify(name: str, text: str) -> str:
    if ADR_HINT.search(name) or ADR_HINT.search(text[:500]):
        return "DecisionRecord"
    if GLOSSARY_HINT.search(name) or GLOSSARY_HINT.search(text[:500]):
        return "GlossaryTerm"
    if RUNBOOK_HINT.search(name) or RUNBOOK_HINT.search(text[:500]):
        return "Design"
    return "Discovery"


def ingest_dir(bundle: Path, source: Path) -> dict:
    stats = {"created": 0, "updated": 0, "skipped": 0}
    files = list(source.rglob("*.md")) if source.is_dir() else [source]
    for f in files:
        if f.name.lower() in ("readme.md", "index.md"):
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        clean, _ = scrub_text(raw)
        ctype = classify(f.name, clean)
        title = f.stem.replace("-", " ").replace("_", " ").title()
        # first markdown heading
        m = re.search(r"(?m)^#\s+(.+)$", clean)
        if m:
            title = m.group(1).strip()
        slug = slugify(f"wiki-{f.stem}")
        rel = path_for_type(ctype, slug)
        body = f"# {title}\n\n_Ingested from wiki: `{f.name}`_\n\n{clean.strip()}\n"
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": ctype,
                "title": title,
                "description": f"Ingested wiki page ({ctype})",
                "tags": ["sac", "wiki-ingest", ctype.lower()],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "wiki-ingest",
                "source_path": str(f),
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1
    for cat in ("decisions", "glossary", "designs", "discoveries"):
        refresh_catalog_index(bundle, cat)
    append_log(bundle, f"Wiki ingest: {stats}")
    return stats


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Ingest wiki markdown into SAC")
    p.add_argument("source", help="File or directory of markdown exports")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    ensure_bundle(bundle)
    stats = ingest_dir(bundle, Path(args.source).resolve())
    print(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
