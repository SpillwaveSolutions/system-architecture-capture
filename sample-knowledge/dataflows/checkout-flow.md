---
type: DataFlow
title: Checkout data flow
description: Client → gateway → cart/order/payment → events → notify
tags: [sac, dataflow]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: flows_to
---

# Checkout data flow

1. Client submits cart checkout
2. Gateway authn via Auth0 JWT
3. Order service reads cart (Redis), writes order (Postgres)
4. Payment service authorizes Stripe
5. Order emits Kafka events
6. Notify worker sends email

## Related

- [Order Service](/services/order-service.md) (`flows_to`)
