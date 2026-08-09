#!/usr/bin/env python3
"""C4 model integration for System Architecture Capture.

Maps SAC concepts ↔ C4 abstractions and generates level views as Mermaid
listings stored in OKF diagram concepts.

Naming (critical):
  C4 Container  → SoftwareContainer   (NOT ContainerImage / Docker)
  C4 Component  → Component
  C4 Person     → Person / Actor
  C4 System     → System / ExternalSystem
  C4 Code       → Module / Class / Function / Method
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import (  # noqa: E402
    append_log,
    ensure_bundle,
    iter_concepts,
    parse_frontmatter,
    path_for_type,
    refresh_catalog_index,
    resolve_knowledge_root,
    slugify,
    write_concept,
)
from sac_graph import load_graph  # noqa: E402

# C4 abstraction ← SAC types
C4_PERSON = frozenset({"Person", "Actor"})
C4_SYSTEM = frozenset({"System"})
C4_EXTERNAL = frozenset({"ExternalSystem", "Integration", "IdentityProvider"})
C4_CONTAINER = frozenset({
    "SoftwareContainer", "Service", "WebApp", "MobileApp", "DesktopApp", "AdminApp",
    "Bff", "ApiGateway", "ServerlessFunction", "Database", "Cache", "ObjectStorage",
    "SearchIndex", "MessageQueue", "Topic", "EventStream", "DataStore", "Job",
})
C4_COMPONENT = frozenset({"Component"})
C4_CODE = frozenset({"Module", "Class", "Interface", "Enum", "Method", "Function"})

LEVEL_DIAGRAM = {
    1: "C4ContextDiagram",
    2: "C4ContainerDiagram",
    3: "C4ComponentDiagram",
    4: "C4CodeDiagram",
}


def classify_c4(concept_type: str) -> str | None:
    if concept_type in C4_PERSON:
        return "Person"
    if concept_type in C4_SYSTEM:
        return "SoftwareSystem"
    if concept_type in C4_EXTERNAL:
        return "ExternalSystem"
    if concept_type in C4_CONTAINER:
        return "Container"
    if concept_type in C4_COMPONENT:
        return "Component"
    if concept_type in C4_CODE:
        return "Code"
    return None


def inventory(bundle: Path) -> dict:
    """Group bundle concepts by C4 abstraction."""
    groups: dict[str, list[dict]] = {
        "Person": [],
        "SoftwareSystem": [],
        "ExternalSystem": [],
        "Container": [],
        "Component": [],
        "Code": [],
        "Other": [],
    }
    for p in iter_concepts(bundle):
        if p.name == "index.md":
            continue
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        ctype = fm.get("type") or "Unknown"
        role = classify_c4(ctype)
        rel = "/" + str(p.relative_to(bundle)).replace("\\", "/")
        item = {
            "path": rel,
            "type": ctype,
            "title": fm.get("title") or p.stem,
            "description": (fm.get("description") or "")[:200],
            "c4": role,
        }
        groups[role or "Other"].append(item)
    return groups


def _node_id(title: str) -> str:
    s = slugify(title).replace("-", "_")
    if not s or s[0].isdigit():
        s = "n_" + s
    return s[:40]


def mermaid_context(inv: dict, system_title: str | None = None) -> str:
    systems = inv["SoftwareSystem"]
    people = inv["Person"]
    externals = inv["ExternalSystem"]
    focus = system_title or (systems[0]["title"] if systems else "System")
    lines = [
        "flowchart TB",
        "  %% C4 Level 1 — System Context",
    ]
    for p in people[:12]:
        nid = _node_id(p["title"])
        lines.append(f'  {nid}(("{p["title"]}"))')
        lines.append(f'  {nid} -->|uses| sys["{focus}"]')
    lines.append(f'  sys["{focus}"]')
    for e in externals[:12]:
        nid = _node_id(e["title"])
        lines.append(f'  sys -->|uses| {nid}["{e["title"]}"]')
    if not people and not externals:
        lines.append("  user((User)) -->|uses| sys")
    return "\n".join(lines) + "\n"


def mermaid_containers(inv: dict, system_title: str | None = None) -> str:
    systems = inv["SoftwareSystem"]
    focus = system_title or (systems[0]["title"] if systems else "System")
    containers = inv["Container"]
    lines = [
        "flowchart TB",
        f'  %% C4 Level 2 — Containers inside {focus}',
        f'  subgraph system["{focus}"]',
    ]
    ids = []
    for c in containers[:30]:
        nid = _node_id(c["title"])
        ids.append((nid, c))
        shape = _container_shape(c["type"], c["title"])
        lines.append(f"    {shape}")
    lines.append("  end")
    # naive edges: web/mobile → gateway → services → data
    by_type: dict[str, list[str]] = {}
    for nid, c in ids:
        by_type.setdefault(c["type"], []).append(nid)
    clients = by_type.get("WebApp", []) + by_type.get("MobileApp", []) + by_type.get("AdminApp", [])
    gws = by_type.get("ApiGateway", []) + by_type.get("Bff", [])
    services = by_type.get("Service", []) + by_type.get("SoftwareContainer", []) + by_type.get("ServerlessFunction", [])
    data = (
        by_type.get("Database", [])
        + by_type.get("Cache", [])
        + by_type.get("ObjectStorage", [])
        + by_type.get("MessageQueue", [])
        + by_type.get("Topic", [])
        + by_type.get("DataStore", [])
    )
    for c in clients:
        for g in gws or services[:1]:
            lines.append(f"  {c} --> {g}")
    for g in gws:
        for s in services[:8]:
            lines.append(f"  {g} --> {s}")
    for s in services[:8]:
        for d in data[:8]:
            lines.append(f"  {s} --> {d}")
    if len(lines) < 6:
        lines.append("  %% no containers found — reverse-engineer services/apps/data first")
    return "\n".join(lines) + "\n"


def _container_shape(ctype: str, title: str) -> str:
    nid = _node_id(title)
    if ctype in ("Database", "Cache", "ObjectStorage", "SearchIndex", "DataStore", "DataWarehouse"):
        return f'{nid}[("{title}")]'
    if ctype in ("MessageQueue", "Topic", "EventStream"):
        return f'{nid}{{{{{title}}}}}'
    if ctype in ("WebApp", "MobileApp", "DesktopApp", "AdminApp"):
        return f'{nid}["{title}"]'
    return f'{nid}["{title}"]'


def mermaid_components(inv: dict, container_title: str | None = None) -> str:
    comps = inv["Component"]
    focus = container_title or "Container"
    lines = [
        "flowchart LR",
        f'  %% C4 Level 3 — Components in {focus}',
        f'  subgraph c["{focus}"]',
    ]
    for c in comps[:40]:
        nid = _node_id(c["title"])
        lines.append(f'    {nid}["{c["title"]}"]')
    lines.append("  end")
    if len(comps) >= 2:
        a = _node_id(comps[0]["title"])
        b = _node_id(comps[1]["title"])
        lines.append(f"  {a} --> {b}")
    if not comps:
        lines.append("  %% no Component concepts yet — author or scan")
    return "\n".join(lines) + "\n"


def mermaid_code(inv: dict, focus_title: str | None = None) -> str:
    classes = [x for x in inv["Code"] if x["type"] == "Class"][:25]
    modules = [x for x in inv["Code"] if x["type"] == "Module"][:15]
    lines = [
        "classDiagram",
        f"  %% C4 Level 4 — Code ({focus_title or 'modules/classes'})",
    ]
    for m in modules[:10]:
        mid = _node_id(m["title"]).replace("_", "")
        lines.append(f"  class {mid} {{")
        lines.append(f"    <<module>>")
        lines.append("  }")
    for c in classes:
        cid = _node_id(c["title"]).replace("_", "")
        lines.append(f"  class {cid}")
    if not classes and not modules:
        lines.append("  class Placeholder {")
        lines.append("    <<scan code structure>>")
        lines.append("  }")
    return "\n".join(lines) + "\n"


def structurizr_dsl(inv: dict, workspace_name: str = "SAC") -> str:
    """Best-effort Structurizr DSL export from the second brain."""
    lines = [
        f"workspace \"{workspace_name}\" {{",
        "  model {",
    ]
    person_ids = []
    for p in inv["Person"][:20]:
        pid = _node_id(p["title"])
        person_ids.append(pid)
        lines.append(f'    {pid} = person "{p["title"]}"')
    sys_ids = []
    for s in inv["SoftwareSystem"][:10]:
        sid = _node_id(s["title"])
        sys_ids.append(sid)
        lines.append(f'    {sid} = softwareSystem "{s["title"]}" {{')
        for c in inv["Container"][:40]:
            cid = _node_id(c["title"])
            tech = c["type"]
            lines.append(f'      {cid} = container "{c["title"]}" "{c["description"][:80]}" "{tech}"')
        lines.append("    }")
    for e in inv["ExternalSystem"][:15]:
        eid = _node_id(e["title"])
        lines.append(f'    {eid} = softwareSystem "{e["title"]}" {{')
        lines.append("      tags \"External\"")
        lines.append("    }")
    if person_ids and sys_ids:
        lines.append(f"    {person_ids[0]} -> {sys_ids[0]} \"Uses\"")
    lines += [
        "  }",
        "  views {",
        "    theme default",
        "  }",
        "}",
    ]
    return "\n".join(lines) + "\n"


def generate_views(
    bundle: Path,
    *,
    system: str | None = None,
    write: bool = True,
) -> dict:
    inv = inventory(bundle)
    sys_title = system
    if not sys_title and inv["SoftwareSystem"]:
        sys_title = inv["SoftwareSystem"][0]["title"]
    views = {
        "context": {
            "level": 1,
            "type": "C4ContextDiagram",
            "mermaid": mermaid_context(inv, sys_title),
        },
        "containers": {
            "level": 2,
            "type": "C4ContainerDiagram",
            "mermaid": mermaid_containers(inv, sys_title),
        },
        "components": {
            "level": 3,
            "type": "C4ComponentDiagram",
            "mermaid": mermaid_components(inv, sys_title),
        },
        "code": {
            "level": 4,
            "type": "C4CodeDiagram",
            "mermaid": mermaid_code(inv, sys_title),
        },
        "structurizr_dsl": structurizr_dsl(inv, sys_title or "SAC"),
        "inventory_counts": {k: len(v) for k, v in inv.items()},
    }
    if write:
        ensure_bundle(bundle)
        base = slugify(sys_title or "system")
        for key, meta in (
            ("context", views["context"]),
            ("containers", views["containers"]),
            ("components", views["components"]),
            ("code", views["code"]),
        ):
            dtype = meta["type"]
            slug = f"{base}-c4-l{meta['level']}-{key}"
            title = f"{sys_title or 'System'} — C4 L{meta['level']} {key.title()}"
            listing = meta["mermaid"].rstrip()
            body = (
                f"# {title}\n\n"
                f"**C4 level:** {meta['level']}  \n"
                f"**Generated from:** SAC second brain inventory\n\n"
                f"## Diagram\n\n"
                f"```mermaid\n{listing}\n```\n\n"
                f"## Notes\n\n"
                f"Auto-generated C4 view. Refine edges and technology tags manually; "
                f"link with `c4_view_of` / `zooms_into`.\n"
            )
            rel = path_for_type(dtype, slug)
            links = []
            if inv["SoftwareSystem"]:
                links.append({"target": inv["SoftwareSystem"][0]["path"], "rel": "c4_view_of"})
            write_concept(
                bundle,
                rel,
                {
                    "type": dtype,
                    "title": title,
                    "description": f"C4 level {meta['level']} {key} view",
                    "tags": ["c4", f"c4-l{meta['level']}", "diagram", "generated"],
                    "diagram_format": "mermaid",
                    "diagram_kind": dtype,
                    "c4_level": meta["level"],
                    "status": "active",
                    "truth_state": "current",
                    "verified": False,
                    "generated": True,
                    "source": "sac-c4",
                    "links": links,
                    "stable_timestamp": True,
                },
                body,
            )
        # export DSL alongside diagrams catalog
        dsl_path = bundle / "diagrams" / f"{base}-structurizr.dsl"
        dsl_path.parent.mkdir(parents=True, exist_ok=True)
        dsl_path.write_text(views["structurizr_dsl"], encoding="utf-8")
        views["structurizr_path"] = str(dsl_path.relative_to(bundle))
        refresh_catalog_index(bundle, "diagrams")
        append_log(bundle, f"Generated C4 views for {sys_title or 'system'}")
    return views


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="C4 model integration for SAC")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default="knowledge")
    p.add_argument("--system", default=None)
    p.add_argument("--inventory", action="store_true", help="Print C4 inventory only")
    p.add_argument("--generate", action="store_true", help="Write C4 diagram concepts")
    p.add_argument("--dsl", action="store_true", help="Print Structurizr DSL")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    # allow sample-knowledge path directly
    if not bundle.is_dir() and (Path(args.repo) / "sample-knowledge").is_dir():
        bundle = Path(args.repo).resolve() / "sample-knowledge"
    if args.bundle == "sample-knowledge" or Path(args.bundle).name == "sample-knowledge":
        cand = Path(args.repo).resolve() / "sample-knowledge"
        if cand.is_dir():
            bundle = cand

    inv = inventory(bundle)
    if args.inventory:
        counts = {k: len(v) for k, v in inv.items()}
        if args.json:
            print(json.dumps({"bundle": str(bundle), "counts": counts, "inventory": inv}, indent=2))
        else:
            print(f"C4 inventory: {bundle}")
            for k, v in counts.items():
                print(f"  {k}: {v}")
        return 0
    if args.dsl:
        print(structurizr_dsl(inv, args.system or "SAC"))
        return 0
    if args.generate:
        views = generate_views(bundle, system=args.system, write=True)
        if args.json:
            out = {k: v for k, v in views.items() if k != "structurizr_dsl"}
            out["structurizr_dsl_bytes"] = len(views["structurizr_dsl"])
            print(json.dumps(out, indent=2))
        else:
            print(f"Generated C4 views in {bundle}")
            print(f"  inventory: {views['inventory_counts']}")
            print(f"  structurizr: {views.get('structurizr_path')}")
        return 0
    # default: inventory + short tip
    counts = {k: len(v) for k, v in inv.items()}
    print(f"C4 inventory: {bundle}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print("Use --generate to write C4Context/Container/Component/Code diagrams")
    return 0


if __name__ == "__main__":
    sys.exit(main())
