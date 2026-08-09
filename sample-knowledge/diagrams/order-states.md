---
type: StateMachineDiagram
title: Order state machine
description: StateMachineDiagram for Northstar demo (mermaid)
tags: [diagram, mermaid, northstar]
diagram_format: mermaid
diagram_kind: StateMachineDiagram
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

# Order state machine

**Kind:** StateMachineDiagram  
**Format:** mermaid

## Diagram

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Placed: submit
  Placed --> Paid: payment_ok
  Placed --> Cancelled: cancel
  Paid --> Fulfilled: ship
  Fulfilled --> [*]
  Cancelled --> [*]
```

## Related

- [System](/systems/northstar-commerce.md)
