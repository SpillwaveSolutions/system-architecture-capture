---
type: SequenceDiagram
title: Place order sequence
description: SequenceDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: SequenceDiagram
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

# Place order sequence

**Kind:** SequenceDiagram  
**Format:** mermaid

## Diagram

```mermaid
sequenceDiagram
  participant Web as WebApp
  participant GW as ApiGateway
  participant Ord as OrderService
  participant Pay as PaymentService
  participant Bus as Topic
  Web->>GW: POST /orders
  GW->>Ord: createOrder
  Ord->>Pay: authorize
  Pay-->>Ord: ok
  Ord->>Bus: OrderPlaced
  Ord-->>GW: 201
  GW-->>Web: order id
```

## Related

- [System](/systems/northstar-commerce.md)
