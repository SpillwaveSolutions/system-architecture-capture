# C4 model integration

SAC’s architecture second brain aligns with the [C4 model](https://c4model.com/) so reverse-engineered systems and design-time work share one vocabulary.

## Mapping (abstractions)

| C4 | SAC concept(s) | Notes |
|----|----------------|-------|
| **Person** | `Person`, `Actor` | Human users / roles |
| **Software System** | `System` | Our boundary |
| **External System** | `ExternalSystem`, `Integration`, `IdentityProvider` | SaaS, banks, IdPs |
| **Container** | `SoftwareContainer`, plus runtime stand-ins: `Service`, `WebApp`, `MobileApp`, `Database`, `Cache`, `MessageQueue`, … | **Not** `ContainerImage` (Docker/OCI) |
| **Component** | `Component` | Inside a SoftwareContainer |
| **Code** | `Module`, `Class`, `Interface`, `Function`, `Method` | C4 level 4 |

### Naming collision (must remember)

| Term | Means in SAC |
|------|----------------|
| **C4 Container** | `SoftwareContainer` — app/service/DB that *runs* |
| **Container image** | `ContainerImage` — Dockerfile / OCI artifact |
| **C4 Component** | `Component` |
| **UML component diagram** | `ComponentDiagram` (generic) vs `C4ComponentDiagram` |

## Mapping (diagrams)

| C4 level | SAC diagram type |
|----------|------------------|
| L1 System Context | `C4ContextDiagram` |
| L2 Containers | `C4ContainerDiagram` |
| L3 Components | `C4ComponentDiagram` |
| L4 Code | `C4CodeDiagram` |
| Landscape | `SystemLandscapeDiagram` |
| Unspecified C4 | `C4Diagram` (umbrella) |

Listings: **Mermaid** (portable) or **PlantUML C4** / **Structurizr DSL**.

## Relations

| rel | Use |
|-----|-----|
| `c4_contains` | System → SoftwareContainer → Component |
| `c4_uses` | Person/System/Container dependency |
| `c4_view_of` | Diagram views a System/Container |
| `zooms_into` | L1 diagram → L2 diagram → L3 → L4 |
| `c4_implements` | Component → Module/Class |

## Workflows

### A. Generate C4 views from the second brain

After reverse-engineering (or from sample knowledge):

```bash
python3 scripts/sac_c4.py --bundle sample-knowledge --inventory
python3 scripts/sac_c4.py --bundle sample-knowledge --generate --system "Northstar Commerce"
python3 scripts/sac_c4.py --bundle sample-knowledge --dsl
```

Writes `C4ContextDiagram` / `C4ContainerDiagram` / `C4ComponentDiagram` / `C4CodeDiagram` concepts with Mermaid listings, plus a Structurizr `.dsl` export under `diagrams/`.

### B. Import Structurizr DSL

```bash
python3 scripts/sac_scan_structurizr.py --root . --json
# included in full scan domain `structurizr`
python3 scripts/sac_orchestrate.py --scan-root . --system MySystem
```

### C. Design with C4

When designing a new service/app:

1. Confirm **System** boundary (L1).
2. Place new capability as **SoftwareContainer** (L2) — not a random free-floating service without C4 home.
3. Optionally decompose into **Component**s (L3).
4. Link **Module/Class** (L4) when implementation starts.
5. Author/update C4 diagrams; use `zooms_into` between levels.

Skill: `sac-c4` · also referenced from `sac-capture-diagrams` and `sac-design-with`.

## What we deliberately do not do

- Full Structurizr server hosting (export DSL; render elsewhere).
- One concept type per AWS resource — C4 stays at container/component abstraction.
- Treating Docker as C4 Container.

## Schema

Machine mapping: `schemas/types.json` → `c4` key (levels + naming collisions).
