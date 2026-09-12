---
name: sac-plan
description: Breadth-first reverse-engineering plan — map monorepo/multi-repo roots, rank focus areas, emit deep-dive checklists. Pause here before spawning area walkers. Not query-time retrieve.
---

# SAC Plan

Cheap, deterministic map of what is *present* in each `--scan-root` (top-level + known markers). Presence and counts only — not a full scan and not `architecture-retriever`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" \
  --repo . --system "$SYSTEM_NAME" --scan-root "$REPO_ROOT" --write --json

python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" \
  --repo . --system "$SYSTEM_NAME" --scan-root "$REPO_ROOT" --plan-only --json
```

Writes `knowledge/.sac/re-plan.md` + `.json` (repo map, ranked areas, unchecked checklists, suggested sub-agents).

Mark progress after an area walker finishes an item:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" mark \
  --plan knowledge/.sac/re-plan.json --area iac --item capture --status done

python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" mark \
  --plan knowledge/.sac/re-plan.json --area identity --item jwt --status blocked \
  --note "token config is generated; no static evidence"
```

Then fan out with skill `sac-reverse-engineer` / `--from-plan --area <id>`.
