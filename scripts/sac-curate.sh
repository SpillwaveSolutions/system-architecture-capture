#!/usr/bin/env bash
# Post-edit light curation for SAC knowledge bundles.
#
# This script previously consisted of `exit 0` — the PostToolUse hook in
# hooks/hooks.json was registered and fired, and then did nothing. The comment
# said "silent no-op if no bundle nearby", which suggests the guard was intended
# to be conditional and the body never landed.
#
# Implemented here to match the sibling plugin: refresh only the catalog holding
# the edited file. Refreshing every catalog on each edit is a whole-file
# read-modify-write per catalog, which races on rapid edits and does far more
# work than the change requires.
#
# Never blocks an edit: every step is best-effort and the script always exits 0.
set -uo pipefail

ROOT="${CLAUDE_PLUGIN_ROOT:-.}"
SCRIPTS="$ROOT/scripts"

FILE="${CLAUDE_TOOL_FILE_PATH:-${1:-}}"
[ -n "$FILE" ] || exit 0
case "$FILE" in
  *.md) ;;
  *) exit 0 ;;
esac
[ -f "$FILE" ] || exit 0

# Walk up from the edited file looking for a bundle root (an index.md).
DIR="$(cd "$(dirname "$FILE")" 2>/dev/null && pwd)" || exit 0
CATALOG="$(basename "$DIR")"
BUNDLE="$(dirname "$DIR")"
[ -f "$BUNDLE/index.md" ] || exit 0

SAC_SCRIPTS="$SCRIPTS" python3 - "$BUNDLE" "$CATALOG" <<'PY' || true
import sys
from pathlib import Path

sys.path.insert(0, __import__("os").environ["SAC_SCRIPTS"])
try:
    from sac_common import CATALOGS, refresh_catalog_index
except Exception:
    sys.exit(0)

bundle, catalog = Path(sys.argv[1]), sys.argv[2]
# refresh_catalog_index already refuses undeclared catalogs; checking here too
# keeps the hook quiet rather than merely inert.
if catalog in CATALOGS and (bundle / catalog).is_dir():
    refresh_catalog_index(bundle, catalog)
    print(f"sac-curate: refreshed {catalog}/index.md")
PY

exit 0
