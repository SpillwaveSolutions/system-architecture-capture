---
type: Vpc
title: Production VPC
description: Primary production network
tags: [sac, network, vpc]
cidr: 10.20.0.0/16
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /networks/prod-private-a.md
    rel: contains
  - target: /networks/prod-alb.md
    rel: contains
  - target: /networks/sg-orders.md
    rel: contains
---

# Production VPC

- Public subnets: ALB
- Private subnets: EKS/GKE/AKS workloads
- Data subnets: RDS/Redis

## Related

- [Prod Private A](/networks/prod-private-a.md) (`contains`)
- [Prod Alb](/networks/prod-alb.md) (`contains`)
- [Sg Orders](/networks/sg-orders.md) (`contains`)
