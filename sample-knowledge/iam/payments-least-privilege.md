---
type: IamPolicy
title: payments-least-privilege
description: Payment service IAM policy
tags: [sac, iam, pci]
status: active
truth_state: current
verified: true
timestamp: "2026-08-09T00:00:00Z"
links: []
---

# payments-least-privilege

Deny: raw secret list. Allow: specific Stripe secret ARN, KMS decrypt for that secret only.
