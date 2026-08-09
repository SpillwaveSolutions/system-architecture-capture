---
name: sac-reverse-engineer
description: End-to-end reverse-engineer one or more git repositories into a SAC architecture knowledge graph (packages, services, IaC, CI/CD, IAM, identity, topology). Primary entry skill for SAC.
---

# SAC Reverse Engineer

Populate **the second brain for system architecture information** on the given monorepo or multi-repo set: walk code/IaC, materialize concepts using the **standard OKF schema pack** (`schemas/types.json`), wire relationships, validate with `--schema`, and leave a queryable knowledge bundle.

## Connectivity

Provider login/API details come from host **skills and MCPs** — not from SAC.
Fetch wiki/tickets/live cloud inventory via those tools first; SAC normalizes
paths you pass in. In-repo scanners need only filesystem access to git roots.

## Process

1. Confirm repo roots (local paths or clones of URLs) and system name.
2. Optional: wiki export dir, tickets JSON.
3. Run orchestrator:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" \
  --repo . \
  --system "$SYSTEM_NAME" \
  --scan-root "$REPO_ROOT" \
  --json
```

4. Delegate enrichment to sub-agents for purpose/SLA/ownership and API contracts.
5. Run blast radius on critical services.
6. Validate:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_validate.py" --repo . --schema
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_doctor.py" --repo .
```

7. Report topology summary + knowledge paths.

Default scan domains include `diagrams` (Mermaid/PlantUML) and `code` (Module/Class/Method/Function).
