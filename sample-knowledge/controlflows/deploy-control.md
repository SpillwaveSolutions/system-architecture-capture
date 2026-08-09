---
type: ControlFlow
title: Production deploy control flow
description: PR → CI → image → Argo sync → mesh rollout
tags: [sac, controlflow]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /pipelines/gha-deploy-prod.md
    rel: controls
---

# Production deploy control flow

GitHub Actions builds/scans → pushes image → updates Helm values PR → Argo CD sync → Istio rolling.

## Related

- [Gha Deploy Prod](/pipelines/gha-deploy-prod.md) (`controls`)
