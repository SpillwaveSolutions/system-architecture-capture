#!/usr/bin/env python3
"""Validate SAC knowledge bundle structure and links."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import DEFAULT_RELATIONS, iter_concepts, parse_frontmatter, resolve_knowledge_root  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "types.json"
ENVELOPE_REQUIRED = ("type", "title")


def load_schema_registry() -> dict:
    import json
    if SCHEMA_PATH.is_file():
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return {"types": [], "relations": {"all": list(DEFAULT_RELATIONS)}}


def validate_bundle(bundle: Path, *, schema: bool = False) -> dict:
    issues = []
    node_count = 0
    edge_count = 0
    paths = set()
    if not (bundle / "index.md").is_file():
        issues.append({"severity": "error", "kind": "missing_index", "message": "bundle missing index.md"})
    for p in iter_concepts(bundle):
        node_count += 1
        rel = "/" + str(p.relative_to(bundle)).replace("\\", "/")
        paths.add(rel)
        text = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if not fm.get("type"):
            issues.append({"severity": "error", "kind": "missing_type", "message": f"{rel} missing type", "path": rel})
        if not fm.get("title"):
            issues.append({"severity": "error", "kind": "missing_title", "message": f"{rel} missing title", "path": rel})
        if schema:
            reg = getattr(validate_bundle, "_registry", None)
            if reg is None:
                validate_bundle._registry = load_schema_registry()
                reg = validate_bundle._registry
            known_types = {t["type"] for t in reg.get("types") or []}
            known_rels = set((reg.get("relations") or {}).get("all") or DEFAULT_RELATIONS)
            ctype = fm.get("type")
            if ctype and known_types and ctype not in known_types and ctype != "Catalog":
                issues.append({
                    "severity": "warning",
                    "kind": "unknown_type",
                    "message": f"{rel} type {ctype!r} not in OKF schema pack",
                    "path": rel,
                })
            if not fm.get("description"):
                issues.append({
                    "severity": "info",
                    "kind": "missing_description",
                    "message": f"{rel} missing description (recommended envelope field)",
                    "path": rel,
                })
            if "verified" not in fm:
                issues.append({
                    "severity": "info",
                    "kind": "missing_verified",
                    "message": f"{rel} missing verified flag",
                    "path": rel,
                })
        for link in fm.get("links") or []:
            if not isinstance(link, dict):
                continue
            edge_count += 1
            tgt = link.get("target")
            reln = link.get("rel")
            if not tgt:
                issues.append({"severity": "error", "kind": "empty_target", "message": f"{rel} empty link target", "path": rel})
                continue
            allowed_rels = DEFAULT_RELATIONS
            if schema:
                reg = getattr(validate_bundle, "_registry", None) or load_schema_registry()
                allowed_rels = tuple((reg.get("relations") or {}).get("all") or DEFAULT_RELATIONS)
            if reln and reln not in allowed_rels:
                issues.append({"severity": "info", "kind": "unknown_rel", "message": f"{rel} unknown rel {reln}", "path": rel})
            tnorm = tgt if str(tgt).startswith("/") else "/" + str(tgt)
            target_file = bundle / tnorm.lstrip("/")
            if not target_file.is_file():
                issues.append({"severity": "warning", "kind": "broken_link", "message": f"{rel} -> {tnorm} missing", "path": rel})
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    return {
        "ok": errors == 0,
        "node_count": node_count,
        "edge_count": edge_count,
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate SAC bundle")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--schema", action="store_true", help="Validate against schemas/types.json OKF schema pack")
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    result = validate_bundle(bundle, schema=args.schema)
    if args.schema:
        result["schema_pack"] = str(SCHEMA_PATH)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Bundle: {bundle}")
        print(f"nodes={result['node_count']} edges={result['edge_count']} errors={result['errors']} warnings={result['warnings']}")
        for i in result["issues"][:40]:
            print(f"  [{i['severity']}] {i['kind']}: {i['message']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
