#!/usr/bin/env python3
"""Breadth-first reverse-engineering plan (presence and counts only).

Maps monorepo / multi-repo roots, ranks focus areas, and emits a Markdown
checklist plus JSON the orchestrator and area sub-agents consume.

This is not a full scan: no AST dumps, no lockfile resolution. Query-time
retrieve (architecture-retriever / sac-retrieve) is a different path.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import DEFAULT_IGNORE, slugify  # noqa: E402

PLAN_VERSION = "1"
SAC_DIRNAME = ".sac"
PLAN_JSON_NAME = "re-plan.json"
PLAN_MD_NAME = "re-plan.md"
PLAN_PROGRESS_NAME = "re-plan-progress.json"

# CI / VCS marker dirs we must walk even though they are dot-directories.
DOT_WALK = frozenset({".github", ".gitlab", ".circleci", ".tekton", ".azure-pipelines"})

MAX_DEPTH = 5
MAX_FILES = 2500
PEEK_BYTES = 2048
MAX_HITS = 24

PACKAGE_FILES = {
    "package.json": "npm",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "pyproject.toml": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "requirements.txt": "pip",
    "Pipfile": "pipenv",
    "composer.json": "composer",
    "Gemfile": "ruby",
    "Package.swift": "swift",
    "mix.exs": "elixir",
}

JAVA_FILES = {
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "settings.gradle": "gradle-settings",
    "settings.gradle.kts": "gradle-settings",
    "gradle.properties": "gradle",
    "gradlew": "gradle-wrapper",
}

TS_FILES = {
    "package.json": "npm",
    "tsconfig.json": "tsconfig",
    "jsconfig.json": "jsconfig",
    "pnpm-workspace.yaml": "pnpm-workspace",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
}

PYTHON_FILES = {
    "pyproject.toml": "python",
    "setup.cfg": "python",
    "setup.py": "python",
    "requirements.txt": "pip",
    "Pipfile": "pipenv",
    "poetry.lock": "poetry",
}

RUST_FILES = {
    "Cargo.toml": "cargo",
    "Cargo.lock": "cargo-lock",
}

OTHER_LANG_FILES = {
    "go.mod": "go",
    "go.work": "go-workspace",
    "Directory.Build.props": "dotnet",
    "composer.json": "composer",
    "Gemfile": "ruby",
    "Package.swift": "swift",
    "mix.exs": "elixir",
}
OTHER_LANG_SUFFIXES = {".csproj": "dotnet", ".fsproj": "dotnet", ".vbproj": "dotnet"}

CONTAINER_EXACT = {
    "Dockerfile": "dockerfile",
    "Containerfile": "dockerfile",
    "docker-compose.yml": "compose",
    "docker-compose.yaml": "compose",
    "compose.yml": "compose",
    "compose.yaml": "compose",
}

IAC_EXACT = {
    "terragrunt.hcl": "terraform",
    "cdk.json": "cdk",
    "cdk.out": "cdk",
    "Pulumi.yaml": "pulumi",
    "Pulumi.yml": "pulumi",
    "Chart.yaml": "helm",
    "Chart.yml": "helm",
    "kustomization.yaml": "kustomize",
    "kustomization.yml": "kustomize",
    "template.yaml": "cloudformation",
    "template.yml": "cloudformation",
}

CICD_EXACT = {
    ".gitlab-ci.yml": "gitlab-ci",
    ".gitlab-ci.yaml": "gitlab-ci",
    "Jenkinsfile": "jenkins",
    "jenkinsfile": "jenkins",
    "azure-pipelines.yml": "azure-devops",
    "azure-pipelines.yaml": "azure-devops",
    "buildspec.yml": "codebuild",
    "buildspec.yaml": "codebuild",
}

K8S_KINDS = {
    "Deployment",
    "StatefulSet",
    "DaemonSet",
    "Service",
    "Ingress",
    "Gateway",
    "HTTPRoute",
    "NetworkPolicy",
    "VirtualService",
    "DestinationRule",
    "PeerAuthentication",
    "Job",
    "CronJob",
    "HorizontalPodAutoscaler",
    "Namespace",
}

K8S_DIR_HINTS = {
    "k8s",
    "kubernetes",
    "manifests",
    "deploy",
    "deployment",
    "overlays",
    "base",
}

MAJOR_DIR_NAMES = {
    "services",
    "apps",
    "packages",
    "libs",
    "lib",
    "cmd",
    "src",
    "internal",
    "infra",
    "infrastructure",
    "terraform",
    "deploy",
    "deployment",
    "k8s",
    "kubernetes",
    "charts",
    "helm",
    "cicd",
    "ci",
    "auth",
    "identity",
    "modules",
    "platform",
    "lambdas",
    "functions",
}

CODE_DIR_HINTS = {"src", "lib", "cmd", "apps", "services", "packages", "internal", "lambdas"}
CODE_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".java",
    ".kt",
    ".cs",
    ".rb",
    ".rs",
    ".php",
    ".scala",
}

DIAGRAM_SUFFIXES = {".puml", ".mmd", ".dsl"}
IDENTITY_NAME_NEEDLES = (
    "auth",
    "oidc",
    "oauth",
    "jwt",
    "cognito",
    "auth0",
    "keycloak",
    "okta",
    "saml",
    "idp",
)
IDENTITY_TEXT_NEEDLES = (
    "auth0",
    "AUTH0_",
    "cognito",
    "COGNITO_",
    "okta",
    "keycloak",
    "openid",
    "oidc",
    "oauth",
    "jsonwebtoken",
    "passport-jwt",
    "login.microsoftonline",
    "SAML_",
    "well-known/openid-configuration",
)
NETWORK_NAME_NEEDLES = (
    "vpc",
    "subnet",
    "nacl",
    "alb",
    "nlb",
    "ingress",
    "gateway",
    "iam",
    "irsa",
    "mesh",
    "istio",
    "linkerd",
)
NETWORK_TEXT_NEEDLES = (
    "aws_vpc",
    "aws_subnet",
    "aws_lb",
    "aws_alb",
    "aws_iam_role",
    "aws_iam_policy",
    "AWS::IAM::Role",
    "AWS::EC2::VPC",
    "kind: Ingress",
    "kind: Gateway",
    "kind: Service",
    "kind: NetworkPolicy",
    "kind: ServiceAccount",
    "VirtualService",
    "istio",
)
K8S_NETWORK_KINDS = {"Ingress", "Gateway", "Service", "NetworkPolicy", "VirtualService"}


def _checklist(pairs: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"id": i, "text": t, "status": "pending", "note": ""} for i, t in pairs]


AREA_SPECS: dict[str, dict[str, Any]] = {
    "packages": {
        "title": "Packages / monorepo map",
        "kind": "domain",
        "agent": "codebase-walker",
        "scan_domains": ["packages"],
        "weight": 3,
        "checklist": _checklist(
            [
                ("inventory", "Inventory package manifests (npm, maven, gradle, go, cargo, pip, poetry)"),
                ("workspaces", "Map workspaces and monorepo package layout"),
                ("boundaries", "Identify service vs library boundaries from directory layout"),
                ("capture", "Capture Package concepts via domain-scoped scanner (script-owned write)"),
                ("apis", "Note OpenAPI, proto, or GraphQL specs if present"),
                ("enrich", "Enrich purpose, ownership, and SLA (agent judgment)"),
            ]
        ),
    },
    "containers": {
        "title": "Containers / images",
        "kind": "domain",
        "agent": "codebase-walker",
        "scan_domains": ["containers"],
        "weight": 4,
        "checklist": _checklist(
            [
                ("inventory", "Inventory Dockerfiles, Containerfiles, and compose files"),
                ("images", "Record base images, ports, and multi-stage builds"),
                ("capture", "Capture ContainerImage concepts (script-owned write)"),
                ("link", "Link images to packages or services they build"),
                ("enrich", "Note runtime hints and deployable vs build-only images"),
            ]
        ),
    },
    "code": {
        "title": "Code structure / service layout",
        "kind": "domain",
        "agent": "codebase-walker",
        "scan_domains": ["code"],
        "weight": 1,
        "checklist": _checklist(
            [
                ("layout", "Map apps/, services/, cmd/, src/ service boundaries"),
                ("capture", "Capture Module / Class / Function signals (script-owned write)"),
                ("contracts", "Flag inferred service boundaries verified: false until deploy evidence"),
                ("enrich", "Enrich module purpose; do not invent edges"),
            ]
        ),
    },
    "iac": {
        "title": "IaC stacks (Terraform / CDK / CFN / Pulumi / Helm / Kustomize)",
        "kind": "domain",
        "agent": "iac-reverse-engineer",
        "scan_domains": ["iac"],
        "weight": 4,
        "checklist": _checklist(
            [
                ("inventory", "Inventory Terraform, CDK, CloudFormation, Pulumi, Helm, Kustomize"),
                ("stacks", "List stacks, tools, and module/chart names"),
                ("capture", "Capture InfrastructureStack concepts (script-owned write)"),
                ("resources", "Note provisioned resource types (counts only)"),
                ("link", "Link stacks to environments and the services they provision"),
                ("enrich", "Enrich ownership and purpose from comments / names"),
            ]
        ),
    },
    "k8s": {
        "title": "Kubernetes deploy / workloads",
        "kind": "domain",
        "agent": "iac-reverse-engineer",
        "scan_domains": ["k8s"],
        "weight": 3,
        "checklist": _checklist(
            [
                ("inventory", "Inventory Deployments, StatefulSets, Jobs, and related workloads"),
                ("services", "Record Service / headless service names and ports"),
                ("capture", "Capture Deployment / Namespace / Cluster concepts (script-owned write)"),
                ("images", "Note container images referenced by workloads"),
                ("link", "Join workloads to Helm/Kustomize stacks and Package images"),
                ("enrich", "Mark inferred environment names; do not invent cluster facts"),
            ]
        ),
    },
    "network-iam": {
        "title": "Network / LB / IAM topology",
        "kind": "domain",
        "agent": "network-iam-topology",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("vpc", "Reconstruct VPC / subnet / SG / NACL from IaC evidence"),
                ("lb", "Record load balancers, Ingress, Gateway API, and mesh entrypoints"),
                ("iam", "Inventory IAM roles, policies, and workload identities (IRSA / WI)"),
                ("mesh", "Note service mesh (Istio / Linkerd / Consul) if present"),
                ("link", "Join Service ↔ Deployment ↔ LB ↔ role with typed edges only when evidenced"),
                ("enrich", "Prefer IaC + K8s over README claims; mark inferred links unverified"),
            ]
        ),
    },
    "cicd": {
        "title": "CI/CD pipelines",
        "kind": "domain",
        "agent": "cicd-reverse-engineer",
        "scan_domains": ["cicd"],
        "weight": 5,
        "checklist": _checklist(
            [
                ("inventory", "Inventory GitHub Actions, GitLab CI, Jenkins, CircleCI, Argo, Tekton"),
                ("stages", "Map build → scan → deploy stages and promotion environments"),
                ("capture", "Capture Pipeline / Workflow concepts (script-owned write)"),
                ("gitops", "Distinguish GitOps (Argo) vs push-based deploys"),
                ("link", "Join pipelines to the services / charts / images they deploy"),
                ("enrich", "Note owners and release cadence if evidenced"),
            ]
        ),
    },
    "identity": {
        "title": "Identity / SSO / auth",
        "kind": "domain",
        "agent": "identity-auth-discoverer",
        "scan_domains": ["identity"],
        "weight": 4,
        "checklist": _checklist(
            [
                ("providers", "Identify IdPs (Auth0, Cognito, Okta, Azure AD, Keycloak, OIDC/SAML)"),
                ("jwt", "Record JWT / OAuth / OIDC validation middleware"),
                ("capture", "Capture IdentityProvider / AuthConfig concepts (script-owned write)"),
                ("svcauth", "Note service-to-service auth (mTLS, mesh policies, API keys)"),
                ("link", "Join services to IdPs with authenticates_via / secured_by when evidenced"),
                ("enrich", "Scrub secrets; never copy live client credentials into the bundle"),
            ]
        ),
    },
    "diagrams": {
        "title": "Diagrams / C4 / Structurizr",
        "kind": "domain",
        "agent": "codebase-walker",
        "scan_domains": ["diagrams", "structurizr"],
        "weight": 2,
        "checklist": _checklist(
            [
                ("inventory", "Inventory Mermaid, PlantUML, and Structurizr sources"),
                ("capture", "Capture Diagram / C4 concepts (script-owned write)"),
                ("link", "Join diagrams to the System / Service they describe"),
                ("enrich", "Do not treat a diagram as runtime evidence without code/IaC backup"),
            ]
        ),
    },
}


def _java_checklist(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    blob = " ".join(str(r.get("kind") or "") for r in rows)
    has_gradle = "gradle" in blob
    has_maven = "maven" in blob
    items: list[tuple[str, str]] = []
    if has_gradle:
        items.append(
            (
                "inventory-gradle",
                "Inventory Gradle multi-project (settings.gradle(.kts), build.gradle(.kts), included builds)",
            )
        )
    if has_maven:
        items.append(("inventory-maven", "Inventory Maven reactors and pom.xml modules"))
    if has_gradle and has_maven:
        items.append(("mixed", "Document how Gradle and Maven coexist (which modules use which)"))
    items.extend(
        [
            ("modules", "Map Java modules vs deployable services / libraries"),
            ("apis", "Note OpenAPI, proto, Spring, or JAX-RS contracts if present"),
            ("enrich", "Enrich Package/Service purpose for Java artifacts (do not re-run sac_scan_packages)"),
        ]
    )
    return _checklist(items)


def _resolve_checklist(spec: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    raw = spec.get("checklist")
    if callable(raw):
        return raw(rows)
    return [dict(x) for x in (raw or [])]


SPECIALIST_SPECS: dict[str, dict[str, Any]] = {
    "lang-java": {
        "title": "Java (Gradle / Maven)",
        "kind": "language",
        "parent": "packages",
        "agent": "java-codebase-walker",
        "scan_domains": [],
        "weight": 3,
        "checklist": _java_checklist,
    },
    "lang-typescript": {
        "title": "TypeScript / JavaScript",
        "kind": "language",
        "parent": "packages",
        "agent": "typescript-codebase-walker",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("inventory", "Inventory package.json, tsconfig/jsconfig, and pnpm/yarn/npm workspaces"),
                ("workspaces", "Map workspace packages vs deployable apps / libraries"),
                ("apis", "Note OpenAPI, tRPC, GraphQL, or proto contracts if present"),
                ("enrich", "Enrich Package/Service purpose for JS/TS artifacts (do not re-run sac_scan_packages)"),
            ]
        ),
    },
    "lang-python": {
        "title": "Python",
        "kind": "language",
        "parent": "packages",
        "agent": "python-codebase-walker",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("inventory", "Inventory pyproject.toml, setup.cfg/py, requirements, Pipfile / Poetry"),
                ("packages", "Distinguish apps, libraries, and extras / optional deps"),
                ("apis", "Note FastAPI / Django / OpenAPI / proto contracts if present"),
                ("enrich", "Enrich Package/Service purpose for Python artifacts (do not re-run sac_scan_packages)"),
            ]
        ),
    },
    "lang-rust": {
        "title": "Rust",
        "kind": "language",
        "parent": "packages",
        "agent": "rust-codebase-walker",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("inventory", "Inventory Cargo.toml workspace members and crates"),
                ("bins", "Distinguish bin vs lib crates and deployable services"),
                ("enrich", "Enrich Package/Service purpose for Rust crates (do not re-run sac_scan_packages)"),
            ]
        ),
    },
    "lang-other": {
        "title": "Other languages (Go, .NET, …)",
        "kind": "language",
        "parent": "packages",
        "agent": "other-codebase-walker",
        "scan_domains": [],
        "weight": 2,
        "checklist": _checklist(
            [
                ("inventory", "List Go / .NET / Ruby / PHP / Swift / Elixir manifests that are present"),
                ("modules", "Map modules vs deployable services for those ecosystems"),
                ("enrich", "Enrich Package/Service purpose (do not re-run sac_scan_packages)"),
            ]
        ),
    },
    "iac-terraform": {
        "title": "Terraform",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "terraform-reverse-engineer",
        "scan_domains": [],
        "weight": 4,
        "checklist": _checklist(
            [
                ("modules", "Map root modules vs shared modules and Terragrunt if present"),
                ("providers", "Note providers, backends, and workspace/env split"),
                ("resources", "Record resource type counts (no full state dump)"),
                ("enrich", "Enrich InfrastructureStack purpose (do not re-run sac_scan_iac)"),
                ("link", "Join stacks to services they provision; leave VPC/LB/IAM topology to network-iam"),
            ]
        ),
    },
    "iac-cdk": {
        "title": "CDK",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "cdk-reverse-engineer",
        "scan_domains": [],
        "weight": 4,
        "checklist": _checklist(
            [
                ("apps", "Inventory CDK apps / stacks (cdk.json, cdk.context.json)"),
                ("languages", "Note CDK language (TypeScript / Python / Java / Go)"),
                ("enrich", "Enrich InfrastructureStack purpose (do not re-run sac_scan_iac)"),
                ("link", "Join CDK stacks to the services they provision"),
            ]
        ),
    },
    "iac-cloudformation": {
        "title": "CloudFormation",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "cloudformation-reverse-engineer",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("templates", "Inventory CFN templates (AWSTemplateFormatVersion)"),
                ("enrich", "Enrich InfrastructureStack purpose (do not re-run sac_scan_iac)"),
            ]
        ),
    },
    "iac-pulumi": {
        "title": "Pulumi",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "pulumi-reverse-engineer",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("stacks", "Inventory Pulumi.yaml projects and stacks"),
                ("enrich", "Enrich InfrastructureStack purpose (do not re-run sac_scan_iac)"),
            ]
        ),
    },
    "iac-helm": {
        "title": "Helm",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "helm-reverse-engineer",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("charts", "Inventory Chart.yaml charts and values files"),
                ("enrich", "Enrich HelmChart / InfrastructureStack purpose (do not re-run sac_scan_iac)"),
                ("link", "Join charts to the K8s workloads they render"),
            ]
        ),
    },
    "iac-kustomize": {
        "title": "Kustomize",
        "kind": "iac-tool",
        "parent": "iac",
        "agent": "kustomize-reverse-engineer",
        "scan_domains": [],
        "weight": 3,
        "checklist": _checklist(
            [
                ("overlays", "Inventory kustomization.yaml bases and overlays"),
                ("enrich", "Enrich InfrastructureStack purpose (do not re-run sac_scan_iac)"),
            ]
        ),
    },
}


def plan_paths(bundle: Path) -> dict[str, Path]:
    d = bundle / SAC_DIRNAME
    return {
        "dir": d,
        "json": d / PLAN_JSON_NAME,
        "md": d / PLAN_MD_NAME,
        "progress": d / PLAN_PROGRESS_NAME,
    }


def resolve_plan_files(plan_or_bundle: Path) -> dict[str, Path]:
    p = Path(plan_or_bundle)
    if p.is_file() and p.suffix == ".json":
        d = p.parent
        return {"dir": d, "json": p, "md": d / PLAN_MD_NAME, "progress": d / PLAN_PROGRESS_NAME}
    if p.is_dir() and (p / PLAN_JSON_NAME).is_file():
        return {
            "dir": p,
            "json": p / PLAN_JSON_NAME,
            "md": p / PLAN_MD_NAME,
            "progress": p / PLAN_PROGRESS_NAME,
        }
    return plan_paths(p)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _should_skip(name: str) -> bool:
    if name in DOT_WALK:
        return False
    if name in DEFAULT_IGNORE:
        return True
    if name.startswith(".git"):
        return True
    if name.startswith(".") and name not in DOT_WALK:
        return True
    return False


def bfs_walk(root: Path, *, max_depth: int = MAX_DEPTH, max_files: int = MAX_FILES) -> list[Path]:
    """Breadth-first file listing. Cheap presence scan, not a full repo dump."""
    root = root.resolve()
    out: list[Path] = []
    q: deque[tuple[Path, int]] = deque([(root, 0)])
    while q and len(out) < max_files:
        cur, depth = q.popleft()
        if depth > max_depth:
            continue
        try:
            entries = sorted(cur.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (OSError, PermissionError):
            continue
        child_dirs: list[Path] = []
        for p in entries:
            if _should_skip(p.name):
                continue
            if p.is_dir():
                child_dirs.append(p)
            elif p.is_file():
                out.append(p)
                if len(out) >= max_files:
                    break
        if depth < max_depth:
            for d in child_dirs:
                q.append((d, depth + 1))
    return out


def _peek(path: Path, limit: int = PEEK_BYTES) -> str:
    try:
        if path.stat().st_size > 1_000_000:
            return ""
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def _name_has_any(name: str, needles: tuple[str, ...]) -> bool:
    low = name.lower()
    return any(n in low for n in needles)


def _hit(kind: str, rel: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"kind": kind, "path": rel}
    if extra:
        row.update(extra)
    return row


def _k8s_kinds_in(text: str) -> list[str]:
    found: list[str] = []
    if "apiVersion:" not in text or "kind:" not in text:
        return found
    for kind in K8S_KINDS:
        if f"kind: {kind}" in text:
            found.append(kind)
    return found


def inspect_root(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = bfs_walk(root)
    top_level: list[str] = []
    try:
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if p.name in DEFAULT_IGNORE or p.name == ".git":
                continue
            if p.name.startswith(".") and p.name not in DOT_WALK:
                continue
            top_level.append(p.name + ("/" if p.is_dir() else ""))
    except OSError:
        pass

    major_dirs: list[str] = []
    seen_major: set[str] = set()
    hits: dict[str, list[dict[str, Any]]] = {k: [] for k in AREA_SPECS}
    specialist_hits: dict[str, list[dict[str, Any]]] = {k: [] for k in SPECIALIST_SPECS}
    ecosystems: set[str] = set()
    workspaces = False
    code_files = 0

    for f in files:
        rel = _rel(root, f)
        parts = Path(rel).parts
        name = f.name
        suffix = f.suffix.lower()

        for part in parts[:-1]:
            if part in MAJOR_DIR_NAMES and part not in seen_major:
                seen_major.add(part)
                major_dirs.append(part)

        eco = PACKAGE_FILES.get(name)
        if eco:
            extra: dict[str, Any] = {"ecosystem": eco}
            if name == "package.json":
                text = _peek(f)
                if '"workspaces"' in text:
                    workspaces = True
                    extra["workspaces"] = True
                if "aws-cdk" in text or "aws-cdk-lib" in text:
                    specialist_hits["iac-cdk"].append(_hit("cdk-dep", rel))
            ecosystems.add(eco)
            hits["packages"].append(_hit(eco, rel, extra))

        if name in JAVA_FILES:
            specialist_hits["lang-java"].append(_hit(JAVA_FILES[name], rel))
        if name in TS_FILES or (name.startswith("tsconfig") and name.endswith(".json")):
            kind = TS_FILES.get(name, "tsconfig")
            specialist_hits["lang-typescript"].append(_hit(kind, rel))
        if name in PYTHON_FILES:
            specialist_hits["lang-python"].append(_hit(PYTHON_FILES[name], rel))
        if name in RUST_FILES:
            specialist_hits["lang-rust"].append(_hit(RUST_FILES[name], rel))
        other_kind = OTHER_LANG_FILES.get(name) or OTHER_LANG_SUFFIXES.get(suffix)
        if other_kind:
            specialist_hits["lang-other"].append(_hit(other_kind, rel))

        if suffix == ".tf" or name in {"terragrunt.hcl", ".terraform.lock.hcl"}:
            specialist_hits["iac-terraform"].append(_hit("terraform", rel))
        if name in {"cdk.json", "cdk.context.json"}:
            specialist_hits["iac-cdk"].append(_hit("cdk", rel))
        if name in {"Pulumi.yaml", "Pulumi.yml"}:
            specialist_hits["iac-pulumi"].append(_hit("pulumi", rel))
        if name in {"Chart.yaml", "Chart.yml"}:
            specialist_hits["iac-helm"].append(_hit("helm", rel))
        if name in {"kustomization.yaml", "kustomization.yml"}:
            specialist_hits["iac-kustomize"].append(_hit("kustomize", rel))
        if suffix in {".yml", ".yaml", ".json", ".template"} and (
            "template" in name.lower() or name.lower().startswith("cfn")
        ):
            cfn_peek = _peek(f)
            if "AWSTemplateFormatVersion" in cfn_peek or '"AWSTemplateFormatVersion"' in cfn_peek:
                specialist_hits["iac-cloudformation"].append(_hit("cloudformation", rel))

        if name in CONTAINER_EXACT or name.upper().startswith("DOCKERFILE"):
            kind = CONTAINER_EXACT.get(name, "dockerfile")
            hits["containers"].append(_hit(kind, rel))

        if suffix == ".tf" or name in IAC_EXACT:
            tool = "terraform" if suffix == ".tf" else IAC_EXACT[name]
            hits["iac"].append(_hit(tool, rel, {"tool": tool}))

        cicd_plat = CICD_EXACT.get(name)
        if cicd_plat:
            hits["cicd"].append(_hit(cicd_plat, rel, {"platform": cicd_plat}))
        elif ".github" in parts and "workflows" in parts and suffix in {".yml", ".yaml"}:
            hits["cicd"].append(_hit("github-actions", rel, {"platform": "github-actions"}))
        elif ".circleci" in parts and suffix in {".yml", ".yaml"}:
            hits["cicd"].append(_hit("circleci", rel, {"platform": "circleci"}))
        elif ".tekton" in parts and suffix in {".yml", ".yaml"}:
            hits["cicd"].append(_hit("tekton", rel, {"platform": "tekton"}))

        if suffix in {".yml", ".yaml"}:
            dir_hint = any(p in K8S_DIR_HINTS for p in parts)
            peek = _peek(f) if dir_hint or name.lower().startswith(("deploy", "ingress", "svc", "service")) else ""
            if not peek and dir_hint:
                peek = _peek(f)
            if not peek and ("kind:" in name or dir_hint):
                peek = _peek(f)
            if dir_hint or peek:
                text = peek or _peek(f)
                kinds = _k8s_kinds_in(text)
                if kinds:
                    hits["k8s"].append(_hit("k8s", rel, {"kinds": kinds}))
                    if any(k in K8S_NETWORK_KINDS for k in kinds):
                        hits["network-iam"].append(
                            _hit("k8s-network", rel, {"kinds": [k for k in kinds if k in K8S_NETWORK_KINDS]})
                        )

        if suffix in DIAGRAM_SUFFIXES or name.lower() in {"structurizr.dsl", "workspace.dsl"}:
            hits["diagrams"].append(_hit(suffix.lstrip(".") or "dsl", rel))

        ident_name = _name_has_any(name, IDENTITY_NAME_NEEDLES)
        if ident_name or suffix in {".tf", ".env"} or name.endswith(".env.example"):
            text = _peek(f)
            if ident_name or any(n in text for n in IDENTITY_TEXT_NEEDLES):
                if any(n in text for n in IDENTITY_TEXT_NEEDLES) or ident_name:
                    provider = None
                    for needle, label in (
                        ("auth0", "auth0"),
                        ("AUTH0_", "auth0"),
                        ("cognito", "cognito"),
                        ("okta", "okta"),
                        ("keycloak", "keycloak"),
                        ("jsonwebtoken", "jwt"),
                        ("oidc", "oidc"),
                    ):
                        if needle.lower() in text.lower() or needle in text:
                            provider = label
                            break
                    hits["identity"].append(_hit(provider or "auth-marker", rel, {"provider": provider}))

        if suffix == ".tf" or _name_has_any(rel, NETWORK_NAME_NEEDLES):
            text = _peek(f)
            if any(n in text for n in NETWORK_TEXT_NEEDLES) or _name_has_any(rel, NETWORK_NAME_NEEDLES):
                hits["network-iam"].append(_hit("network-iam", rel))

        if suffix in CODE_SUFFIXES:
            code_files += 1

    if code_files or any(d in CODE_DIR_HINTS for d in seen_major):
        if code_files:
            hits["code"].append(_hit("source-files", f"{code_files} files", {"count": code_files}))
        for d in sorted(seen_major & CODE_DIR_HINTS):
            hits["code"].append(_hit("layout-dir", d + "/"))

    pkg_parents = {str(Path(h["path"]).parent) for h in hits["packages"]}
    if workspaces or len(pkg_parents) >= 2 or "services" in seen_major:
        layout = "monorepo"
    elif not hits["packages"] and (hits["iac"] or hits["k8s"]):
        layout = "infra"
    elif len(hits["packages"]) == 1:
        layout = "single-package"
    else:
        layout = "mixed"

    def _trim(groups: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
        trimmed: dict[str, list[dict[str, Any]]] = {}
        for key, rows in groups.items():
            seen: set[tuple[str, str]] = set()
            uniq: list[dict[str, Any]] = []
            for row in rows:
                k = (row.get("kind", ""), row.get("path", ""))
                if k in seen:
                    continue
                seen.add(k)
                uniq.append(row)
            trimmed[key] = uniq[:MAX_HITS]
        return trimmed

    return {
        "path": str(root),
        "name": root.name,
        "top_level": top_level,
        "major_dirs": major_dirs,
        "ecosystems": sorted(ecosystems),
        "layout": layout,
        "workspaces": workspaces,
        "hits": _trim(hits),
        "specialist_hits": _trim(specialist_hits),
        "file_count": len(files),
    }


def _signal_for(area_id: str, spec: dict[str, Any], rows: list[dict[str, Any]]) -> int:
    weight = int(spec["weight"])
    n = 0
    for row in rows:
        if area_id == "code" and row.get("kind") == "source-files":
            n += min(int(row.get("count") or 0), 8)
        else:
            n += 1
    return n * weight


def _combine_hits(inspected: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    combined: dict[str, list[dict[str, Any]]] = {}
    for info in inspected:
        for area_id, rows in (info.get(key) or {}).items():
            bucket = combined.setdefault(area_id, [])
            prefix = info["name"]
            for row in rows:
                item = dict(row)
                item["root"] = prefix
                bucket.append(item)
    return combined


def _area_entry(area_id: str, spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    signal = _signal_for(area_id, spec, rows)
    if signal <= 0:
        return None
    return {
        "id": area_id,
        "title": spec["title"],
        "kind": spec.get("kind") or "domain",
        "parent": spec.get("parent"),
        "signal": signal,
        "hit_count": len(rows),
        "agent": spec["agent"],
        "scan_domains": list(spec.get("scan_domains") or []),
        "hits": rows[:MAX_HITS],
        "checklist": _resolve_checklist(spec, rows),
        "spawn": True,
    }


def build_plan(roots: list[Path], *, system_name: str) -> dict[str, Any]:
    inspected = [inspect_root(Path(r)) for r in roots]
    combined = _combine_hits(inspected, "hits")
    combined_spec = _combine_hits(inspected, "specialist_hits")

    focus: list[dict[str, Any]] = []
    for area_id, spec in AREA_SPECS.items():
        entry = _area_entry(area_id, spec, combined.get(area_id) or [])
        if entry:
            focus.append(entry)
    for area_id, spec in SPECIALIST_SPECS.items():
        entry = _area_entry(area_id, spec, combined_spec.get(area_id) or [])
        if entry:
            focus.append(entry)
    focus.sort(key=lambda a: (-int(a["signal"]), a["id"]))
    for i, area in enumerate(focus, start=1):
        area["rank"] = i

    ecosystems: list[str] = []
    for info in inspected:
        for eco in info["ecosystems"]:
            if eco not in ecosystems:
                ecosystems.append(eco)

    slug = slugify(system_name)
    return {
        "version": PLAN_VERSION,
        "system": system_name,
        "system_slug": slug,
        "roots": [
            {
                "path": i["path"],
                "name": i["name"],
                "top_level": i["top_level"],
                "major_dirs": i["major_dirs"],
                "ecosystems": i["ecosystems"],
                "layout": i["layout"],
                "workspaces": i["workspaces"],
                "file_count": i["file_count"],
            }
            for i in inspected
        ],
        "ecosystems": ecosystems,
        "focus_areas": focus,
        "specialists": [
            {
                "id": a["id"],
                "kind": a.get("kind"),
                "parent": a.get("parent"),
                "agent": a.get("agent"),
                "title": a.get("title"),
                "signal": a.get("signal"),
                "hit_count": a.get("hit_count"),
            }
            for a in focus
            if a.get("kind") in ("language", "iac-tool")
        ],
        "artifacts": {
            "plan_json": f"{SAC_DIRNAME}/{PLAN_JSON_NAME}",
            "plan_md": f"{SAC_DIRNAME}/{PLAN_MD_NAME}",
            "progress": f"{SAC_DIRNAME}/{PLAN_PROGRESS_NAME}",
        },
    }


def empty_progress(plan: dict[str, Any]) -> dict[str, Any]:
    areas: dict[str, Any] = {}
    for area in plan.get("focus_areas") or []:
        areas[area["id"]] = {
            "items": {
                item["id"]: {"status": item.get("status") or "pending", "note": item.get("note") or ""}
                for item in area.get("checklist") or []
            }
        }
    return {"plan": plan.get("artifacts", {}).get("plan_json", f"{SAC_DIRNAME}/{PLAN_JSON_NAME}"), "areas": areas}


def apply_progress(plan: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    areas = progress.get("areas") or {}
    for area in plan.get("focus_areas") or []:
        rec = areas.get(area["id"]) or {}
        items = rec.get("items") or {}
        for item in area.get("checklist") or []:
            st = items.get(item["id"]) or {}
            if st.get("status"):
                item["status"] = st["status"]
            if "note" in st:
                item["note"] = st.get("note") or ""
    return plan


def checklist_summary(plan: dict[str, Any]) -> dict[str, int]:
    done = blocked = pending = total = 0
    for area in plan.get("focus_areas") or []:
        for item in area.get("checklist") or []:
            total += 1
            status = item.get("status") or "pending"
            if status == "done":
                done += 1
            elif status == "blocked":
                blocked += 1
            else:
                pending += 1
    return {"done": done, "blocked": blocked, "pending": pending, "total": total}


def scan_domains_from_plan(plan: dict[str, Any], *, area: str | None = None) -> list[str]:
    domains: list[str] = []
    for focus in plan.get("focus_areas") or []:
        if area and focus["id"] != area:
            continue
        for d in focus.get("scan_domains") or []:
            if d not in domains:
                domains.append(d)
    return domains


def render_plan_markdown(plan: dict[str, Any]) -> str:
    system = plan.get("system") or "System"
    lines: list[str] = [
        f"# Reverse-engineering plan: {system}",
        "",
        "Generated by `sac_plan.py` (deterministic; presence and counts only).",
        "Walkers populate the graph. Query-time `architecture-retriever` / `sac-retrieve` stay separate.",
        "",
        "## Repo map",
        "",
    ]
    for root in plan.get("roots") or []:
        lines.append(f"### `{root.get('name')}` (`{root.get('path')}`)")
        lines.append("")
        lines.append(f"- Layout: **{root.get('layout')}**")
        ecos = ", ".join(root.get("ecosystems") or []) or "_none detected_"
        lines.append(f"- Ecosystems: {ecos}")
        top = ", ".join(f"`{t}`" for t in (root.get("top_level") or []))
        if top:
            lines.append(f"- Top-level: {top}")
        majors = ", ".join(f"`{d}/`" for d in (root.get("major_dirs") or []))
        if majors:
            lines.append(f"- Major dirs: {majors}")
        lines.append(f"- Files visited (BFS cap): {root.get('file_count')}")
        lines.append("")

    def _table(areas: list[dict[str, Any]]) -> None:
        lines.extend(
            [
                "| Rank | Area | Signal | Hits | Agent | Scan domains |",
                "|------|------|--------|------|-------|--------------|",
            ]
        )
        for area in areas:
            domains = ", ".join(area.get("scan_domains") or []) or "enrichment only"
            lines.append(
                f"| {area.get('rank')} | `{area['id']}` — {area.get('title')} | "
                f"{area.get('signal')} | {area.get('hit_count')} | `{area.get('agent')}` | `{domains}` |"
            )
        lines.append("")

    domains_only = [a for a in (plan.get("focus_areas") or []) if a.get("kind", "domain") == "domain"]
    lang_specs = [a for a in (plan.get("focus_areas") or []) if a.get("kind") == "language"]
    iac_specs = [a for a in (plan.get("focus_areas") or []) if a.get("kind") == "iac-tool"]

    lines.extend(["## Focus areas (ranked by signal)", ""])
    _table(domains_only)

    lines.extend(
        [
            "## Language specialists (signal-gated)",
            "",
            "Spawn **only** when markers exist. Do not spawn Java without Gradle/Maven,",
            "or Python without pyproject/setup/requirements. Specialists enrich after",
            "`sac_scan_packages.py` — they do not replace it.",
            "",
        ]
    )
    if lang_specs:
        _table(lang_specs)
    else:
        lines.append("_None — no language specialist signals._")
        lines.append("")

    lines.extend(
        [
            "## IaC specialists (signal-gated)",
            "",
            "Spawn **only** when tool markers exist (no Terraform walker without `.tf`).",
            "K8s deploy / Service / LB stays on `k8s` + `network-iam`. Specialists enrich",
            "after `sac_scan_iac.py`.",
            "",
        ]
    )
    if iac_specs:
        _table(iac_specs)
    else:
        lines.append("_None — no IaC specialist signals._")
        lines.append("")

    lines.extend(
        [
            "## Suggested fan-out",
            "",
            "Parent reviews this plan, then **spawns one child per domain area and each listed specialist**.",
            "Independent domains run in parallel. Specialists start after the parent domain's",
            "deterministic capture (or read what the scanner already wrote).",
            "Do **not** re-run `full_scan` in every child. Retrievers are not walkers.",
            "",
            "```bash",
            "# Pause after plan",
            'python3 scripts/sac_orchestrate.py --plan-only --system "Name" --scan-root <repo>',
            "# Child: one area, domain-scoped scan + capture",
            "python3 scripts/sac_orchestrate.py --from-plan knowledge/.sac/re-plan.json --area packages \\",
            "  --system \"Name\" --scan-root <repo>",
            "# Or: scan + capture without repeating other domains",
            "python3 scripts/sac_scan.py --root <repo> --domains packages --json",
            'python3 scripts/sac_capture.py --repo . --root <repo> --system "Name" --domains packages',
            "python3 scripts/sac_plan.py mark --plan knowledge/.sac/re-plan.json --area packages \\",
            "  --item inventory --status done",
            "```",
            "",
            "## Deep-dive checklists",
            "",
        ]
    )
    for area in plan.get("focus_areas") or []:
        kind = area.get("kind") or "domain"
        lines.append(f"### `{area['id']}` — `{area.get('agent')}` ({kind})")
        lines.append("")
        lines.append(area.get("title") or area["id"])
        sample = ", ".join(f"`{h.get('path')}`" for h in (area.get("hits") or [])[:8] if h.get("path"))
        if sample:
            lines.append("")
            lines.append(f"Signals: {sample}")
        lines.append("")
        for item in area.get("checklist") or []:
            status = item.get("status") or "pending"
            box = "x" if status == "done" else " "
            note = item.get("note") or ""
            extra = ""
            if status == "blocked":
                extra = f" *(blocked{': ' + note if note else ''})*"
            elif note and status == "done":
                extra = f" *({note})*"
            lines.append(f"- [{box}] `{item['id']}` — {item['text']}{extra}")
        lines.append("")

    summary = checklist_summary(plan)
    lines.extend(
        [
            "## Checklist summary",
            "",
            f"- done: {summary['done']}",
            f"- blocked: {summary['blocked']}",
            f"- pending: {summary['pending']}",
            f"- total: {summary['total']}",
            "",
        ]
    )
    return "\n".join(lines)


def write_plan(
    bundle: Path,
    roots: list[Path],
    *,
    system_name: str,
    progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = Path(bundle)
    plan = build_plan(roots, system_name=system_name)
    if progress:
        apply_progress(plan, progress)
        prog = progress
    else:
        prog = empty_progress(plan)
    paths = plan_paths(bundle)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    paths["json"].write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    paths["md"].write_text(render_plan_markdown(plan), encoding="utf-8")
    paths["progress"].write_text(json.dumps(prog, indent=2) + "\n", encoding="utf-8")
    plan = dict(plan)
    plan["written"] = {k: str(v) for k, v in paths.items()}
    plan["checklist"] = checklist_summary(plan)
    return plan


def load_plan(plan_or_bundle: Path) -> dict[str, Any]:
    files = resolve_plan_files(plan_or_bundle)
    if not files["json"].is_file():
        raise FileNotFoundError(f"RE plan not found: {files['json']}")
    plan = json.loads(files["json"].read_text(encoding="utf-8"))
    if files["progress"].is_file():
        prog = json.loads(files["progress"].read_text(encoding="utf-8"))
        apply_progress(plan, prog)
    return plan


def mark_checklist(
    plan_or_bundle: Path,
    *,
    area: str,
    item: str,
    status: str,
    note: str = "",
) -> dict[str, Any]:
    if status not in {"pending", "done", "blocked"}:
        raise ValueError(f"status must be pending|done|blocked, got {status!r}")
    files = resolve_plan_files(plan_or_bundle)
    plan = load_plan(files["json"])
    focus_ids = {a["id"] for a in plan.get("focus_areas") or []}
    if area not in focus_ids:
        raise KeyError(f"area {area!r} is not in the plan ({sorted(focus_ids)})")
    item_ids = []
    for a in plan["focus_areas"]:
        if a["id"] == area:
            item_ids = [i["id"] for i in a.get("checklist") or []]
            break
    if item not in item_ids:
        raise KeyError(f"item {item!r} is not in area {area!r} ({item_ids})")
    if files["progress"].is_file():
        prog = json.loads(files["progress"].read_text(encoding="utf-8"))
    else:
        prog = empty_progress(plan)
    areas = prog.setdefault("areas", {})
    rec = areas.setdefault(area, {"items": {}})
    items = rec.setdefault("items", {})
    items[item] = {"status": status, "note": note}
    apply_progress(plan, prog)
    files["dir"].mkdir(parents=True, exist_ok=True)
    files["json"].write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    files["progress"].write_text(json.dumps(prog, indent=2) + "\n", encoding="utf-8")
    files["md"].write_text(render_plan_markdown(plan), encoding="utf-8")
    return {
        "area": area,
        "item": item,
        "status": status,
        "note": note,
        "checklist": checklist_summary(plan),
        "written": {k: str(v) for k, v in files.items()},
    }


def mark_area_item_if_present(
    plan_or_bundle: Path,
    *,
    area: str,
    item: str,
    status: str = "done",
    note: str = "",
) -> dict[str, Any] | None:
    try:
        return mark_checklist(plan_or_bundle, area=area, item=item, status=status, note=note)
    except (FileNotFoundError, KeyError):
        return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SAC breadth-first reverse-engineering plan")
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--repo", default=".", help="Knowledge host repo")
    p.add_argument("--bundle", default=None)
    p.add_argument("--system", default="System")
    p.add_argument("--scan-root", action="append", default=[], help="Repo root(s) to map")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write .sac/re-plan.{json,md} into the bundle")

    p_mark = sub.add_parser("mark", help="Check off (or block) a deep-dive checklist item")
    p_mark.add_argument("--plan", default=None, help="Plan JSON, .sac dir, or bundle")
    p_mark.add_argument("--repo", default=".")
    p_mark.add_argument("--bundle", default=None)
    p_mark.add_argument("--area", required=True)
    p_mark.add_argument("--item", required=True)
    p_mark.add_argument("--status", default="done", choices=("pending", "done", "blocked"))
    p_mark.add_argument("--note", default="")
    p_mark.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="Print an existing plan")
    p_show.add_argument("--plan", default=None)
    p_show.add_argument("--repo", default=".")
    p_show.add_argument("--bundle", default=None)
    p_show.add_argument("--json", action="store_true")

    args = p.parse_args(argv)
    from sac_common import resolve_knowledge_root

    if args.cmd == "mark":
        host = Path(args.repo).resolve()
        target = Path(args.plan).resolve() if args.plan else resolve_knowledge_root(host, args.bundle)
        result = mark_checklist(target, area=args.area, item=args.item, status=args.status, note=args.note)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"marked {args.area}/{args.item} -> {args.status}")
            print(f"checklist: {result['checklist']}")
        return 0

    if args.cmd == "show":
        host = Path(args.repo).resolve()
        target = Path(args.plan).resolve() if args.plan else resolve_knowledge_root(host, args.bundle)
        plan = load_plan(target)
        if args.json:
            print(json.dumps(plan, indent=2, default=str))
        else:
            print(render_plan_markdown(plan))
        return 0

    host = Path(args.repo).resolve()
    roots = [Path(r).resolve() for r in (args.scan_root or [str(host)])]
    if args.write:
        bundle = resolve_knowledge_root(host, args.bundle)
        bundle.mkdir(parents=True, exist_ok=True)
        plan = write_plan(bundle, roots, system_name=args.system)
    else:
        plan = build_plan(roots, system_name=args.system)
        plan["checklist"] = checklist_summary(plan)
    if args.json:
        print(json.dumps(plan, indent=2, default=str))
    else:
        print(render_plan_markdown(plan))
        if args.write:
            written = plan.get("written") or {}
            print(f"\nWrote {written.get('md')} and {written.get('json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
