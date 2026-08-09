---
type: FeatureFlag
title: checkout-v2
description: Gradual rollout of checkout redesign
tags: [sac, feature-flag]
provider: launchdarkly
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /services/order-service.md
    rel: flagged_by
---

# checkout-v2

25% prod traffic. Targets order-service + cart-service.

## Related

- [Order Service](/services/order-service.md) (`flagged_by`)
