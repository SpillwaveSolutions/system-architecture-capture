---
type: C4Diagram
title: Northstar C4 context
description: C4Diagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: C4Diagram
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

# Northstar C4 context

**Kind:** C4Diagram  
**Format:** mermaid

## Diagram

```mermaid
flowchart TB
  Customer((Customer))
  System[Northstar Commerce]
  Payments[Payment Provider]
  IdP[Auth0]
  Customer --> System
  System --> Payments
  System --> IdP
```

## Related

- [System](/systems/northstar-commerce.md)
