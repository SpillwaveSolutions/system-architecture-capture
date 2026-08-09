---
name: sac-pack
description: Build progressive disclosure context packs (default 2-hop) for precise LLM queries over architecture knowledge.
---

# SAC Pack

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --hops 2
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --tiny
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_pack.py" services/order-service.md --repo . --mermaid
```
