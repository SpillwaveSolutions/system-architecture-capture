#!/usr/bin/env python3
"""Scan Structurizr DSL (.dsl) workspaces into SAC C4-oriented findings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import slugify  # noqa: E402

SKIP = {".git", "node_modules", "vendor", "dist", "build", ".venv"}

PERSON_RE = re.compile(r'(\w+)\s*=\s*person\s+"([^"]+)"', re.I)
SYS_RE = re.compile(r'(\w+)\s*=\s*softwareSystem\s+"([^"]+)"', re.I)
CONTAINER_RE = re.compile(
    r'(\w+)\s*=\s*container\s+"([^"]+)"(?:\s+"([^"]*)")?(?:\s+"([^"]*)")?',
    re.I,
)
COMPONENT_RE = re.compile(
    r'(\w+)\s*=\s*component\s+"([^"]+)"(?:\s+"([^"]*)")?(?:\s+"([^"]*)")?',
    re.I,
)


def scan_structurizr(root: Path) -> dict:
    root = root.resolve()
    files = []
    people, systems, containers, components = [], [], [], []
    for p in root.rglob("*.dsl"):
        if any(part in SKIP for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(p.relative_to(root))
        files.append(rel)
        for m in PERSON_RE.finditer(text):
            people.append({"id": m.group(1), "name": m.group(2), "path": rel, "kind": "Person"})
        for m in SYS_RE.finditer(text):
            systems.append({"id": m.group(1), "name": m.group(2), "path": rel, "kind": "System", "slug": slugify(m.group(2))})
        for m in CONTAINER_RE.finditer(text):
            containers.append({
                "id": m.group(1),
                "name": m.group(2),
                "description": m.group(3) or "",
                "technology": m.group(4) or "",
                "path": rel,
                "kind": "SoftwareContainer",
                "slug": slugify(m.group(2)),
            })
        for m in COMPONENT_RE.finditer(text):
            components.append({
                "id": m.group(1),
                "name": m.group(2),
                "description": m.group(3) or "",
                "technology": m.group(4) or "",
                "path": rel,
                "kind": "Component",
                "slug": slugify(m.group(2)),
            })
    return {
        "files": files,
        "people": people,
        "systems": systems,
        "containers": containers,
        "components": components,
        "count": len(people) + len(systems) + len(containers) + len(components),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    data = scan_structurizr(Path(args.root))
    print(json.dumps(data, indent=2) if args.json else f"Structurizr: {data['count']} elements in {len(data['files'])} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
