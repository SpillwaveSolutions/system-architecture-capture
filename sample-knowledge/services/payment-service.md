---
type: Service
title: Payment Service
description: Payment authorization and capture via Stripe; PCI-scoped
tags: [sac, service, payments, pci]
status: active
truth_state: current
verified: true
language: kotlin
runtime: kubernetes
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /apis/payment-api.md
    rel: exposes_api
  - target: /iam/payments-least-privilege.md
    rel: secured_by
  - target: /secrets/prod-secrets.md
    rel: uses
  - target: /messaging/orders-bus.md
    rel: publishes_to
---

# Payment Service

Never stores PAN. Tokenized cards via Stripe. Emits `PaymentCaptured` / `PaymentFailed`.

## Related

- [Payment Api](/apis/payment-api.md) (`exposes_api`)
- [Payments Least Privilege](/iam/payments-least-privilege.md) (`secured_by`)
- [Prod Secrets](/secrets/prod-secrets.md) (`uses`)
- [Orders Bus](/messaging/orders-bus.md) (`publishes_to`)
