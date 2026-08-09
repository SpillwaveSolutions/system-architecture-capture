---
type: ComponentDiagram
title: Order service components
description: ComponentDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: ComponentDiagram
status: active
verified: true
truth_state: current
links:
  - target: /systems/northstar-commerce.md
    rel: visualizes
  - target: /systems/northstar-commerce.md
    rel: part_of
timestamp: "2026-08-09T12:20:27Z"
---

# Order service components

**Kind:** ComponentDiagram  
**Format:** mermaid

## Diagram

```mermaid
flowchart LR
  API[Order API] --> App[Application]
  App --> Dom[Domain]
  Dom --> Ports[Ports]
  Ports --> PG[(Database)]
  Ports --> K[Kafka]
```

## Related

- [System](/systems/northstar-commerce.md)
