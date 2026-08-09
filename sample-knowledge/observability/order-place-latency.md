---
type: Metric
title: order_place_latency_ms
description: p50/p99 place-order latency
tags: [sac, observability, metric]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: observed_by
---

# order_place_latency_ms

SLO: p99 < 300ms over 30d. Alert at burn rate 2x.

## Related

- [Order Service](/services/order-service.md) (`observed_by`)
