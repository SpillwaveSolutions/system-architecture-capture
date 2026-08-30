---
name: sac-pack
description: Build progressive disclosure context packs (default 2-hop) for precise LLM queries over architecture knowledge.
---

# SAC Pack

Walks outbound `links[]` from the seed plus inbound/backlinks (files that
point at it). Inbound uses ripgrep when `rg` is on PATH; otherwise a full
scan. Same graph either way. `--no-rg` forces the scan.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --hops 2
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --tiny
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --mermaid
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --no-rg --json
```
