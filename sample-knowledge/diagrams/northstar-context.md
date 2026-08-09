---
type: ArchitectureDiagram
title: Northstar context architecture
description: ArchitectureDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: ArchitectureDiagram
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

# Northstar context architecture

**Kind:** ArchitectureDiagram  
**Format:** mermaid

## Diagram

```mermaid
flowchart TB
  subgraph Clients
    Web[WebApp Storefront]
    iOS[MobileApp iOS]
  end
  GW[ApiGateway]
  Cat[Catalog Service]
  Ord[Order Service]
  Pay[Payment Service]
  DB[(Orders Database)]
  Cache[(Catalog Cache)]
  Bus{{Orders Topic}}
  Web --> GW
  iOS --> GW
  GW --> Cat
  GW --> Ord
  Ord --> Pay
  Ord --> DB
  Cat --> Cache
  Ord --> Bus
```

## Related

- [System](/systems/northstar-commerce.md)
