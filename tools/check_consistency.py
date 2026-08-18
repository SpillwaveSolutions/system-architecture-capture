#!/usr/bin/env python3
"""Packaging consistency guard. Zero pip deps (Rule 1).

Rule 5 says a version bump touches every manifest; Rule 4 says a new capability
joins the typecheck list. Both were being applied by hand, and both drifted:
`.opencode-plugin/plugin.json` missed three consecutive releases and the README
missed one. This asserts what those rules require, so CI catches the omission
instead of a later reader.

Version sites are DISCOVERED by glob, not hardcoded — a new host manifest is
covered the day it lands. A hardcoded list would drift exactly like the
checklist it replaces.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rel(path: str) -> str:
    return os.path.relpath(path, REPO)


def version_sites(errors: list[str]) -> list[tuple[str, str]]:
    """Every (label, version) pair SAC publishes. Order is stable for output."""
    files = sorted(glob.glob(os.path.join(REPO, ".*-plugin", "*.json")))
    files += [os.path.join(REPO, f) for f in ("marketplace.json", "package.json", "plugin.json")]
    sites: list[tuple[str, str]] = []
    for path in files:
        if not os.path.isfile(path):
            continue
        try:
            data = json.load(open(path, encoding="utf-8"))
        except json.JSONDecodeError as exc:
            # Name the file. A traceback in CI output makes the reader hunt.
            errors.append(f"{rel(path)}: invalid JSON ({exc})")
            continue
        if isinstance(data.get("version"), str):
            sites.append((f"{rel(path)}:.version", data["version"]))
        for i, plugin in enumerate(data.get("plugins", []) or []):
            if isinstance(plugin.get("version"), str):
                sites.append((f"{rel(path)}:.plugins[{i}].version", plugin["version"]))
    return sites


def readme_version() -> tuple[str, str | None]:
    path = os.path.join(REPO, "README.md")
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^\|\s*\*\*Version\*\*\s*\|\s*([^|\s]+)\s*\|", text, re.M)
    return "README.md:Version table", (m.group(1) if m else None)


def check_versions(errors: list[str]) -> None:
    expected = json.load(open(os.path.join(REPO, "package.json"), encoding="utf-8"))["version"]
    sites = version_sites(errors)
    label, found = readme_version()
    if found is None:
        errors.append(f"{label}: no version row found")
    else:
        sites.append((label, found))
    for site_label, value in sites:
        if value != expected:
            errors.append(f"{site_label}: {value} != {expected} (package.json)")
    print(f"  version parity: {len(sites)} sites at {expected}")


def check_typecheck_list(errors: list[str]) -> None:
    pkg = json.load(open(os.path.join(REPO, "package.json"), encoding="utf-8"))
    listed = set(re.findall(r"scripts/([A-Za-z_0-9]+\.py)", pkg["scripts"]["typecheck"]))
    actual = {os.path.basename(p) for p in glob.glob(os.path.join(REPO, "scripts", "*.py"))}
    for name in sorted(actual - listed):
        errors.append(f"package.json typecheck: scripts/{name} missing")
    for name in sorted(listed - actual):
        errors.append(f"package.json typecheck: scripts/{name} listed but absent")
    print(f"  typecheck list: {len(listed)} scripts")


def main() -> int:
    errors: list[str] = []
    print("SAC consistency")
    check_versions(errors)
    check_typecheck_list(errors)
    if errors:
        print("\nFAIL")
        for e in errors:
            print(f"  {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
