#!/usr/bin/env python3
"""Ingest tickets from JSON export (Jira/Linear/Azure DevOps/GitHub Issues shape)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

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


def _adf_to_text(node: Any) -> str:
    """Flatten Atlassian Document Format to plain text.

    Jira's REST v3 returns descriptions as a document tree, not a string. Passing
    the dict through `str()` yields a Python repr of nested dicts, which is worse
    than empty. Only the text-bearing nodes matter here.
    """
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text") or ""
    if node.get("type") in ("hardBreak", "paragraph", "heading", "listItem"):
        return _adf_to_text(node.get("content")) + "\n"
    return _adf_to_text(node.get("content"))


def _name_of(value: Any) -> str | None:
    """Jira wraps status/type/priority as {"name": ...}; other trackers use a
    bare string. Accept both rather than assuming one."""
    if isinstance(value, dict):
        return value.get("name") or value.get("value") or None
    return value or None


def normalize_ticket(item: dict) -> dict:
    """Accept heterogeneous ticket JSON shapes, including raw Jira REST.

    Jira's search API nests almost everything under `fields{}`:

        {"key": "ABC-1", "fields": {"summary": ..., "status": {"name": ...}}}

    Only `key` sits where a flat reader expects it, so previously every Jira
    ticket fell through to `str(key)` for its title and lost description,
    status, labels and type entirely — while the ingest reported success.
    """
    # `key` and `id` stay at the top level in Jira; everything else moves.
    fields = item.get("fields") if isinstance(item.get("fields"), dict) else {}
    src = {**fields, **{k: v for k, v in item.items() if k != "fields"}}
    # Values that live ONLY under fields must not be shadowed by a top-level
    # absence, so read from fields first and fall back to the merged view.
    def pick(*names: str) -> Any:
        for n in names:
            if fields.get(n) not in (None, "", []):
                return fields[n]
        for n in names:
            if src.get(n) not in (None, "", []):
                return src[n]
        return None

    key = pick("key", "id", "number", "identifier")
    title = pick("title", "summary", "name") or str(key)
    body = pick("body", "description", "content") or ""
    if not isinstance(body, str):
        body = _adf_to_text(body)
    # Previously this read `item.get("state")` whenever `state` was not a dict,
    # which discarded a perfectly good flat `"status": "Done"`.
    status = _name_of(pick("status", "state")) or "unknown"
    labels = pick("labels", "tags") or []
    if labels and isinstance(labels[0], dict):
        labels = [l.get("name") for l in labels if l.get("name")]
    ttype = _name_of(pick("type", "issue_type", "issuetype")) or "story"
    return {
        "key": str(key),
        "title": str(title),
        "body": str(body)[:8000],
        "status": str(status),
        "labels": labels,
        "type": str(ttype).lower(),
        "url": pick("url", "html_url", "webUrl", "self"),
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
