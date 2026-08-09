---
type: ApiContract
title: Order Service API
description: Internal gRPC/REST order API
tags: [sac, api, internal]
status: active
truth_state: current
verified: true
protocol: grpc+rest
timestamp: "2026-08-09T00:00:00Z"
links: []
---

# Order Service API

- `POST /orders` — place order
- `GET /orders/{id}` — fetch
- `POST /orders/{id}/cancel` — cancel
