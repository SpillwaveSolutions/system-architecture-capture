---
type: ClassDiagram
title: Order domain class diagram
description: ClassDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: ClassDiagram
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

# Order domain class diagram

**Kind:** ClassDiagram  
**Format:** mermaid

## Diagram

```mermaid
classDiagram
  class Order {
    +id: UUID
    +status: Status
    +place()
  }
  class LineItem {
    +sku: string
    +qty: int
  }
  Order "1" *-- "many" LineItem
```

## Related

- [System](/systems/northstar-commerce.md)
