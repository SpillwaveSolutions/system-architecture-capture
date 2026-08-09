---
name: sac-blast-radius
description: Compute and optionally write blast-radius analysis for a service or concept through the SAC graph.
---

# SAC Blast Radius

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_blast_radius.py" \
  services/order-service.md --repo . --hops 3 --write --json
```
