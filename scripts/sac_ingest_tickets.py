#!/usr/bin/env python3
"""Ingest tickets from JSON export (Jira/Linear/Azure DevOps/GitHub Issues shape)."""

from __future__ import annotations

import argparse
import json
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


def normalize_ticket(item: dict) -> dict:
    """Accept heterogeneous ticket JSON shapes."""
    key = item.get("key") or item.get("id") or item.get("number") or item.get("identifier")
    title = item.get("title") or item.get("summary") or item.get("name") or str(key)
    body = item.get("body") or item.get("description") or item.get("content") or ""
    status = item.get("status") or (item.get("state") or {}).get("name") if isinstance(item.get("state"), dict) else item.get("state")
    labels = item.get("labels") or item.get("tags") or []
    if labels and isinstance(labels[0], dict):
        labels = [l.get("name") for l in labels if l.get("name")]
    ttype = item.get("type") or item.get("issue_type") or item.get("issuetype") or "story"
    if isinstance(ttype, dict):
        ttype = ttype.get("name") or "story"
    return {
        "key": str(key),
        "title": str(title),
        "body": str(body)[:8000],
        "status": str(status or "unknown"),
        "labels": labels,
        "type": str(ttype).lower(),
        "url": item.get("url") or item.get("html_url") or item.get("webUrl"),
    }


def ingest_tickets(bundle: Path, data: list | dict) -> dict:
    items = data if isinstance(data, list) else data.get("issues") or data.get("tickets") or data.get("items") or []
    stats = {"created": 0, "updated": 0, "skipped": 0}
    for raw in items:
        if not isinstance(raw, dict):
            continue
        t = normalize_ticket(raw)
        clean, _ = scrub_text(t["body"])
        slug = slugify(f"ticket-{t['key']}")
        rel = path_for_type("TicketLink", slug)
        body = (
            f"# {t['key']}: {t['title']}\n\n"
            f"**Status:** {t['status']}  \n"
            f"**Type:** {t['type']}  \n"
            + (f"**URL:** {t['url']}\n" if t.get("url") else "")
            + f"\n## Description\n\n{clean or '_No description._'}\n"
        )
        ctype = "Feature" if t["type"] in ("epic", "feature", "story") and "epic" in t["type"] else "TicketLink"
        if t["type"] == "epic":
            rel = path_for_type("Feature", slug)
            fm_type = "Feature"
        else:
            fm_type = "TicketLink"
            rel = path_for_type("TicketLink", slug)
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": fm_type,
                "title": f"{t['key']}: {t['title']}",
                "description": t["title"],
                "tags": ["sac", "ticket", t["type"]] + list(t["labels"] or [])[:8],
                "status": t["status"],
                "truth_state": "current",
                "verified": False,
                "source": "ticket-ingest",
                "external_key": t["key"],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1
    refresh_catalog_index(bundle, "tickets")
    refresh_catalog_index(bundle, "features")
    append_log(bundle, f"Ticket ingest: {stats}")
    return stats


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Ingest tickets JSON into SAC")
    p.add_argument("source", help="JSON file of tickets/issues")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    ensure_bundle(bundle)
    data = json.loads(Path(args.source).read_text(encoding="utf-8"))
    print(ingest_tickets(bundle, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
