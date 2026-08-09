#!/usr/bin/env python3
"""Discover SSO/OAuth providers and auth configuration patterns."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import slugify, walk_repo  # noqa: E402

PROVIDER_PATTERNS = [
    ("auth0", re.compile(r"(?i)\bauth0\b|AUTH0_DOMAIN|auth0\.com")),
    ("cognito", re.compile(r"(?i)\bcognito\b|COGNITO_|amazonaws\.com/oauth2|user-pool")),
    ("okta", re.compile(r"(?i)\bokta\b|OKTA_|okta\.com")),
    ("azure-ad", re.compile(r"(?i)\bazure[-_ ]?ad\b|AZURE_AD|login\.microsoftonline\.com|microsoft-identity")),
    ("keycloak", re.compile(r"(?i)\bkeycloak\b|KEYCLOAK_|/realms/")),
    ("google-oauth", re.compile(r"(?i)accounts\.google\.com|GOOGLE_CLIENT_ID|googleapis\.com/auth")),
    ("github-oauth", re.compile(r"(?i)github\.com/login/oauth|GITHUB_CLIENT_ID")),
    ("generic-oidc", re.compile(r"(?i)\bopenid[-_ ]?connect\b|\boidc\b|/\.well-known/openid-configuration")),
    ("saml", re.compile(r"(?i)\bsaml\b|SAML_")),
    ("jwt", re.compile(r"(?i)\bjwt\b|jsonwebtoken|jose\.|passport-jwt")),
]

IAM_PATTERNS = [
    ("iam-role", re.compile(r"(?i)AWS::IAM::Role|aws_iam_role|IamRole|iam\.Role")),
    ("iam-policy", re.compile(r"(?i)AWS::IAM::Policy|aws_iam_policy|IamPolicy|PolicyDocument")),
    ("service-account", re.compile(r"(?i)kind:\s*ServiceAccount|serviceAccountName")),
]


def scan_identity(root: Path) -> dict[str, Any]:
    providers: dict[str, dict[str, Any]] = {}
    iam: list[dict[str, Any]] = []
    text_exts = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".java", ".yml", ".yaml", ".json", ".tf", ".env", ".toml", ".properties", ".xml", ".gradle", ".kt"}
    for f in walk_repo(root):
        if f.suffix.lower() not in text_exts and f.name not in (".env.example", "Dockerfile"):
            continue
        try:
            if f.stat().st_size > 500_000:
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pname, pat in PROVIDER_PATTERNS:
            if pat.search(text):
                if pname not in providers:
                    providers[pname] = {
                        "name": pname,
                        "slug": slugify(f"idp-{pname}"),
                        "kind": "IdentityProvider",
                        "provider": pname,
                        "evidence": [],
                    }
                if len(providers[pname]["evidence"]) < 12:
                    providers[pname]["evidence"].append(str(f.relative_to(root)))
        for iname, pat in IAM_PATTERNS:
            if pat.search(text):
                iam.append({
                    "name": f"{iname}-{f.stem}",
                    "slug": slugify(f"{iname}-{f.stem}"),
                    "kind": "IamRole" if "role" in iname else "IamPolicy" if "policy" in iname else "ServiceAccount",
                    "path": str(f.relative_to(root)),
                    "pattern": iname,
                })
    # dedupe iam by path+pattern
    seen = set()
    iam_u = []
    for x in iam:
        k = (x["path"], x["pattern"])
        if k not in seen:
            seen.add(k)
            iam_u.append(x)
    return {
        "identity_providers": list(providers.values()),
        "iam": iam_u[:80],
        "count": len(providers) + len(iam_u),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scan identity/SSO/IAM")
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    data = scan_identity(Path(args.root).resolve())
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for pvd in data["identity_providers"]:
            print(f"idp  {pvd['provider']:16} evidence={len(pvd['evidence'])}")
        for i in data["iam"][:20]:
            print(f"iam  {i['pattern']:16} {i['path']}")
        print(f"\n{data['count']} identity/iam finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
