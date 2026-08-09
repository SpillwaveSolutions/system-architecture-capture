---
type: InfrastructureStack
title: "terraform: network"
description: Terraform stack for VPC/subnets/SG/ALB
tags: [sac, iac, terraform]
tool: terraform
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /networks/prod-vpc.md
    rel: provisions
---

# terraform: network

Resources: aws_vpc, subnets, security groups, alb, waf.

## Related

- [Prod Vpc](/networks/prod-vpc.md) (`provisions`)
