---
type: Wireframe
title: Checkout wireframe
description: Wireframe for Northstar demo (plantuml)
tags: [diagram, plantuml, northstar]
diagram_format: plantuml
diagram_kind: Wireframe
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

# Checkout wireframe

**Kind:** Wireframe  
**Format:** plantuml

## Diagram

```plantuml
@startuml
salt
{
  Checkout
  . | Cart summary
  {^"Email" | "customer@example.com" }
  {^"Card" | "**** **** **** 4242" }
  [Back] | [Pay now]
}
@enduml
```

## Related

- [System](/systems/northstar-commerce.md)
