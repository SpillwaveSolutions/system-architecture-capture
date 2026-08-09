---
type: LoadBalancer
title: prod-alb
description: Public application load balancer
tags: [sac, network, lb]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/api-gateway.md
    rel: connects_to
---

# prod-alb

TLS 1.2+. Forwards to gateway pods. WAF attached.

## Related

- [Api Gateway](/services/api-gateway.md) (`connects_to`)
