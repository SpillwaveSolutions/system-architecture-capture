#!/usr/bin/env python3
"""Discover Mermaid and PlantUML diagrams in repo markdown and .puml files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import slugify  # noqa: E402

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".venv", "venv",
    "__pycache__", ".tox", "coverage", ".next", "target",
}

# fenced blocks: ```mermaid ... ``` or ```plantuml ... ``` or ```puml ... ```
FENCE_RE = re.compile(
    r"```(?P<lang>mermaid|plantuml|puml)\s*\n(?P<body>.*?)```",
    re.I | re.S,
)
# @startuml ... @enduml in free text / .puml
PUML_RE = re.compile(r"@startuml(?P<body>.*?)@enduml", re.I | re.S)

KIND_HINTS = [
    (re.compile(r"\bsalt\b|wireframe|mockup", re.I), "Wireframe"),
    (re.compile(r"\berDiagram\b|entity\s*\{", re.I), "ErdDiagram"),
    (re.compile(r"\bclassDiagram\b|^\s*class\s+\w+", re.M), "ClassDiagram"),
    (re.compile(r"\bstateDiagram|state\s+\"", re.I), "StateMachineDiagram"),
    (re.compile(r"\bsequenceDiagram\b|^\s*\w+->>", re.M), "SequenceDiagram"),
    (re.compile(r"\bflowchart\b|\bgraph\s+(TB|LR|TD|BT|RL)\b", re.I), "ActivityDiagram"),
    (re.compile(r"\bC4Context\b|\bC4Container\b|Person\(|System\(", re.I), "C4Diagram"),
    (re.compile(r"component\s+\[|componentDiagram|package\s+\"", re.I), "ComponentDiagram"),
    (re.compile(r"deployment|node\s+\"|cloud\s+\"", re.I), "DeploymentDiagram"),
    (re.compile(r"architecture|context\s+diagram", re.I), "ArchitectureDiagram"),
    (re.compile(r"activity|start\s*$|stop\s*$", re.I | re.M), "ActivityDiagram"),
]


def infer_kind(lang: str, body: str, path_hint: str = "") -> str:
    blob = f"{path_hint}\n{body}"
    for rx, kind in KIND_HINTS:
        if rx.search(blob):
            return kind
    if lang.lower() in ("plantuml", "puml") and re.search(r"\bsalt\b", body, re.I):
        return "Wireframe"
    return "Diagram"


def _iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in {".md", ".markdown", ".mdx", ".puml", ".plantuml", ".pu"}:
            yield p


def scan_diagrams(root: Path) -> list[dict]:
    root = root.resolve()
    found: list[dict] = []
    seen: set[tuple[str, int]] = set()

    for path in _iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(root))

        if path.suffix.lower() in {".puml", ".plantuml", ".pu"}:
            for i, m in enumerate(PUML_RE.finditer(text)):
                body = m.group(0).strip()
                key = (rel, m.start())
                if key in seen:
                    continue
                seen.add(key)
                kind = infer_kind("plantuml", body, rel)
                title = _title_from_puml(body) or f"{path.stem}-{i+1}"
                found.append(_item(root, path, rel, "plantuml", kind, body, title, i))
            # whole file if no @startuml
            if not PUML_RE.search(text) and text.strip():
                body = text.strip()
                if not body.startswith("@startuml"):
                    body = f"@startuml\n{body}\n@enduml"
                kind = infer_kind("plantuml", body, rel)
                found.append(_item(root, path, rel, "plantuml", kind, body, path.stem, 0))
            continue

        # markdown fences
        for i, m in enumerate(FENCE_RE.finditer(text)):
            lang = m.group("lang").lower()
            if lang == "puml":
                lang = "plantuml"
            body = m.group("body").strip()
            if lang == "plantuml" and "@startuml" not in body.lower():
                body = f"@startuml\n{body}\n@enduml"
            kind = infer_kind(lang, body, rel)
            # title: nearest heading above
            title = _title_near(text, m.start()) or f"{path.stem}-{lang}-{i+1}"
            found.append(_item(root, path, rel, lang, kind, body, title, i))

    return found


def _title_from_puml(body: str) -> str | None:
    m = re.search(r"^\s*title\s+(.+)$", body, re.M | re.I)
    if m:
        return m.group(1).strip().strip('"')
    return None


def _title_near(text: str, pos: int) -> str | None:
    before = text[:pos]
    heads = list(re.finditer(r"^#{1,3}\s+(.+)$", before, re.M))
    if heads:
        return heads[-1].group(1).strip()
    return None


def _item(root, path, rel, lang, kind, body, title, idx) -> dict:
    slug = slugify(f"{path.stem}-{kind}-{idx}")
    return {
        "slug": slug,
        "title": title[:120],
        "kind": kind,
        "format": lang,  # mermaid | plantuml
        "path": rel,
        "source_path": rel,
        "body": body,
        "lines": body.count("\n") + 1,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan Mermaid/PlantUML diagrams")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    data = scan_diagrams(Path(args.root))
    if args.json:
        # omit huge bodies in summary mode? keep for capture
        print(json.dumps({"count": len(data), "diagrams": data}, indent=2))
    else:
        print(f"Diagrams: {len(data)}")
        for d in data[:30]:
            print(f"  [{d['format']}/{d['kind']}] {d['title']}  ({d['path']})")
        if len(data) > 30:
            print(f"  … {len(data) - 30} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
