---
doc_type: guide
slug: noun-ownership-migration
title: Noun-ownership migration (SAC)
truth_state: current
---

# Noun-ownership migration (SAC 0.5.0)

Family runbook: [okf-plugin noun-ownership migration](https://github.com/SpillwaveSolutions/okf-plugin/blob/main/docs/user_guide/noun-ownership-migration.md).

SAC `schemas/types.json` **1.4.0** is architecture / runtime topology only. PKC, DEKC, AGER, and okf-plugin nouns were dropped from this pack’s registry. Existing files with those types are still valid in a **mixed** bundle when the owning plugin is installed.

## Upgrade

1. Install **okf-graph-eng v0.8.0**, **PKC v0.8.0**, and **SAC v0.5.0**. Add DEKC / AGER if the tree has those nouns.
2. Do not re-add `DecisionRecord`, `TicketLink`, `Runbook`, `AgentNode`, `Dataset`, `Catalog`, or `ContextPack` to `types.json`.
3. Validate:

```bash
python3 scripts/sac_validate.py --bundle knowledge --schema
python3 path/to/okf-plugin/scripts/okf-graph.py validate knowledge --strict
```

`--schema` checks SAC types. Mixed PKC/AGER files need those plugins on the schema merge path.

## Wiki ingest

`scripts/sac_ingest_wiki.py` still classifies:

| Hint | Emits |
|------|-------|
| ADR / decision record | `DecisionRecord` (PKC) |
| glossary / terminology | `GlossaryTerm` (SAC **and** DEKC name — here it is architecture glossary) |
| runbook / playbook / on-call | `Runbook` (PKC) |

That is a **write** into PKC-shaped files, not a SAC registry claim. Keep PKC installed or stop ingesting wiki runbooks/ADRs through SAC until classify is routed.

Do not expand SAC’s registry to own `Runbook` again.

## Dual-owned names

Same `type:` string, different meaning. Pick one per tree.

| Name | SAC meaning | Also in |
|------|-------------|---------|
| `Package` | Build package / module | PKC project-memory Package |
| `Dashboard` | Observability dashboard | DEKC analytics Dashboard |
| `DataLake` | Platform lake in the estate | DEKC medallion DataLake |
| `GlossaryTerm` | Architecture glossary | DEKC data-domain glossary |
| `RateLimit` | Gateway / config quota | AGER runtime RateLimit |

API surface is `ApiContract`, not a generic `API`. Diagrams and wireframes live here. A DEKC tree that still has `type: Diagram` / `Wireframe` should keep those types and keep SAC installed — or move the files into this pack’s catalog layout.

## What not to do

- Do not retype SAC `Service` / `System` / `Component` nodes.
- Do not treat isolated SAC `--schema` as a license to delete PKC files it does not list.
- Undeclared overlaps to watch later (not this cut): `Topic`, `Event`, `Channel`, `Product`, `Incident`, `Job`, `Actor`, `Person`.

## Done when

- `types.json` stays 1.4.0 architecture-only.
- Mixed-bundle `--strict` is green with PKC (and DEKC/AGER if present).
- Wiki ingest is either mixed-with-PKC or no longer emitting PKC nouns.
