#!/usr/bin/env python3
"""Scan Dockerfiles, compose files, and container runtime hints."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import DEFAULT_IGNORE, slugify, walk_repo  # noqa: E402


def parse_dockerfile(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    froms = re.findall(r"(?im)^FROM\s+(\S+)", text)
    expos = re.findall(r"(?im)^EXPOSE\s+(.+)", text)
    ports = []
    for e in expos:
        ports.extend(re.findall(r"\d+", e))
    workdirs = re.findall(r"(?im)^WORKDIR\s+(\S+)", text)
    entrys = re.findall(r"(?im)^(?:ENTRYPOINT|CMD)\s+(.+)", text)
    base = froms[0] if froms else "unknown"
    stages = froms
    name = path.parent.name if path.name.upper() == "DOCKERFILE" else path.stem
    return {
        "name": name,
        "slug": slugify(f"img-{name}"),
        "kind": "ContainerImage",
        "path": str(path),
        "base_image": base,
        "stages": stages,
        "ports": ports,
        "workdir": workdirs[-1] if workdirs else None,
        "entry": entrys[-1] if entrys else None,
        "multi_stage": len(stages) > 1,
        "runtime_hint": _runtime_from_base(base),
    }


def _runtime_from_base(base: str) -> str:
    b = base.lower()
    if "distroless" in b or "scratch" in b:
        return "minimal"
    if "alpine" in b:
        return "docker-alpine"
    if any(x in b for x in ("python", "node", "openjdk", "eclipse-temurin", "golang", "rust")):
        return "docker"
    return "containerd-compatible"


def parse_compose(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    services: list[dict[str, Any]] = []
    # Lightweight service name extraction
    in_services = False
    current = None
    for line in text.splitlines():
        if re.match(r"^services:\s*$", line):
            in_services = True
            continue
        if in_services:
            if re.match(r"^[a-zA-Z]", line) and not line.startswith(" "):
                break
            m = re.match(r"^  ([a-zA-Z0-9_-]+):\s*$", line)
            if m:
                current = {"name": m.group(1), "slug": slugify(f"svc-compose-{m.group(1)}"), "compose": str(path), "ports": [], "image": None, "build": None}
                services.append(current)
                continue
            if current:
                im = re.match(r"^\s+image:\s*[\"']?(\S+?)[\"']?\s*$", line)
                if im:
                    current["image"] = im.group(1)
                bm = re.match(r"^\s+build:\s*[\"']?(\S+?)[\"']?\s*$", line)
                if bm:
                    current["build"] = bm.group(1)
                pm = re.findall(r"[\"']?(\d+):(\d+)[\"']?", line)
                for host, cont in pm:
                    current["ports"].append({"host": host, "container": cont})
    return services


def scan_containers(root: Path) -> dict[str, Any]:
    images: list[dict[str, Any]] = []
    compose_svcs: list[dict[str, Any]] = []
    for f in walk_repo(root):
        name = f.name.upper()
        if name == "DOCKERFILE" or name.startswith("DOCKERFILE."):
            try:
                images.append(parse_dockerfile(f))
            except Exception:
                pass
        elif f.name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            try:
                compose_svcs.extend(parse_compose(f))
            except Exception:
                pass
    return {"images": images, "compose_services": compose_svcs, "count": len(images) + len(compose_svcs)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan containers")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    data = scan_containers(Path(args.root).resolve())
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for img in data["images"]:
            print(f"image  {img['name']:30} base={img['base_image']}")
        for s in data["compose_services"]:
            print(f"compose {s['name']:30} image={s.get('image')}")
        print(f"\n{data['count']} container artifact(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
