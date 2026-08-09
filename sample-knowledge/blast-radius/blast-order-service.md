---
type: BlastRadius
title: Blast radius of order-service
description: Impact analysis if order-service is degraded
tags: [sac, blast-radius]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: impacts
---

# Blast radius of order-service

## Direct

- Public checkout API
- Payment capture sequencing
- Order events to notify-worker

## Indirect

- Cart abandonment metrics
- Support tools reading order state
- Feature flag checkout-v2

## Related

- [Order Service](/services/order-service.md) (`impacts`)
