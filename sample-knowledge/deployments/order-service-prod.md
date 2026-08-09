---
type: Deployment
title: order-service prod deploy
description: Helm release order-service in prod
tags: [sac, deployment]
strategy: rolling
replicas: 6
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /environments/prod.md
    rel: deploys_to
---

# order-service prod deploy

Rolling update, maxUnavailable=1. HPA 6–20 on CPU 60%.

## Related

- [Prod](/environments/prod.md) (`deploys_to`)
