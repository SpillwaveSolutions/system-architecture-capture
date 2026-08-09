---
type: Database
title: Orders PostgreSQL
description: Primary relational store for orders and line items.
tags: [postgres, aws-rds, database]
engine: postgresql
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T11:07:21Z"
links:
  - target: /services/order-service.md
    rel: reads_from
  - target: /services/order-service.md
    rel: writes_to
  - target: /systems/northstar-commerce.md
    rel: part_of
---

# Orders PostgreSQL

Primary **Database** for order lifecycle.

## Related

- [Order Service](/services/order-service.md)
