---
name: sac-capture-diagrams
description: >-
  Capture wireframes and architecture diagrams into the SAC second brain as OKF
  concepts with Mermaid or PlantUML listings embedded in Markdown. Covers
  wireframes (PlantUML salt), architecture, component, sequence, activity,
  state machine, class, ERD, deployment, C4, and data-flow diagrams. Also use
  when authoring Module/Class/Method/Function concepts.
---

# Capture diagrams into the architecture second brain

Diagrams live **inside** OKF concept Markdown as fenced `mermaid` or `plantuml` /
`puml` listings — portable, LLM-readable, and scannable.

## Types

| Type | Typical format |
|------|----------------|
| `Wireframe` | PlantUML `salt` |
| `ArchitectureDiagram` | Mermaid / PlantUML / C4 |
| `ComponentDiagram` | Mermaid / PlantUML |
| `SequenceDiagram` | Mermaid `sequenceDiagram` |
| `ActivityDiagram` | Mermaid flowchart / PlantUML activity |
| `StateMachineDiagram` | Mermaid `stateDiagram-v2` |
| `ClassDiagram` | Mermaid `classDiagram` |
| `ErdDiagram` | Mermaid `erDiagram` |
| `DeploymentDiagram` | PlantUML deployment |
| `DataFlowDiagram` | Mermaid flowchart |
| `C4Diagram` | PlantUML C4 / Mermaid |
| `Diagram` | Umbrella only when kind unknown |

## Process

1. **Discover existing diagrams** in the repo:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan_diagrams.py" --root . --json
```

2. **Materialize** via full capture (or orchestrate):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_orchestrate.py" --scan-root . --system "MySystem"
# domains include diagrams + code by default
```

3. **Author new design diagrams** (when designing features/apps):
   - Create concept under `diagrams/` using the right type.
   - Put the listing in a `## Diagram` section inside ```mermaid or ```plantuml fences.
   - Link with `visualizes` / `diagrams` / `wireframes` / `models` to Service, WebApp, ApiContract, Database, Class, etc.

4. **Code structure** (modules / classes / methods / functions):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan_code_structure.py" --root .
```

- `Package` = build unit (npm/maven/gradle/…)
- `Module` = source module / namespace inside a package
- `Class` / `Interface` / `Enum` / `Method` / `Function` = code-level concepts for design and blast radius

## Rules

1. Prefer **specific** diagram types over bare `Diagram`.
2. Always keep the diagram source **in the Markdown** (never only as a PNG link).
3. One primary listing per concept; extra variants can be additional sections.
4. After writing, link related topology and run `sac_validate.py --schema`.
5. For UI work, use PlantUML **salt** wireframes linked to `WebApp` / `MobileApp` / `Channel`.
