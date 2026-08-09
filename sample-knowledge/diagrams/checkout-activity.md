---
type: ActivityDiagram
title: Checkout activity
description: ActivityDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: ActivityDiagram
status: active
verified: true
truth_state: current
links:
  - target: /systems/northstar-commerce.md
    rel: visualizes
  - target: /clients/storefront-web.md
    rel: related_to
timestamp: "2026-08-09T12:20:27Z"
---

# Checkout activity

**Kind:** ActivityDiagram  
**Format:** mermaid

## Diagram

```mermaid
flowchart TD
  A[Browse catalog] --> B[Add to cart]
  B --> C[Start checkout]
  C --> D{Payment ok?}
  D -->|yes| E[Place order]
  D -->|no| F[Show error]
  E --> G[Emit OrderPlaced]
```

## Related

- [System](/systems/northstar-commerce.md)
