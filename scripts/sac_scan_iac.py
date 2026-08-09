#!/usr/bin/env python3
"""Scan CloudFormation, Terraform, CDK, Pulumi, Helm, Kustomize stacks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import DEFAULT_IGNORE, slugify, walk_repo  # noqa: E402


def _detect_cfn(path: Path, text: str) -> dict[str, Any] | None:
    if "AWSTemplateFormatVersion" not in text and "Resources:" not in text:
        # also json CFN
        if '"AWSTemplateFormatVersion"' not in text and '"Resources"' not in text:
            return None
        if path.suffix not in (".yml", ".yaml", ".json", ".template"):
            return None
    if path.suffix not in (".yml", ".yaml", ".json", ".template") and "template" not in path.name.lower():
        if "AWSTemplateFormatVersion" not in text and '"AWSTemplateFormatVersion"' not in text:
            return None
    resources = re.findall(r"(?m)^  (\w+):\s*$", text) if path.suffix != ".json" else re.findall(r'"(\w+)"\s*:\s*\{\s*"Type"', text)
    types = re.findall(r"(?:Type:|\"Type\"\s*:)\s*[\"']?(AWS::[\w:]+)", text)
    return {
        "name": path.stem,
        "slug": slugify(f"cfn-{path.stem}"),
        "kind": "InfrastructureStack",
        "tool": "cloudformation",
        "path": str(path),
        "resource_count": len(set(resources)) or len(types),
        "resource_types": sorted(set(types))[:40],
        "produces": sorted(set(t.split("::")[1] for t in types if "::" in t))[:20],
    }


def _detect_terraform(path: Path, text: str) -> dict[str, Any] | None:
    if path.suffix != ".tf" and path.name not in ("terragrunt.hcl",):
        return None
    resources = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', text)
    modules = re.findall(r'module\s+"([^"]+)"', text)
    providers = re.findall(r'provider\s+"([^"]+)"', text)
    return {
        "name": path.stem if path.suffix == ".tf" else path.parent.name,
        "slug": slugify(f"tf-{path.parent.name}-{path.stem}"),
        "kind": "InfrastructureStack",
        "tool": "terraform",
        "path": str(path),
        "resource_count": len(resources),
        "resource_types": sorted({r[0] for r in resources})[:40],
        "modules": modules[:20],
        "providers": providers[:10],
        "produces": sorted({r[0].split("_")[0] for r in resources})[:20],
    }


def _detect_cdk(path: Path, text: str) -> dict[str, Any] | None:
    if not any(x in text for x in ("aws-cdk-lib", "@aws-cdk/", "aws_cdk", "cdk.Stack", "cdk.App")):
        return None
    if path.suffix not in (".ts", ".js", ".py", ".java", ".go"):
        return None
    constructs = re.findall(r"new\s+(\w+)\(", text)
    return {
        "name": path.stem,
        "slug": slugify(f"cdk-{path.stem}"),
        "kind": "InfrastructureStack",
        "tool": "cdk",
        "path": str(path),
        "resource_count": len(constructs),
        "resource_types": sorted(set(constructs))[:40],
        "produces": ["cloudformation-template"],
    }


def _detect_pulumi(path: Path, text: str) -> dict[str, Any] | None:
    if path.name == "Pulumi.yaml" or path.name == "Pulumi.yml":
        name_m = re.search(r"(?m)^name:\s*(\S+)", text)
        runtime_m = re.search(r"(?m)^  name:\s*(\S+)", text) or re.search(r"(?m)^runtime:\s*(\S+)", text)
        return {
            "name": name_m.group(1) if name_m else path.parent.name,
            "slug": slugify(f"pulumi-{path.parent.name}"),
            "kind": "InfrastructureStack",
            "tool": "pulumi",
            "path": str(path),
            "resource_count": 0,
            "resource_types": [],
            "produces": ["pulumi-stack"],
            "runtime": runtime_m.group(1) if runtime_m else None,
        }
    if "import * as pulumi" in text or "from pulumi" in text or '@pulumi/' in text:
        return {
            "name": path.stem,
            "slug": slugify(f"pulumi-{path.stem}"),
            "kind": "InfrastructureStack",
            "tool": "pulumi",
            "path": str(path),
            "resource_count": len(re.findall(r"new\s+\w+\.", text)),
            "resource_types": [],
            "produces": ["pulumi-stack"],
        }
    return None


def _detect_helm(path: Path) -> dict[str, Any] | None:
    if path.name == "Chart.yaml" or path.name == "Chart.yml":
        text = path.read_text(encoding="utf-8", errors="replace")
        name_m = re.search(r"(?m)^name:\s*(\S+)", text)
        ver_m = re.search(r"(?m)^version:\s*(\S+)", text)
        return {
            "name": name_m.group(1) if name_m else path.parent.name,
            "slug": slugify(f"helm-{path.parent.name}"),
            "kind": "InfrastructureStack",
            "tool": "helm",
            "path": str(path),
            "version": ver_m.group(1) if ver_m else None,
            "resource_count": 0,
            "resource_types": ["HelmChart"],
            "produces": ["kubernetes-manifests"],
        }
    return None


def _detect_kustomize(path: Path) -> dict[str, Any] | None:
    if path.name in ("kustomization.yaml", "kustomization.yml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        resources = re.findall(r"(?m)^- (\S+\.ya?ml)\s*$", text)
        return {
            "name": path.parent.name,
            "slug": slugify(f"kust-{path.parent.name}"),
            "kind": "InfrastructureStack",
            "tool": "kustomize",
            "path": str(path),
            "resource_count": len(resources),
            "resource_types": ["Kustomization"],
            "resources": resources[:30],
            "produces": ["kubernetes-manifests"],
        }
    return None


def scan_iac(root: Path) -> list[dict[str, Any]]:
    stacks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for f in walk_repo(root):
        try:
            text = f.read_text(encoding="utf-8", errors="replace") if f.stat().st_size < 2_000_000 else ""
        except OSError:
            continue
        candidates = [
            _detect_helm(f),
            _detect_kustomize(f),
            _detect_pulumi(f, text) if text else None,
            _detect_terraform(f, text) if text else None,
            _detect_cdk(f, text) if text else None,
            _detect_cfn(f, text) if text else None,
        ]
        for c in candidates:
            if not c:
                continue
            key = c["path"]
            if key in seen:
                continue
            seen.add(key)
            stacks.append(c)
    return stacks


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan IaC")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    stacks = scan_iac(Path(args.root).resolve())
    if args.json:
        print(json.dumps({"stacks": stacks, "count": len(stacks)}, indent=2))
    else:
        for s in stacks:
            print(f"{s['tool']:14} {s['name']:30} resources={s.get('resource_count', 0)}")
        print(f"\n{len(stacks)} stack(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
