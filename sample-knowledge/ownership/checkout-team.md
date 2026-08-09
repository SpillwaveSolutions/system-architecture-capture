---
type: Ownership
title: checkout-team
description: Owns cart, order, payment services
tags: [sac, ownership]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: owns
  - target: /services/payment-service.md
    rel: owns
  - target: /services/cart-service.md
    rel: owns
---

# checkout-team

Owns cart-service, order-service, payment-service and related Helm charts.

## Related

- [Order Service](/services/order-service.md) (`owns`)
- [Payment Service](/services/payment-service.md) (`owns`)
- [Cart Service](/services/cart-service.md) (`owns`)
