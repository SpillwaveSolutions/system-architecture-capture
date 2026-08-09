---
type: Service
title: Cart Service
description: Session shopping carts backed by Redis
tags: [sac, service, cart]
status: active
truth_state: current
verified: true
language: go
runtime: kubernetes
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/catalog-service.md
    rel: calls
  - target: /datastores/cart-redis.md
    rel: reads_from
  - target: /datastores/cart-redis.md
    rel: writes_to
  - target: /packages/go-cart-service.md
    rel: depends_on_package
---

# Cart Service

Ephemeral carts with 7-day TTL in Redis. Calls catalog for price validation.

## Related

- [Catalog Service](/services/catalog-service.md) (`calls`)
- [Cart Redis](/datastores/cart-redis.md) (`reads_from`)
- [Go Cart Service](/packages/go-cart-service.md) (`depends_on_package`)
