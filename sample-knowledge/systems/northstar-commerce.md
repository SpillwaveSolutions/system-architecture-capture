---
type: System
title: Northstar Commerce
description: "Multi-region e-commerce platform: catalog, cart, orders, payments, notifications"
tags: [sac, system, commerce]
status: active
truth_state: current
verified: true
sla: "99.9% API availability"
owners: [platform-team]
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/api-gateway.md
    rel: contains
  - target: /services/catalog-service.md
    rel: contains
  - target: /services/cart-service.md
    rel: contains
  - target: /services/order-service.md
    rel: contains
  - target: /services/payment-service.md
    rel: contains
  - target: /services/notify-worker.md
    rel: contains
---

# Northstar Commerce

Cloud-agnostic commerce platform running as microservices on Kubernetes with serverless workers.

## Purpose

Accept browse/cart/checkout traffic, process payments, fulfill orders, and notify customers.

## Topology (logical)

```
Client → API Gateway → [Catalog | Cart | Order | Payment | Notify]
                              ↓           ↓         ↓
                           Postgres    Kafka    Stripe/SQS
```

## Environments

- dev, stage, prod (see environments catalog)

## Related

- [Api Gateway](/services/api-gateway.md) (`contains`)
- [Catalog Service](/services/catalog-service.md) (`contains`)
- [Cart Service](/services/cart-service.md) (`contains`)
- [Order Service](/services/order-service.md) (`contains`)
- [Payment Service](/services/payment-service.md) (`contains`)
- [Notify Worker](/services/notify-worker.md) (`contains`)
