---
name: sac-ingest-wiki
description: Ingest Confluence/Notion/wiki Markdown exports into ADRs, glossary terms, runbooks, and discoveries.
---

# SAC Ingest Wiki

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_ingest_wiki.py" path/to/export --repo .
```

## Provider access

Obtain content via environment skills/MCPs (or a manual export), then pass the
file/directory path to this script. SAC does not embed wiki/docs MCP or export auth.

