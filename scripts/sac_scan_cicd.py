#!/usr/bin/env python3
"""Scan CI/CD pipelines: GitHub Actions, GitLab CI, Jenkins, CircleCI, Argo, Tekton."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import slugify, walk_repo  # noqa: E402


def scan_github_actions(root: Path) -> list[dict[str, Any]]:
    out = []
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.is_dir():
        return out
    for f in sorted(wf_dir.glob("*.y*ml")):
        text = f.read_text(encoding="utf-8", errors="replace")
        name_m = re.search(r"(?m)^name:\s*[\"']?(.+?)[\"']?\s*$", text)
        jobs = re.findall(r"(?m)^  ([a-zA-Z0-9_-]+):\s*$", text.split("jobs:")[-1] if "jobs:" in text else "")
        uses = re.findall(r"uses:\s*(\S+)", text)
        on = re.findall(r"(?m)^  (\w+):\s*$", text.split("on:")[-1].split("jobs:")[0] if "on:" in text else "")
        out.append({
            "name": (name_m.group(1).strip() if name_m else f.stem),
            "slug": slugify(f"gha-{f.stem}"),
            "kind": "Pipeline",
            "platform": "github-actions",
            "path": str(f),
            "jobs": jobs[:20],
            "actions": uses[:30],
            "triggers": on[:15],
            "deploys": bool(re.search(r"(?i)deploy|release|helm|kubectl|terraform apply", text)),
        })
    return out


def scan_gitlab_ci(root: Path) -> list[dict[str, Any]]:
    f = root / ".gitlab-ci.yml"
    if not f.is_file():
        f = root / ".gitlab-ci.yaml"
    if not f.is_file():
        return []
    text = f.read_text(encoding="utf-8", errors="replace")
    stages = re.findall(r"(?m)^  - (\w+)", text.split("stages:")[-1].split("\n\n")[0] if "stages:" in text else "")
    jobs = re.findall(r"(?m)^([a-zA-Z0-9_-]+):\s*$", text)
    jobs = [j for j in jobs if j not in ("stages", "variables", "include", "default", "workflow")]
    return [{
        "name": "gitlab-ci",
        "slug": "gitlab-ci",
        "kind": "Pipeline",
        "platform": "gitlab-ci",
        "path": str(f),
        "jobs": jobs[:30],
        "stages": stages,
        "actions": [],
        "triggers": ["push", "mr"],
        "deploys": "deploy" in text.lower(),
    }]


def scan_circleci(root: Path) -> list[dict[str, Any]]:
    f = root / ".circleci" / "config.yml"
    if not f.is_file():
        return []
    text = f.read_text(encoding="utf-8", errors="replace")
    jobs = re.findall(r"(?m)^  ([a-zA-Z0-9_-]+):\s*$", text.split("jobs:")[-1].split("workflows:")[0] if "jobs:" in text else "")
    return [{
        "name": "circleci",
        "slug": "circleci",
        "kind": "Pipeline",
        "platform": "circleci",
        "path": str(f),
        "jobs": jobs[:30],
        "actions": [],
        "triggers": ["push"],
        "deploys": "deploy" in text.lower(),
    }]


def scan_jenkins(root: Path) -> list[dict[str, Any]]:
    out = []
    for name in ("Jenkinsfile", "jenkinsfile"):
        f = root / name
        if f.is_file():
            text = f.read_text(encoding="utf-8", errors="replace")
            stages = re.findall(r"stage\s*\(\s*['\"]([^'\"]+)", text)
            out.append({
                "name": "jenkins",
                "slug": "jenkins",
                "kind": "Pipeline",
                "platform": "jenkins",
                "path": str(f),
                "jobs": stages,
                "actions": [],
                "triggers": [],
                "deploys": "deploy" in text.lower(),
            })
    return out


def scan_argo(root: Path) -> list[dict[str, Any]]:
    out = []
    for f in walk_repo(root):
        if f.suffix not in (".yml", ".yaml"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "kind: Application" in text and "argoproj.io" in text:
            name_m = re.search(r"(?m)^  name:\s*(\S+)", text)
            out.append({
                "name": name_m.group(1) if name_m else f.stem,
                "slug": slugify(f"argo-{f.stem}"),
                "kind": "Pipeline",
                "platform": "argo-cd",
                "path": str(f),
                "jobs": [],
                "actions": [],
                "triggers": ["gitops"],
                "deploys": True,
            })
        if "kind: Workflow" in text and "argoproj.io" in text:
            name_m = re.search(r"(?m)^  name:\s*(\S+)", text)
            out.append({
                "name": name_m.group(1) if name_m else f.stem,
                "slug": slugify(f"argo-wf-{f.stem}"),
                "kind": "Workflow",
                "platform": "argo-workflows",
                "path": str(f),
                "jobs": re.findall(r"(?m)^      - name: (\S+)", text)[:20],
                "actions": [],
                "triggers": [],
                "deploys": False,
            })
    return out


def scan_tekton(root: Path) -> list[dict[str, Any]]:
    out = []
    for f in walk_repo(root):
        if f.suffix not in (".yml", ".yaml"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "tekton.dev" not in text:
            continue
        kind_m = re.search(r"(?m)^kind:\s*(\w+)", text)
        name_m = re.search(r"(?m)^  name:\s*(\S+)", text)
        if not kind_m:
            continue
        out.append({
            "name": name_m.group(1) if name_m else f.stem,
            "slug": slugify(f"tekton-{f.stem}"),
            "kind": "Pipeline" if "Pipeline" in kind_m.group(1) else "Workflow",
            "platform": "tekton",
            "path": str(f),
            "jobs": [],
            "actions": [],
            "triggers": [],
            "deploys": "deploy" in text.lower(),
        })
    return out


def scan_cicd(root: Path) -> list[dict[str, Any]]:
    pipelines = []
    pipelines.extend(scan_github_actions(root))
    pipelines.extend(scan_gitlab_ci(root))
    pipelines.extend(scan_circleci(root))
    pipelines.extend(scan_jenkins(root))
    pipelines.extend(scan_argo(root))
    pipelines.extend(scan_tekton(root))
    return pipelines


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan CI/CD")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    pipes = scan_cicd(Path(args.root).resolve())
    if args.json:
        print(json.dumps({"pipelines": pipes, "count": len(pipes)}, indent=2))
    else:
        for x in pipes:
            print(f"{x['platform']:16} {x['name']:40} deploys={x.get('deploys')}")
        print(f"\n{len(pipes)} pipeline(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
