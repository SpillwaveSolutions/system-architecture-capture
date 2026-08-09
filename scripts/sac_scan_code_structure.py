#!/usr/bin/env python3
"""Lightweight reverse-engineering of modules, classes, methods, and functions.

Stack-agnostic heuristics — not a full language server. Captures enough structure
for the architecture second brain (ownership, blast radius, design-time packs).
"""

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
    "__pycache__", ".tox", "coverage", ".next", "target", "out",
    "generated", ".turbo", ".cache",
}

# language by extension
LANG = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "csharp",
    ".rb": "ruby",
    ".rs": "rust",
    ".php": "php",
    ".scala": "scala",
}

# class / function patterns (best-effort)
CLASS_RX = {
    "python": re.compile(r"^class\s+(\w+)", re.M),
    "typescript": re.compile(r"^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)", re.M),
    "javascript": re.compile(r"^(?:export\s+)?class\s+(\w+)", re.M),
    "go": re.compile(r"^type\s+(\w+)\s+struct\b", re.M),
    "java": re.compile(r"(?:public|protected|private)?\s*(?:static\s+)?(?:final\s+)?class\s+(\w+)", re.M),
    "kotlin": re.compile(r"^(?:data\s+)?class\s+(\w+)", re.M),
    "csharp": re.compile(r"(?:public|internal|private)?\s*(?:static\s+)?(?:partial\s+)?class\s+(\w+)", re.M),
    "ruby": re.compile(r"^class\s+(\w+)", re.M),
    "rust": re.compile(r"^(?:pub\s+)?struct\s+(\w+)", re.M),
    "php": re.compile(r"class\s+(\w+)", re.M),
    "scala": re.compile(r"^(?:case\s+)?class\s+(\w+)", re.M),
}

FUNC_RX = {
    "python": re.compile(r"^def\s+(\w+)\s*\(", re.M),
    "typescript": re.compile(
        r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(",
        re.M,
    ),
    "javascript": re.compile(
        r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(",
        re.M,
    ),
    "go": re.compile(r"^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(", re.M),
    "java": re.compile(
        r"(?:public|protected|private)\s+(?:static\s+)?[\w<>,\[\]\s]+\s+(\w+)\s*\(",
        re.M,
    ),
    "kotlin": re.compile(r"^\s*fun\s+(\w+)\s*\(", re.M),
    "csharp": re.compile(
        r"(?:public|private|protected|internal)\s+(?:static\s+)?[\w<>,\[\]\?]+\s+(\w+)\s*\(",
        re.M,
    ),
    "ruby": re.compile(r"^\s*def\s+(\w+)", re.M),
    "rust": re.compile(r"^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*[<\(]", re.M),
    "php": re.compile(r"function\s+(\w+)\s*\(", re.M),
    "scala": re.compile(r"^\s*def\s+(\w+)", re.M),
}

METHOD_HINT = re.compile(
    r"^\s+(?:public|private|protected|async|static|export)?\s*(?:async\s+)?(\w+)\s*\([^;]*\)\s*\{?",
    re.M,
)

# skip common noise method names
SKIP_FUNCS = {
    "if", "for", "while", "switch", "catch", "return", "new", "get", "set",
    "from", "import", "export", "class", "interface", "struct", "type",
}


def scan_code_structure(root: Path, *, max_files: int = 4000, max_per_file: int = 80) -> dict:
    root = root.resolve()
    modules: dict[str, dict] = {}
    classes: list[dict] = []
    functions: list[dict] = []
    methods: list[dict] = []
    n_files = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        lang = LANG.get(path.suffix.lower())
        if not lang:
            continue
        n_files += 1
        if n_files > max_files:
            break
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(text) > 400_000:
            continue
        rel = str(path.relative_to(root))
        mod_name = _module_name(rel, lang)
        mod_slug = slugify(mod_name.replace("/", "-").replace(".", "-"))
        if mod_slug not in modules:
            modules[mod_slug] = {
                "slug": mod_slug,
                "name": mod_name,
                "language": lang,
                "path": str(Path(rel).parent).replace("\\", "/"),
                "files": [],
            }
        modules[mod_slug]["files"].append(rel)

        crx = CLASS_RX.get(lang)
        if crx:
            for m in crx.finditer(text):
                cname = m.group(1)
                classes.append({
                    "slug": slugify(f"{mod_slug}-{cname}"),
                    "name": cname,
                    "module": mod_slug,
                    "module_name": mod_name,
                    "language": lang,
                    "path": rel,
                    "kind": "Class",
                })
                # methods inside class block (heuristic: indented defs after class)
                if lang == "python":
                    for mm in re.finditer(
                        rf"class\s+{re.escape(cname)}\b.*?(?=^class\s|\Z)",
                        text,
                        re.S | re.M,
                    ):
                        block = mm.group(0)
                        for dm in re.finditer(r"^\s+def\s+(\w+)\s*\(", block, re.M):
                            mname = dm.group(1)
                            if mname.startswith("__") and mname.endswith("__"):
                                continue
                            methods.append({
                                "slug": slugify(f"{mod_slug}-{cname}-{mname}"),
                                "name": mname,
                                "class": cname,
                                "module": mod_slug,
                                "language": lang,
                                "path": rel,
                            })

        frx = FUNC_RX.get(lang)
        if frx:
            count = 0
            for m in frx.finditer(text):
                groups = [g for g in m.groups() if g]
                if not groups:
                    continue
                fname = groups[0]
                if fname in SKIP_FUNCS or fname.startswith("_") and lang == "python":
                    # keep public-ish only for python dunder skip already
                    if fname.startswith("__"):
                        continue
                if lang == "python" and fname.startswith("_"):
                    continue
                functions.append({
                    "slug": slugify(f"{mod_slug}-{fname}"),
                    "name": fname,
                    "module": mod_slug,
                    "module_name": mod_name,
                    "language": lang,
                    "path": rel,
                })
                count += 1
                if count >= max_per_file:
                    break

    return {
        "modules": list(modules.values()),
        "classes": classes[:5000],
        "functions": functions[:8000],
        "methods": methods[:8000],
        "file_count": n_files,
        "count": len(modules) + len(classes) + len(functions) + len(methods),
    }


def _module_name(rel: str, lang: str) -> str:
    p = Path(rel)
    parts = list(p.parts[:-1])
    stem = p.stem
    if lang == "python":
        if stem != "__init__":
            parts = parts + [stem]
        return ".".join(parts) if parts else stem
    if lang in ("java", "kotlin", "csharp", "scala"):
        return ".".join(parts + [stem]) if parts else stem
    if lang == "go":
        return "/".join(parts) if parts else stem
    # js/ts — path without extension
    return "/".join(parts + [stem]) if parts else stem


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan modules/classes/functions")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    data = scan_code_structure(Path(args.root))
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"Files: {data['file_count']}")
        print(f"  modules:   {len(data['modules'])}")
        print(f"  classes:   {len(data['classes'])}")
        print(f"  methods:   {len(data['methods'])}")
        print(f"  functions: {len(data['functions'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
