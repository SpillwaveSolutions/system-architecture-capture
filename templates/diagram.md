---
type: Diagram
title: Example diagram
description: Architecture or design diagram (Mermaid or PlantUML listing).
tags: [diagram]
diagram_format: mermaid
diagram_kind: ArchitectureDiagram
timestamp: 2026-08-09T00:00:00Z
status: active
verified: false
truth_state: current
links: []
---

# Example diagram

## Diagram

```mermaid
flowchart LR
  Client --> API
  API --> Service
  Service --> DB[(Database)]
```

## Notes

- Prefer specific types: Wireframe, ArchitectureDiagram, ComponentDiagram, SequenceDiagram, ActivityDiagram, StateMachineDiagram, ClassDiagram, ErdDiagram, DeploymentDiagram, C4Diagram.
- Keep listings inside fenced code blocks so the second brain stays portable Markdown.
