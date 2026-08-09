---
type: Service
title: Catalog Service
description: Product catalog read API and search index writer
tags: [sac, service, catalog]
status: active
truth_state: current
verified: true
language: typescript
runtime: kubernetes
timestamp: "2026-08-09T00:00:00Z"
links:
  - target: /packages/npm-order-client.md
    rel: related_to
---

# Catalog Service

Owns product master data. Reads from Postgres, writes search documents to OpenSearch.

## Related

- [Npm Order Client](/packages/npm-order-client.md) (`related_to`)
