#!/usr/bin/env python3
"""Materialize scan findings into SAC OKF knowledge concepts."""

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
    slugify,
    write_concept,
)
from sac_scan import full_scan  # noqa: E402


def capture_scan(bundle: Path, scan: dict, *, system_name: str = "System") -> dict:
    stats = {"created": 0, "updated": 0, "skipped": 0}
    sys_slug = slugify(system_name)
    sys_path = path_for_type("System", sys_slug)
    _, st = write_concept(
        bundle,
        sys_path,
        {
            "type": "System",
            "title": system_name,
            "description": f"Reverse-engineered system: {system_name}",
            "tags": ["sac", "system"],
            "status": "active",
            "truth_state": "current",
            "verified": False,
            "source": "sac-scan",
                "generated": True,
            "stable_timestamp": True,
        },
        f"# {system_name}\n\nArchitecture knowledge reverse-engineered by System Architecture Capture.\n",
    )
    stats[st] = stats.get(st, 0) + 1

    # Packages
    for pkg in scan.get("packages") or []:
        slug = pkg.get("slug") or slugify(pkg["name"])
        rel = path_for_type("Package", slug)
        body = (
            f"# {pkg['name']}\n\n"
            f"**Ecosystem:** {pkg['ecosystem']}  \n"
            f"**Language:** {pkg.get('language')}  \n"
            f"**Version:** {pkg.get('version')}  \n"
            f"**Path:** `{pkg.get('path')}`\n\n"
            f"## Produces\n\n"
            + "\n".join(f"- `{p}`" for p in (pkg.get("produces") or ["artifact"]))
            + "\n\n## Dependencies\n\n"
            + (
                "\n".join(f"- `{d}`" for d in (pkg.get("dependencies") or [])[:40])
                or "_None listed._"
            )
            + "\n"
        )
        links = [{"target": f"/{sys_path}", "rel": "part_of"}]
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Package",
                "title": pkg["name"],
                "description": f"{pkg['ecosystem']} package {pkg['name']}",
                "tags": ["sac", "package", pkg["ecosystem"]],
                "ecosystem": pkg["ecosystem"],
                "language": pkg.get("language"),
                "version": pkg.get("version"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": pkg.get("manifest"),
                "links": links,
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Container images
    for img in (scan.get("containers") or {}).get("images") or []:
        rel = path_for_type("ContainerImage", img["slug"])
        body = (
            f"# {img['name']}\n\n"
            f"**Base:** `{img.get('base_image')}`  \n"
            f"**Runtime:** {img.get('runtime_hint')}  \n"
            f"**Multi-stage:** {img.get('multi_stage')}  \n"
            f"**Ports:** {', '.join(img.get('ports') or []) or '—'}  \n"
            f"**Path:** `{img.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "ContainerImage",
                "title": img["name"],
                "description": f"Container image from {img.get('path')}",
                "tags": ["sac", "container"],
                "base_image": img.get("base_image"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Compose → Service
    for svc in (scan.get("containers") or {}).get("compose_services") or []:
        rel = path_for_type("Service", svc["slug"])
        body = (
            f"# {svc['name']}\n\n"
            f"Discovered via Docker Compose.\n\n"
            f"**Image:** `{svc.get('image') or 'build'}`  \n"
            f"**Build:** `{svc.get('build') or '—'}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Service",
                "title": svc["name"],
                "description": f"Compose service {svc['name']}",
                "tags": ["sac", "service", "compose"],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # IaC stacks
    for stack in scan.get("iac") or []:
        rel = path_for_type("InfrastructureStack", stack["slug"])
        body = (
            f"# {stack['name']}\n\n"
            f"**Tool:** {stack['tool']}  \n"
            f"**Resources:** {stack.get('resource_count', 0)}  \n"
            f"**Path:** `{stack.get('path')}`\n\n"
            f"## Resource types\n\n"
            + (
                "\n".join(f"- `{t}`" for t in (stack.get("resource_types") or [])[:30])
                or "_Unknown / empty._"
            )
            + "\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "InfrastructureStack",
                "title": f"{stack['tool']}: {stack['name']}",
                "description": f"{stack['tool']} stack at {stack.get('path')}",
                "tags": ["sac", "iac", stack["tool"]],
                "tool": stack["tool"],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "provisions"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # K8s workloads → Service / Deployment concepts
    for m in scan.get("k8s") or []:
        if m["kind"] in ("Deployment", "StatefulSet", "DaemonSet"):
            ctype = "Service"
            d = "services"
        elif m["kind"] == "Service":
            ctype = "ApiContract"
            d = "apis"
        elif m["kind"] in ("NetworkPolicy",):
            ctype = "SecurityGroup"
            d = "networks"
        else:
            ctype = "Deployment"
            d = "deployments"
        slug = m["slug"]
        rel = f"{d}/{slug}.md"
        body = (
            f"# {m['name']}\n\n"
            f"**Kind:** {m['kind']}  \n"
            f"**Namespace:** {m.get('namespace')}  \n"
            f"**Images:** {', '.join(f'`{i}`' for i in (m.get('images') or [])) or '—'}  \n"
            f"**Path:** `{m.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": ctype,
                "title": f"{m['kind']}/{m['name']}",
                "description": f"Kubernetes {m['kind']} {m['name']}",
                "tags": ["sac", "k8s", m["kind"].lower()],
                "k8s_kind": m["kind"],
                "namespace": m.get("namespace"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Pipelines
    for pipe in scan.get("cicd") or []:
        rel = path_for_type(pipe.get("kind") or "Pipeline", pipe["slug"])
        body = (
            f"# {pipe['name']}\n\n"
            f"**Platform:** {pipe['platform']}  \n"
            f"**Deploys:** {pipe.get('deploys')}  \n"
            f"**Path:** `{pipe.get('path')}`\n\n"
            f"## Jobs / stages\n\n"
            + (
                "\n".join(f"- `{j}`" for j in (pipe.get("jobs") or pipe.get("stages") or [])[:30])
                or "_None listed._"
            )
            + "\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": pipe.get("kind") or "Pipeline",
                "title": pipe["name"],
                "description": f"{pipe['platform']} pipeline",
                "tags": ["sac", "cicd", pipe["platform"]],
                "platform": pipe["platform"],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Identity providers
    for idp in (scan.get("identity") or {}).get("identity_providers") or []:
        rel = path_for_type("IdentityProvider", idp["slug"])
        body = (
            f"# {idp['name']}\n\n"
            f"Identity provider evidence found in codebase.\n\n"
            f"## Evidence files\n\n"
            + "\n".join(f"- `{e}`" for e in (idp.get("evidence") or [])[:20])
            + "\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "IdentityProvider",
                "title": idp["name"],
                "description": f"SSO/OAuth provider: {idp['provider']}",
                "tags": ["sac", "identity", idp["provider"]],
                "provider": idp["provider"],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Refresh indexes for touched catalogs
    for cat in (
        "systems",
        "packages",
        "containers",
        "services",
        "apis",
        "infrastructure",
        "deployments",
        "pipelines",
        "identity",
        "networks",
    ):
        refresh_catalog_index(bundle, cat)

    append_log(bundle, f"SAC scan capture: {stats}")

    # Diagrams (Mermaid / PlantUML)
    for d in scan.get("diagrams") or []:
        kind = d.get("kind") or "Diagram"
        rel = path_for_type(kind, d["slug"])
        fmt = d.get("format") or "mermaid"
        fence = "plantuml" if fmt == "plantuml" else "mermaid"
        listing = (d.get("body") or "").rstrip()
        body = (
            f"# {d['title']}\n\n"
            f"**Kind:** {kind}  \n"
            f"**Format:** {fmt}  \n"
            f"**Source:** `{d.get('path')}`\n\n"
            f"## Diagram\n\n"
            f"```{fence}\n{listing}\n```\n"
        )
        links = [
            {"target": f"/{sys_path}", "rel": "part_of"},
            {"target": f"/{sys_path}", "rel": "visualizes"},
        ]
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": kind,
                "title": d["title"],
                "description": f"{kind} ({fmt}) from {d.get('path')}",
                "tags": ["sac", "diagram", fmt, str(kind).lower()],
                "diagram_format": fmt,
                "diagram_kind": kind,
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": d.get("source_path") or d.get("path"),
                "links": links,
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    # Code structure: modules, classes, methods, functions
    code = scan.get("code") or {}
    for mod in code.get("modules") or []:
        rel = path_for_type("Module", mod["slug"])
        files = mod.get("files") or []
        body = (
            f"# {mod['name']}\n\n"
            f"**Language:** {mod.get('language')}  \n"
            f"**Path:** `{mod.get('path')}`\n\n"
            f"## Files\n\n"
            + ("\n".join(f"- `{f}`" for f in files[:40]) or "_None._")
            + "\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Module",
                "title": mod["name"],
                "description": f"{mod.get('language')} module {mod['name']}",
                "tags": ["sac", "module", mod.get("language") or "code"],
                "language": mod.get("language"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": mod.get("path"),
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    for cls in (code.get("classes") or [])[:2000]:
        rel = path_for_type("Class", cls["slug"])
        links = [{"target": f"/{sys_path}", "rel": "part_of"}]
        if cls.get("module"):
            links.append({"target": f"/modules/{cls['module']}.md", "rel": "declared_in"})
        body = (
            f"# {cls['name']}\n\n"
            f"**Module:** {cls.get('module_name') or cls.get('module')}  \n"
            f"**Language:** {cls.get('language')}  \n"
            f"**Path:** `{cls.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Class",
                "title": cls["name"],
                "description": f"Class {cls['name']}",
                "tags": ["sac", "class", cls.get("language") or "code"],
                "language": cls.get("language"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": cls.get("path"),
                "links": links,
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    for fn in (code.get("functions") or [])[:3000]:
        rel = path_for_type("Function", fn["slug"])
        links = []
        if fn.get("module"):
            links.append({"target": f"/modules/{fn['module']}.md", "rel": "declared_in"})
        body = (
            f"# {fn['name']}\n\n"
            f"**Module:** {fn.get('module_name') or fn.get('module')}  \n"
            f"**Language:** {fn.get('language')}  \n"
            f"**Path:** `{fn.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Function",
                "title": fn["name"],
                "description": f"Function {fn['name']}",
                "tags": ["sac", "function", fn.get("language") or "code"],
                "language": fn.get("language"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": fn.get("path"),
                "links": links,
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1

    for meth in (code.get("methods") or [])[:3000]:
        rel = path_for_type("Method", meth["slug"])
        class_slug = slugify(f"{meth.get('module', '')}-{meth.get('class', '')}")
        links = [{"target": f"/classes/{class_slug}.md", "rel": "has_method"}]
        body = (
            f"# {meth.get('class')}.{meth['name']}\n\n"
            f"**Class:** {meth.get('class')}  \n"
            f"**Path:** `{meth.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Method",
                "title": f"{meth.get('class')}.{meth['name']}",
                "description": f"Method {meth['name']} on {meth.get('class')}",
                "tags": ["sac", "method", meth.get("language") or "code"],
                "language": meth.get("language"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "sac-scan",
                "generated": True,
                "source_path": meth.get("path"),
                "links": links,
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1


    # Structurizr DSL → C4 concepts
    sz = scan.get("structurizr") or {}
    for person in sz.get("people") or []:
        rel = path_for_type("Person", slugify(person["name"]))
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Person",
                "title": person["name"],
                "description": f"C4 Person from Structurizr ({person.get('path')})",
                "tags": ["c4", "person", "structurizr"],
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "structurizr",
                "generated": True,
                "source_path": person.get("path"),
                "links": [{"target": f"/{sys_path}", "rel": "related_to"}],
                "stable_timestamp": True,
            },
            f"# {person['name']}\n\nC4 **Person** imported from Structurizr DSL.\n",
        )
        stats[st] = stats.get(st, 0) + 1
    for cont in sz.get("containers") or []:
        rel = path_for_type("SoftwareContainer", cont.get("slug") or slugify(cont["name"]))
        body = (
            f"# {cont['name']}\n\n"
            f"**C4 Container** (not a Docker image).\n\n"
            f"**Technology:** {cont.get('technology') or '—'}  \n"
            f"**Description:** {cont.get('description') or '—'}  \n"
            f"**Source:** `{cont.get('path')}`\n"
        )
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "SoftwareContainer",
                "title": cont["name"],
                "description": cont.get("description") or f"C4 container {cont['name']}",
                "tags": ["c4", "software-container", "structurizr"],
                "technology": cont.get("technology"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "structurizr",
                "generated": True,
                "source_path": cont.get("path"),
                "links": [{"target": f"/{sys_path}", "rel": "c4_contains"}],
                "stable_timestamp": True,
            },
            body,
        )
        stats[st] = stats.get(st, 0) + 1
    for comp in sz.get("components") or []:
        rel = path_for_type("Component", comp.get("slug") or slugify(comp["name"]))
        _, st = write_concept(
            bundle,
            rel,
            {
                "type": "Component",
                "title": comp["name"],
                "description": comp.get("description") or f"C4 component {comp['name']}",
                "tags": ["c4", "component", "structurizr"],
                "technology": comp.get("technology"),
                "status": "active",
                "truth_state": "current",
                "verified": False,
                "source": "structurizr",
                "generated": True,
                "source_path": comp.get("path"),
                "links": [{"target": f"/{sys_path}", "rel": "part_of"}],
                "stable_timestamp": True,
            },
            f"# {comp['name']}\n\nC4 **Component**.\n",
        )
        stats[st] = stats.get(st, 0) + 1

    return stats


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Capture architecture scan into knowledge bundle")
    p.add_argument("--repo", default=".")
    p.add_argument("--root", default=None, help="Code root to scan (default: --repo)")
    p.add_argument("--bundle", default=None)
    p.add_argument("--system", default="System")
    p.add_argument("--json", action="store_true")
    p.add_argument("--scan-json", default=None, help="Use precomputed scan JSON file")
    args = p.parse_args(argv)
    repo = Path(args.repo).resolve()
    code_root = Path(args.root).resolve() if args.root else repo
    bundle = resolve_knowledge_root(repo, args.bundle)
    ensure_bundle(bundle, args.system)
    if args.scan_json:
        scan = json.loads(Path(args.scan_json).read_text(encoding="utf-8"))
    else:
        scan = full_scan(code_root)
    stats = capture_scan(bundle, scan, system_name=args.system)
    if args.json:
        print(json.dumps({"bundle": str(bundle), "stats": stats, "summary": scan.get("summary")}, indent=2))
    else:
        print(f"Bundle: {bundle}")
        print(f"Stats:  {stats}")
        print(f"Scan:   {scan.get('summary')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
