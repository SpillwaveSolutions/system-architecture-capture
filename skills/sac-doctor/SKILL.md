---
name: sac-doctor
description: One-screen health check for SAC knowledge bundles (types, thin concepts, broken links).
---

# SAC Doctor

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_doctor.py" --repo . --json
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_validate.py" --repo . --schema --json
```
