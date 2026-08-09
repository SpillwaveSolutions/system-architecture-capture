---
type: Service
title: Order Service
description: Order lifecycle orchestration; publishes domain events
tags: [sac, service, orders]
status: active
truth_state: current
verified: true
language: java
runtime: kubernetes
sla: p99 < 300ms place-order
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/cart-service.md
    rel: calls
  - target: /services/payment-service.md
    rel: calls
  - target: /apis/order-api.md
    rel: exposes_api
  - target: /datastores/orders-db.md
    rel: writes_to
  - target: /messaging/orders-bus.md
    rel: publishes_to
  - target: /packages/maven-order-service.md
    rel: depends_on_package
  - target: /containers/order-service-image.md
    rel: runs_in
  - target: /iam/order-service-role.md
    rel: secured_by
  - target: /networks/sg-orders.md
    rel: secured_by
  - target: /deployments/order-service-prod.md
    rel: deploys_to
  - target: /ownership/checkout-team.md
    rel: owned_by
  - target: /meshes/istio-mesh.md
    rel: secured_by
---

# Order Service

Coordinates checkout: validates cart, reserves inventory, requests payment, emits `OrderPlaced`.

## Blast radius note

Downstream of payment + notify; upstream of cart and gateway.

## Related

- [Cart Service](/services/cart-service.md) (`calls`)
- [Payment Service](/services/payment-service.md) (`calls`)
- [Order Api](/apis/order-api.md) (`exposes_api`)
- [Orders Db](/datastores/orders-db.md) (`writes_to`)
- [Orders Bus](/messaging/orders-bus.md) (`publishes_to`)
- [Maven Order Service](/packages/maven-order-service.md) (`depends_on_package`)
- [Order Service Image](/containers/order-service-image.md) (`runs_in`)
- [Order Service Role](/iam/order-service-role.md) (`secured_by`)
- [Sg Orders](/networks/sg-orders.md) (`secured_by`)
- [Order Service Prod](/deployments/order-service-prod.md) (`deploys_to`)
- [Checkout Team](/ownership/checkout-team.md) (`owned_by`)
- [Istio Mesh](/meshes/istio-mesh.md) (`secured_by`)
