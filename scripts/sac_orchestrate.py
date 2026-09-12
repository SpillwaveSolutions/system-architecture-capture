#!/usr/bin/env python3
"""Top-level reverse-engineering orchestrator.

Point at one or more git repo roots (or a monorepo) and produce a full SAC knowledge bundle.
Agent hosts invoke this as the deterministic backbone of the architecture-orchestrator agent.

Workflow: init-bundle → breadth-first plan → (optional pause) → domain-scoped
scan/capture → graph → validate. Wiki/ticket paths are optional exports produced
by host skills/MCPs — SAC does not connect to Confluence/Jira/etc. itself.

Query-time retrieve (architecture-retriever / sac-retrieve) is a different path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import ensure_bundle, resolve_knowledge_root, append_log  # noqa: E402
from sac_materialize import materialize_repos  # noqa: E402
from sac_graph import load_graph  # noqa: E402
from sac_validate import validate_bundle  # noqa: E402
from sac_plan import (  # noqa: E402
    load_plan,
    mark_area_item_if_present,
    plan_paths,
    scan_domains_from_plan,
    write_plan,
    checklist_summary,
)


PHASES = [
    "init-bundle",
    "plan",
    "scan-packages",
    "scan-containers",
    "scan-iac",
    "scan-k8s",
    "scan-cicd",
    "scan-identity",
    "capture",
    "graph",
    "validate",
]


def _public_plan(plan: dict) -> dict:
    return {
        "system": plan.get("system"),
        "system_slug": plan.get("system_slug"),
        "roots": plan.get("roots"),
        "ecosystems": plan.get("ecosystems"),
        "focus_areas": [
            {
                "id": a.get("id"),
                "rank": a.get("rank"),
                "title": a.get("title"),
                "signal": a.get("signal"),
                "hit_count": a.get("hit_count"),
                "agent": a.get("agent"),
                "scan_domains": a.get("scan_domains"),
                "checklist": a.get("checklist"),
            }
            for a in (plan.get("focus_areas") or [])
        ],
        "artifacts": plan.get("artifacts"),
        "written": plan.get("written"),
        "checklist": plan.get("checklist") or checklist_summary(plan),
    }


def _resolve_from_plan(bundle: Path, from_plan: str | Path | None) -> Path:
    if from_plan:
        p = Path(from_plan)
        if not p.is_absolute():
            if p.exists():
                return p.resolve()
            cand = bundle / p
            if cand.exists():
                return cand.resolve()
            return p.resolve()
        return p
    return plan_paths(bundle)["json"]


def orchestrate(
    host_repo: Path,
    scan_roots: list[Path],
    *,
    system_name: str,
    bundle_name: str | None,
    wiki: Path | None = None,
    tickets: Path | None = None,
    author: str,
    plan_only: bool = False,
    from_plan: str | Path | None = None,
    area: str | None = None,
) -> dict:
    bundle = resolve_knowledge_root(host_repo, bundle_name)
    ensure_bundle(bundle, system_name)
    phases_done = ["init-bundle"]

    plan: dict
    if from_plan:
        plan = load_plan(_resolve_from_plan(bundle, from_plan))
        if system_name == "System" and plan.get("system"):
            system_name = plan["system"]
    else:
        plan = write_plan(bundle, scan_roots, system_name=system_name)
    phases_done.append("plan")
    append_log(
        bundle,
        "RE plan: areas="
        + ",".join(a["id"] for a in (plan.get("focus_areas") or []))
        + f" checklist={checklist_summary(plan)}",
    )

    if plan_only:
        validation = validate_bundle(bundle)
        return {
            "bundle": str(bundle),
            "system": system_name,
            "phases": phases_done,
            "plan": _public_plan(plan),
            "materialize": None,
            "graph": {"node_count": 0, "edge_count": 0},
            "validation": {
                "ok": validation["ok"],
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            },
        }

    domains = scan_domains_from_plan(plan, area=area)
    mat = materialize_repos(bundle, scan_roots, system_name, author=author, domains=domains or None)
    phases_done.extend(["scan-*", "capture"])
    if area:
        mark_area_item_if_present(
            bundle, area=area, item="capture", status="done", note="orchestrate --from-plan"
        )
    else:
        for focus in plan.get("focus_areas") or []:
            if "capture" in {i["id"] for i in (focus.get("checklist") or [])}:
                mark_area_item_if_present(
                    bundle,
                    area=focus["id"],
                    item="capture",
                    status="done",
                    note="orchestrate scoped capture",
                )
    if wiki and wiki.exists():
        from sac_ingest_wiki import ingest_dir
        mat["wiki"] = ingest_dir(bundle, wiki, author=author)
        phases_done.append("ingest-wiki")
    if tickets and tickets.exists():
        from sac_ingest_tickets import ingest_tickets
        mat["tickets"] = ingest_tickets(bundle, json.loads(tickets.read_text(encoding="utf-8")), author=author)
        phases_done.append("ingest-tickets")
    graph = load_graph(bundle)
    phases_done.append("graph")
    validation = validate_bundle(bundle)
    phases_done.append("validate")
    try:
        plan = load_plan(bundle)
    except FileNotFoundError:
        pass
    append_log(bundle, f"Orchestrate complete: nodes={graph['node_count']} edges={graph['edge_count']}")
    return {
        "bundle": str(bundle),
        "system": system_name,
        "phases": phases_done,
        "plan": _public_plan(plan),
        "materialize": mat,
        "graph": {"node_count": graph["node_count"], "edge_count": graph["edge_count"]},
        "validation": {
            "ok": validation["ok"],
            "errors": validation["errors"],
            "warnings": validation["warnings"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC reverse-engineering orchestrator")
    p.add_argument("--repo", default=".", help="Knowledge host repo")
    p.add_argument("--bundle", default=None)
    p.add_argument("--system", default="System")
    p.add_argument("--scan-root", action="append", default=[], help="Repo root(s) to reverse-engineer")
    p.add_argument("--wiki", default=None, help="Wiki markdown export path")
    p.add_argument("--tickets", default=None, help="Tickets JSON export path")
    p.add_argument("--plan-only", action="store_true", help="Init + breadth-first plan, then stop")
    p.add_argument(
        "--from-plan",
        default=None,
        help="Existing .sac/re-plan.json (or bundle / .sac dir) — skip remapping",
    )
    p.add_argument(
        "--area",
        default=None,
        help="With --from-plan: run one focus area (domain-scoped scan + capture)",
    )
    p.add_argument("--json", action="store_true")
    p.add_argument("--author", default="")
    args = p.parse_args(argv)
    from sac_common import resolve_author
    author = resolve_author(args.author)
    host = Path(args.repo).resolve()
    roots = [Path(r).resolve() for r in (args.scan_root or [str(host)])]
    result = orchestrate(
        host,
        roots,
        system_name=args.system,
        bundle_name=args.bundle,
        wiki=Path(args.wiki) if args.wiki else None,
        tickets=Path(args.tickets) if args.tickets else None,
        author=author,
        plan_only=args.plan_only,
        from_plan=args.from_plan,
        area=args.area,
    )
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"System Architecture Capture complete")
        print(f"  bundle:  {result['bundle']}")
        print(f"  system:  {result['system']}")
        print(f"  graph:   {result['graph']}")
        print(f"  valid:   {result['validation']}")
        print(f"  phases:  {', '.join(result['phases'])}")
        plan = result.get("plan") or {}
        areas = ", ".join(
            f"{a.get('rank')}:{a.get('id')}({a.get('agent')})" for a in (plan.get("focus_areas") or [])
        )
        if areas:
            print(f"  plan:    {areas}")
        if plan.get("checklist"):
            print(f"  checks:  {plan['checklist']}")
        written = (plan.get("written") or {})
        if written.get("md"):
            print(f"  plan md: {written['md']}")
    return 0 if result["validation"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
