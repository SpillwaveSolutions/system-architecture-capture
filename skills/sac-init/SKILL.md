---
name: sac-init
description: Scaffold a System Architecture Capture knowledge bundle with SAC + PKC catalogs for reverse-engineering systems into OKF. Use when starting architecture capture in a repo.
---

# SAC Init

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_common.py" init-bundle \
  --repo . --bundle knowledge --title "System Architecture Knowledge"
```

Optionally copy `.sac/config.example.yml` → `.sac/config.yml`.

Requires companions: **project-knowledge-capture** (PKC) and **okf-plugin** (OKF) for full graph tooling.
