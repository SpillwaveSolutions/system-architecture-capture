---
type: DecisionRecord
title: Use event-driven checkout
description: Orders publish domain events rather than sync notify calls
tags: [sac, decision, adr]
status: accepted
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: decides
  - target: /services/notify-worker.md
    rel: decides
---

# Use event-driven checkout

## Context

Synchronous email/SMS in the order request path caused p99 regressions.

## Decision

Publish Kafka events; notify-worker is eventually consistent.

## Consequences

- Better isolation and retries
- Need idempotent consumers
- Slight delay before confirmation email

## Related

- [Order Service](/services/order-service.md) (`decides`)
- [Notify Worker](/services/notify-worker.md) (`decides`)
