# Standard OKF Schemas for the Project Second Brain

SAC’s job is to build a **second brain** for monorepo / multi-repo **project information**, stored only as **standard OKF schemas** — portable Markdown concepts that [okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin) and [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture) already understand.

Machine registry: [`schemas/types.json`](../schemas/types.json) · envelope: [`schemas/okf-concept-envelope.json`](../schemas/okf-concept-envelope.json)

## Universal concept envelope (every file)

| Field | Required | Notes |
|-------|----------|--------|
| `type` | **yes** | From type registry |
| `title` | **yes** | Human name |
| `description` | recommended | One-line summary |
| `timestamp` | recommended | ISO-8601 |
| `tags` | optional | Free tags |
| `status` | optional | `active` / `draft` / … |
| `verified` | optional | Trust flag |
| `truth_state` | optional | `current` / `snapshot` / `superseded` / `archived` |
| `generated` | optional | Agent/scanner authored |
| `sources` | optional | Provenance paths/URLs |
| `owners` | optional | Team tags |
| `links[]` | optional | `{target, rel}` typed edges |

Body must include absolute Markdown links for humans; `links[].rel` enriches the same targets.

## Schema layers

### OKF core (okf-plugin)

`Catalog` · `ContextPack` · envelope `BaseConcept`

### PKC project memory

`Meeting` · `Experiment` · `Discovery` · `Assumption` · `Question` · `Feature` · `Requirement` · `Specification` · `Design` · `Release` · `CodeChange` · `Package` · `Risk` · `Acceptance` · `DecisionRecord` · `TicketLink` · `Epic` · `Story` · `Task` · `Subtask` · `Bug` · `Branch` · `Project` · `Playbook` · `Runbook` · `Reference`

### AGER agent / harness graph

`AgentNode` · `Workflow` · `Harness` · `SharedState` · `ToolCapability` · loop/runtime/ops/eval types — see the AGER README.

### DEKC data plane

`Dataset` · `Table` · `View` · `Metric` · lakes, marts, streams, jobs, semantic layer, glossary — see the DEKC README.

### SAC architecture (second-brain system topology)

See [concept-types.md](./concept-types.md) — 139 types in `schemas/types.json` v1.4.0 (System, Service, Component, SoftwareContainer, ApiContract, diagrams/wireframes, IAM, network, …).
## Relations

**OKF:** `depends_on` · `routes_to` · `implements` · `documents` · `uses` · `owns` · `supersedes` · `related_to` · `tracks` · `maps_to`  

**PKC:** `decides` · `informs` · `satisfies` · `verified_by` · …  

**SAC:** `calls` · `exposes_api` · `deploys_to` · `secured_by` · `provisions` · `flows_to` · `impacts` · …  

Full lists: `schemas/types.json` → `relations` and [typed-edges.md](./typed-edges.md).

## Bundle root

```yaml
---
okf_version: "0.2"
title: Project Second Brain
description: Architecture + project knowledge for <system>
timestamp: 2026-08-09T00:00:00Z
tags: [sac, pkc, okf, second-brain]
---
```

## Validation

```bash
python3 scripts/sac_validate.py --bundle sample-knowledge --schema
python3 scripts/sac_validate.py --bundle knowledge --schema --json
```

`--schema` checks every concept against the envelope + registered types/relations.
