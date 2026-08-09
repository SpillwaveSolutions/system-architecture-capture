---
type: SecurityGroup
title: sg-orders
description: Security group / network policy for order-service
tags: [sac, network, sg]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links: []
---

# sg-orders

Ingress: gateway + mesh only on 8080. Egress: Postgres, Kafka, payment-service.
