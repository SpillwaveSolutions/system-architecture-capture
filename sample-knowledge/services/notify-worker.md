---
type: Service
title: Notify Worker
description: Serverless-style worker consuming order events and sending email/SMS
tags: [sac, service, notifications, serverless]
status: active
truth_state: current
verified: true
language: python
runtime: lambda
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /messaging/orders-bus.md
    rel: subscribes_to
  - target: /serverless/notify-worker-fn.md
    rel: runs_in
---

# Notify Worker

Lambda (or Cloud Function) subscribed to order/payment topics. Templates in SES/SendGrid.

## Related

- [Orders Bus](/messaging/orders-bus.md) (`subscribes_to`)
- [Notify Worker Fn](/serverless/notify-worker-fn.md) (`runs_in`)
