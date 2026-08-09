#!/usr/bin/env python3
"""Scan build manifests for packages/modules (npm, maven, gradle, cargo, go, pip, poetry).

Extracts only the *common* shape: name, version, language/ecosystem, produces (artifacts),
dependencies (names only — not full lock resolution).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import DEFAULT_IGNORE, load_json_safe, slugify, walk_repo  # noqa: E402

MANIFEST_NAMES = {
    "package.json": "npm",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "pyproject.toml": "python",
    "setup.py": "python",
    "requirements.txt": "pip",
    "Pipfile": "pipenv",
    "composer.json": "composer",
    "Gemfile": "ruby",
    "Package.swift": "swift",
    "mix.exs": "elixir",
}


def _npm_package(path: Path) -> dict[str, Any] | None:
    data = load_json_safe(path)
    if not isinstance(data, dict) or not data.get("name"):
        return None
    deps = list((data.get("dependencies") or {}).keys())
    dev = list((data.get("devDependencies") or {}).keys())
    scripts = list((data.get("scripts") or {}).keys())
    produces = []
    if data.get("main"):
        produces.append(str(data["main"]))
    if data.get("module"):
        produces.append(str(data["module"]))
    if data.get("bin"):
        produces.append("cli-binaries")
    return {
        "name": data["name"],
        "version": data.get("version") or "0.0.0",
        "ecosystem": "npm",
        "language": data.get("type") == "module" and "javascript-esm" or "javascript",
        "path": str(path.parent),
        "manifest": str(path),
        "dependencies": deps[:80],
        "dev_dependencies": dev[:40],
        "scripts": scripts[:30],
        "produces": produces or ["package-artifact"],
        "private": bool(data.get("private")),
        "workspaces": data.get("workspaces"),
    }


def _maven_package(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    def g(tag: str) -> str | None:
        m = re.search(rf"<{tag}>([^<]+)</{tag}>", text)
        return m.group(1).strip() if m else None
    # Prefer project-level (first after <project>)
    artifact = g("artifactId")
    group = g("groupId")
    version = g("version")
    if not artifact:
        return None
    deps = re.findall(r"<artifactId>([^<]+)</artifactId>", text)
    deps = [d for d in deps if d != artifact][:60]
    packaging = g("packaging") or "jar"
    return {
        "name": f"{group}:{artifact}" if group else artifact,
        "version": version or "0.0.0",
        "ecosystem": "maven",
        "language": "java",
        "path": str(path.parent),
        "manifest": str(path),
        "dependencies": deps,
        "dev_dependencies": [],
        "scripts": [],
        "produces": [packaging],
        "private": False,
    }


def _gradle_package(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    name = None
    for pat in (r'rootProject\.name\s*=\s*["\']([^"\']+)', r'archivesBaseName\s*=\s*["\']([^"\']+)'):
        m = re.search(pat, text)
        if m:
            name = m.group(1)
            break
    if not name:
        name = path.parent.name
    deps = re.findall(r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?["\']([^"\']+)["\']', text)
    version_m = re.search(r'version\s*=\s*["\']([^"\']+)', text)
    return {
        "name": name,
        "version": version_m.group(1) if version_m else "0.0.0",
        "ecosystem": "gradle",
        "language": "java" if "java" in text or "kotlin" not in text else "kotlin",
        "path": str(path.parent),
        "manifest": str(path),
        "dependencies": deps[:60],
        "dev_dependencies": [],
        "scripts": [],
        "produces": ["jar"] if "java" in text or "kotlin" in text else ["build-artifact"],
        "private": False,
    }


def _cargo_package(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    name_m = re.search(r'(?m)^name\s*=\s*"([^"]+)"', text)
    ver_m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not name_m:
        return None
    deps = re.findall(r'(?m)^([a-zA-Z0-9_-]+)\s*=\s*', text.split("[dependencies]")[-1].split("[")[0] if "[dependencies]" in text else "")
    deps = [d for d in deps if d not in ("version", "features", "default-features", "path", "git", "optional")][:60]
    return {
        "name": name_m.group(1),
        "version": ver_m.group(1) if ver_m else "0.0.0",
        "ecosystem": "cargo",
        "language": "rust",
        "path": str(path.parent),
        "manifest": str(path),
        "dependencies": deps,
        "dev_dependencies": [],
        "scripts": [],
        "produces": ["binary" if "[[bin]]" in text else "crate"],
        "private": False,
    }


def _go_package(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?m)^module\s+(\S+)", text)
    if not m:
        return None
    reqs = re.findall(r"(?m)^\t(\S+)\s+v[\w.-]+", text)
    return {
        "name": m.group(1),
        "version": "module",
        "ecosystem": "go",
        "language": "go",
        "path": str(path.parent),
        "manifest": str(path),
        "dependencies": reqs[:80],
        "dev_dependencies": [],
        "scripts": [],
        "produces": ["module"],
        "private": False,
    }


def _python_package(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.name == "pyproject.toml":
        name_m = re.search(r'(?m)^name\s*=\s*"([^"]+)"', text)
        ver_m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
        deps = re.findall(r'"([a-zA-Z0-9_.\-]+(?:\[[^\]]+\])?)(?:[>=<!~][^"]*)?"', text)
        # crude: filter common non-deps
        skip = {"build-system", "project", "tool"}
        name = name_m.group(1) if name_m else path.parent.name
        return {
            "name": name,
            "version": ver_m.group(1) if ver_m else "0.0.0",
            "ecosystem": "python",
            "language": "python",
            "path": str(path.parent),
            "manifest": str(path),
            "dependencies": [d for d in deps if d not in skip][:60],
            "dev_dependencies": [],
            "scripts": [],
            "produces": ["wheel", "sdist"],
            "private": False,
        }
    if path.name == "requirements.txt":
        deps = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            deps.append(re.split(r"[>=<!~\[]", line)[0].strip())
        return {
            "name": path.parent.name + "-requirements",
            "version": "0.0.0",
            "ecosystem": "pip",
            "language": "python",
            "path": str(path.parent),
            "manifest": str(path),
            "dependencies": deps[:80],
            "dev_dependencies": [],
            "scripts": [],
            "produces": ["environment"],
            "private": True,
        }
    return None


PARSERS = {
    "npm": _npm_package,
    "maven": _maven_package,
    "gradle": _gradle_package,
    "cargo": _cargo_package,
    "go": _go_package,
    "python": _python_package,
    "pip": _python_package,
}


def scan_packages(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for f in walk_repo(root, ignore=DEFAULT_IGNORE):
        eco = MANIFEST_NAMES.get(f.name)
        if not eco:
            continue
        parser = PARSERS.get(eco)
        if not parser:
            continue
        try:
            pkg = parser(f)
        except Exception:
            continue
        if not pkg:
            continue
        key = f"{pkg['ecosystem']}:{pkg['name']}:{pkg['path']}"
        if key in seen:
            continue
        seen.add(key)
        pkg["slug"] = slugify(f"{pkg['ecosystem']}-{pkg['name']}")
        results.append(pkg)
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan packages/build manifests")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    pkgs = scan_packages(root)
    if args.json:
        print(json.dumps({"packages": pkgs, "count": len(pkgs)}, indent=2))
    else:
        for pkg in pkgs:
            print(f"{pkg['ecosystem']:10} {pkg['name']:40} v{pkg['version']}  ({len(pkg['dependencies'])} deps)")
        print(f"\n{len(pkgs)} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
