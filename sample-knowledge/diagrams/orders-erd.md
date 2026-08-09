---
type: ErdDiagram
title: Orders ERD
description: ErdDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: ErdDiagram
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

# Orders ERD

**Kind:** ErdDiagram  
**Format:** mermaid

## Diagram

```mermaid
erDiagram
  ORDERS ||--o{ LINE_ITEMS : contains
  ORDERS {
    uuid id PK
    string status
  }
  LINE_ITEMS {
    uuid id PK
    uuid order_id FK
    string sku
    int qty
  }
```

## Related

- [System](/systems/northstar-commerce.md)
