---
name: sac-link
description: Add typed architecture edges between SAC concepts (calls, exposes_api, deploys_to, secured_by, …).
---

# SAC Link

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_link.py" \
  services/order-service.md services/payment-service.md --rel calls --repo .
```

See `docs/typed-edges.md` for the full relation set.
