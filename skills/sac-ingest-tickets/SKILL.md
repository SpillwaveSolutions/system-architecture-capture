---
name: sac-ingest-tickets
description: Ingest Jira/Linear/Azure DevOps/GitHub Issues JSON exports into TicketLink and Feature concepts.
---

# SAC Ingest Tickets

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_ingest_tickets.py" tickets.json --repo .
```

## Provider access

Obtain content via environment skills/MCPs (or a manual export), then pass the
file/directory path to this script. SAC does not embed issues MCP or export auth.

