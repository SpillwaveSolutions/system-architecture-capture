---
type: Pipeline
title: Argo CD app sync
description: GitOps continuous delivery for cluster apps
tags: [sac, cicd, argo-cd]
platform: argo-cd
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /deployments/order-service-prod.md
    rel: deploys_to
---

# Argo CD app sync

Watches `deploy/prod` path. Auto-sync with prune + self-heal for non-prod only.

## Related

- [Order Service Prod](/deployments/order-service-prod.md) (`deploys_to`)
