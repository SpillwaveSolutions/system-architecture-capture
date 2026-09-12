---
name: sac-reverse-engineer
description: End-to-end reverse-engineer one or more git repositories into a SAC architecture knowledge graph (packages, services, IaC, CI/CD, IAM, identity, topology). Plan breadth-first, then fan out area walkers. Primary entry skill for SAC.
---

# SAC Reverse Engineer

Populate **the second brain for system architecture information** on the given monorepo or multi-repo set: map the estate first, prioritize focus areas, walk code/IaC with matching sub-agents, materialize concepts using the **standard OKF schema pack** (`schemas/types.json`), wire relationships, validate with `--schema`, and leave a queryable knowledge bundle.

This is **capture-time**. Do not conflate it with query-time `architecture-retriever` / `sac-retrieve`. Walkers populate the graph. Retrievers stay separate.

## Connectivity

Provider login/API details come from host **skills and MCPs** — not from SAC.
Fetch wiki/tickets/live cloud inventory via those tools first; SAC normalizes
paths you pass in. In-repo scanners need only filesystem access to git roots.

## Process

1. Confirm repo roots (local paths or clones of URLs) and system name.
2. Optional: wiki export dir, tickets JSON.
3. **Init** the knowledge bundle if needed.
4. **Plan (breadth-first)** — map layout, ecosystems, and which domains are present. Do not start with a full scan.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" \
  --repo . \
  --system "$SYSTEM_NAME" \
  --scan-root "$REPO_ROOT" \
  --plan-only \
  --json
```

Or:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" \
  --repo . --system "$SYSTEM_NAME" --scan-root "$REPO_ROOT" --write --json
```

Artifacts (operational, not OKF concepts):

- `knowledge/.sac/re-plan.md` — repo map, ranked task list, unchecked deep-dive checklists
- `knowledge/.sac/re-plan.json` — same, machine-readable
- `knowledge/.sac/re-plan-progress.json` — checklist status

5. **Review the plan**, then **spawn from the assignment tables**: one child per domain area **and** one child per listed language/IaC specialist. Signal-gated — do not spawn Java (Gradle / Maven) unless Gradle or Maven markers exist (both first-class; mixed repos cover both), or Terraform without `.tf`. Independent domains in parallel; specialists enrich after the deterministic scan for that ecosystem. Pass that area’s checklist and `scan_domains`.
6. Each child runs a **domain-scoped** scanner + capture (scripts own writes) and marks checklist items:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" \
  --repo . --system "$SYSTEM_NAME" --scan-root "$REPO_ROOT" \
  --from-plan knowledge/.sac/re-plan.json --area packages --json

# equivalent scoped pair
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan.py" --root "$REPO_ROOT" --domains packages --json
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_capture.py" \
  --repo . --root "$REPO_ROOT" --system "$SYSTEM_NAME" --domains packages
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" mark \
  --plan knowledge/.sac/re-plan.json --area packages --item capture --status done
```

Do **not** re-run `full_scan` in every child if the plan already scoped domains. Language/IaC specialists (`--area lang-java`, `iac-terraform`, …) are enrichment-only — they do not re-scan.

7. After children return, **graph-builder** (or orchestrate without `--plan-only`) joins Package/Service ↔ Deployment ↔ LB ↔ Pipeline where evidence exists.
8. Optional wiki/ticket ingest. Blast radius on critical services.
9. Validate + doctor + report checklist completion:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_validate.py" --repo . --schema
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_doctor.py" --repo .
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_plan.py" show --plan knowledge/.sac/re-plan.json
```

Unattended (plan + scoped capture of every detected domain + graph):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" \
  --repo . \
  --system "$SYSTEM_NAME" \
  --scan-root "$REPO_ROOT" \
  --json
```

Default scan domains include `diagrams` (Mermaid/PlantUML) and `code` (Module/Class/Method/Function) **when the plan detects them**.
