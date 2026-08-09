---
type: C4ContextDiagram
title: Northstar Commerce — C4 L1 Context
description: C4 level 1 context view
tags: [c4, c4-l1, diagram, generated]
diagram_format: mermaid
diagram_kind: C4ContextDiagram
c4_level: 1
status: active
truth_state: current
verified: false
generated: true
source: sac-c4
links:
  - target: /systems/northstar-commerce.md
    rel: c4_view_of
timestamp: "2026-08-09T12:27:08Z"
---

# Northstar Commerce — C4 L1 Context

**C4 level:** 1  
**Generated from:** SAC second brain inventory

## Diagram

```mermaid
flowchart TB
  %% C4 Level 1 — System Context
  customer(("Customer"))
  customer -->|uses| sys["Northstar Commerce"]
  sys["Northstar Commerce"]
  sys -->|uses| auth0["Auth0"]
  sys -->|uses| stripe["Stripe"]
```

## Notes

Auto-generated C4 view. Refine edges and technology tags manually; link with `c4_view_of` / `zooms_into`.
