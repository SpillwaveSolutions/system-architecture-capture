---
name: sac-search
description: Full-text search over SAC architecture knowledge concepts.
---

# SAC Search

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_search.py" "kafka payment" --repo . --json
```

For parent topology questions, spawn `architecture-retriever` (`sac-retrieve`)
instead of running this in the parent. The child may call this with `--limit 5`.
