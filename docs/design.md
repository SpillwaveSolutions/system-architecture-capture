# SAC Design

## Stack position

```
OKF (graph format, impact, pack, validate)
  ↑
PKC (meetings, experiments, decisions, WikiTicket materialize)
  ↑
SAC (this plugin — reverse-engineer runtime & infrastructure topology)
```

## Principles

1. **Deterministic scanners first** — agents add judgment, not path logic.
2. **Zero pip deps** — hand-rolled YAML like PKC.
3. **Cloud/stack agnostic concepts** with tool tags (`terraform`, `auth0`, …).
4. **Multi-host plugins** — Claude, Grok, Codex, OpenCode share one skill tree.
5. **Progressive disclosure** — packs default 2 hops for LLM precision.

## Module map

| Module | Role |
|--------|------|
| sac_common.py | catalogs, frontmatter, bundle IO |
| sac_scan_*.py | domain scanners |
| sac_scan.py | unified scan |
| sac_capture.py | scan → concepts |
| sac_orchestrate.py | multi-repo pipeline |
| sac_graph.py / sac_blast_radius.py | graph analytics |
| sac_pack.py / sac_search.py | query surfaces |
| sac_ingest_*.py | wiki + tickets |

## External connectivity (skills & MCPs)

SAC does **not** own deep provider SDKs or auth flows for Confluence, Notion,
Jira, Linear, Azure DevOps, GitHub Issues, Auth0 admin APIs, cloud control
planes, etc.

| Layer | Owns |
|-------|------|
| **Environment skills / MCPs** | Connect, auth, fetch/export from providers |
| **SAC** | Normalize exports → OKF concepts; scan *repo-local* artifacts; graph/query |

Ingest scripts accept **already-fetched** markdown/JSON (or whatever the MCP
writes to disk). Reverse-engineering of IdPs/IAM from *code and IaC evidence*
still runs in-repo scanners — live API admin of those providers is out of scope.

When an agent needs live data: call the host MCP/skill first, then pass the
export path into `sac_ingest_wiki.py` / `sac_ingest_tickets.py` / orchestrator
flags (`--wiki`, `--tickets`).

## OKF schema pack

Second-brain content is **not free-form**. Types and relations live in:

- `schemas/okf-concept-envelope.json` — required/optional frontmatter
- `schemas/types.json` — OKF + PKC + SAC type and relation registry
- `docs/okf-schemas.md` — human guide

`sac_validate.py --schema` enforces the pack. Prefer OKF-native types when they fit (`API`, `Metric`, `DecisionRecord`, `TicketLink`); use SAC types for topology.

## Design-time consumption

SAC is dual-mode:

1. **Build** the second brain (orchestrator + scanners + ingest).
2. **Use** it when designing new features, services, APIs, mobile/web apps, or infra
   via `sac-design-with` / `sac_pack` / `sac_blast_radius` / `sac_search`.

Design recommendations must cite existing concepts and edges; inventing a new
service without checking the graph is a process failure.

## Diagrams & code structure

The second brain stores **diagrams as Markdown concepts** with embedded Mermaid or
PlantUML listings (wireframes via PlantUML salt; architecture, component, sequence,
activity, state machine, class, ERD, deployment, C4, data-flow).

Source-level **Module / Class / Method / Function** concepts complement build-level
**Package** so design-time packs can reason about both deployables and code shape.

- Scan: `sac_scan_diagrams.py`, `sac_scan_code_structure.py`
- Capture: included in default orchestrate domains `diagrams` + `code`
- Skill: `sac-capture-diagrams`

