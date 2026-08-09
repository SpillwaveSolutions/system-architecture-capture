#!/usr/bin/env python3
"""Scan Kubernetes manifests for Deployments, Services, Ingress, etc."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import slugify, walk_repo  # noqa: E402

K8S_KINDS = {
    "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob",
    "Service", "Ingress", "ConfigMap", "Secret", "ServiceAccount",
    "Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding",
    "NetworkPolicy", "HorizontalPodAutoscaler", "PodDisruptionBudget",
    "PersistentVolumeClaim", "Namespace", "Gateway", "HTTPRoute",
    "VirtualService", "DestinationRule", "PeerAuthentication",  # Istio
}


def parse_k8s_doc(text: str, path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    # split multi-doc yaml
    for part in re.split(r"(?m)^---\s*$", text):
        kind_m = re.search(r"(?m)^kind:\s*(\w+)\s*$", part)
        name_m = re.search(r"(?m)^  name:\s*[\"']?([^\s\"']+)", part)
        ns_m = re.search(r"(?m)^  namespace:\s*[\"']?([^\s\"']+)", part)
        api_m = re.search(r"(?m)^apiVersion:\s*(\S+)\s*$", part)
        if not kind_m:
            continue
        kind = kind_m.group(1)
        if kind not in K8S_KINDS and kind not in ("Pod", "ReplicaSet"):
            continue
        name = name_m.group(1) if name_m else "unnamed"
        images = re.findall(r"(?m)^\s+image:\s*[\"']?([^\s\"']+)", part)
        ports = re.findall(r"(?m)^\s+containerPort:\s*(\d+)", part)
        ports += re.findall(r"(?m)^\s+port:\s*(\d+)", part)
        docs.append({
            "name": name,
            "slug": slugify(f"k8s-{kind.lower()}-{name}"),
            "kind": kind,
            "api_version": api_m.group(1) if api_m else None,
            "namespace": ns_m.group(1) if ns_m else "default",
            "path": str(path),
            "images": images[:10],
            "ports": list(dict.fromkeys(ports))[:20],
            "labels": re.findall(r"(?m)^    ([\w.-]+):\s*[\"']?([^\s\"']+)", part)[:20],
        })
    return docs


def scan_k8s(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for f in walk_repo(root):
        if f.suffix not in (".yml", ".yaml"):
            continue
        # skip helm templates with heavy templating sometimes still useful
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "kind:" not in text or "apiVersion:" not in text:
            continue
        try:
            out.extend(parse_k8s_doc(text, f))
        except Exception:
            pass
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan K8s manifests")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    docs = scan_k8s(Path(args.root).resolve())
    if args.json:
        print(json.dumps({"manifests": docs, "count": len(docs)}, indent=2))
    else:
        for d in docs:
            print(f"{d['kind']:24} {d['namespace']:16} {d['name']}")
        print(f"\n{len(docs)} manifest object(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
