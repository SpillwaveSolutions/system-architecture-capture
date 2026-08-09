#!/usr/bin/env python3
"""Add typed edges between SAC concepts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sac_common import add_typed_link, concept_ref, resolve_knowledge_root  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Link SAC concepts")
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--rel", default="related_to")
    p.add_argument("--repo", default=".")
    p.add_argument("--bundle", default=None)
    args = p.parse_args(argv)
    bundle = resolve_knowledge_root(Path(args.repo).resolve(), args.bundle)
    src = concept_ref(args.source, "services")
    tgt = concept_ref(args.target, "services")
    path = bundle / src.lstrip("/")
    result = add_typed_link(path, tgt, args.rel)
    print(f"{result}: {src} -[{args.rel}]-> {tgt}")
    return 0 if result in ("created", "exists") else 1


if __name__ == "__main__":
    sys.exit(main())
