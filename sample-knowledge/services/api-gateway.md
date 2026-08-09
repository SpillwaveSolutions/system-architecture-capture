---
type: Service
title: API Gateway
description: Edge gateway (Kong/Envoy) terminating TLS and routing to internal services
tags: [sac, service, edge]
status: active
truth_state: current
verified: true
language: lua/go
runtime: kubernetes
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /apis/api-gateway.md
    rel: exposes_api
  - target: /services/catalog-service.md
    rel: calls
  - target: /services/cart-service.md
    rel: calls
  - target: /services/order-service.md
    rel: calls
  - target: /identity/auth0.md
    rel: authenticates_via
  - target: /identity/gateway-jwt.md
    rel: authorizes_with
  - target: /meshes/istio-mesh.md
    rel: secured_by
---

# API Gateway

Routes `/v1/*` to internal services. Integrates with Auth0 JWT validation.

## Contracts

Exposes the public OpenAPI surface aggregated from downstream services.

## Related

- [Api Gateway](/apis/api-gateway.md) (`exposes_api`)
- [Catalog Service](/services/catalog-service.md) (`calls`)
- [Cart Service](/services/cart-service.md) (`calls`)
- [Order Service](/services/order-service.md) (`calls`)
- [Auth0](/identity/auth0.md) (`authenticates_via`)
- [Gateway Jwt](/identity/gateway-jwt.md) (`authorizes_with`)
- [Istio Mesh](/meshes/istio-mesh.md) (`secured_by`)
