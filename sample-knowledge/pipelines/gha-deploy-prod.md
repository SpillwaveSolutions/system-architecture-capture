---
type: Pipeline
title: GitHub Actions deploy-prod
description: Build, scan, deploy to prod via Helm
tags: [sac, cicd, github-actions]
platform: github-actions
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /deployments/order-service-prod.md
    rel: builds
---

# GitHub Actions deploy-prod

Jobs: `test` → `build-image` → `security-scan` → `helm-deploy` (environment: prod, required reviewers).

## Related

- [Order Service Prod](/deployments/order-service-prod.md) (`builds`)
