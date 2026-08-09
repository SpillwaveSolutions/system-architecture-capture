---
type: InfrastructureStack
title: "cloudformation: payments-secrets"
description: CFN stack for payment secrets + KMS
tags: [sac, iac, cloudformation]
tool: cloudformation
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /secrets/prod-secrets.md
    rel: provisions
---

# cloudformation: payments-secrets

KMS CMK + Secrets Manager entries for Stripe.

## Related

- [Prod Secrets](/secrets/prod-secrets.md) (`provisions`)
