---
type: ApiContract
title: Public API Gateway
description: OpenAPI 3 public surface for Northstar
tags: [sac, api, public]
status: active
truth_state: current
verified: true
protocol: https+json
auth: bearer-jwt
timestamp: "2026-08-09T00:00:00Z"
links: []
---

# Public API Gateway

## Selected endpoints

| Method | Path | Service |
|--------|------|---------|
| GET | /v1/products | catalog-service |
| GET/POST | /v1/carts/{id} | cart-service |
| POST | /v1/orders | order-service |
| POST | /v1/payments/intent | payment-service |
