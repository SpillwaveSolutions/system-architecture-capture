---
type: C4ContainerDiagram
title: Northstar Commerce — C4 L2 Containers
description: C4 level 2 containers view
tags: [c4, c4-l2, diagram, generated]
diagram_format: mermaid
diagram_kind: C4ContainerDiagram
c4_level: 2
status: active
truth_state: current
verified: false
generated: true
source: sac-c4
links:
  - target: /systems/northstar-commerce.md
    rel: c4_view_of
timestamp: "2026-08-09T12:27:08Z"
---

# Northstar Commerce — C4 L2 Containers

**C4 level:** 2  
**Generated from:** SAC second brain inventory

## Diagram

```mermaid
flowchart TB
  %% C4 Level 2 — Containers inside Northstar Commerce
  subgraph system["Northstar Commerce"]
    catalog_redis_cache[("Catalog Redis cache")]
    storefront_ios["Storefront iOS"]
    storefront_web["Storefront Web"]
    storefront_web_container["Storefront Web Container"]
    cart_redis[("cart-redis")]
    orders_postgresql[("Orders PostgreSQL")]
    nightly_settlement_job["Nightly settlement job"]
    orders_bus{{orders-bus}}
    orders_events_topic{{Orders events topic}}
    product_search_index[("Product search index")]
    notify_worker_function["notify-worker function"]
    api_gateway["API Gateway"]
    cart_service["Cart Service"]
    catalog_service["Catalog Service"]
    notify_worker["Notify Worker"]
    order_service["Order Service"]
    payment_service["Payment Service"]
    receipts_object_store[("Receipts object store")]
  end
  storefront_web --> api_gateway
  storefront_ios --> api_gateway
  api_gateway --> orders_postgresql
  api_gateway --> catalog_redis_cache
  api_gateway --> receipts_object_store
  api_gateway --> orders_bus
  api_gateway --> orders_events_topic
  api_gateway --> cart_redis
  cart_service --> orders_postgresql
  cart_service --> catalog_redis_cache
  cart_service --> receipts_object_store
  cart_service --> orders_bus
  cart_service --> orders_events_topic
  cart_service --> cart_redis
  catalog_service --> orders_postgresql
  catalog_service --> catalog_redis_cache
  catalog_service --> receipts_object_store
  catalog_service --> orders_bus
  catalog_service --> orders_events_topic
  catalog_service --> cart_redis
  notify_worker --> orders_postgresql
  notify_worker --> catalog_redis_cache
  notify_worker --> receipts_object_store
  notify_worker --> orders_bus
  notify_worker --> orders_events_topic
  notify_worker --> cart_redis
  order_service --> orders_postgresql
  order_service --> catalog_redis_cache
  order_service --> receipts_object_store
  order_service --> orders_bus
  order_service --> orders_events_topic
  order_service --> cart_redis
  payment_service --> orders_postgresql
  payment_service --> catalog_redis_cache
  payment_service --> receipts_object_store
  payment_service --> orders_bus
  payment_service --> orders_events_topic
  payment_service --> cart_redis
  storefront_web_container --> orders_postgresql
  storefront_web_container --> catalog_redis_cache
  storefront_web_container --> receipts_object_store
  storefront_web_container --> orders_bus
  storefront_web_container --> orders_events_topic
  storefront_web_container --> cart_redis
  notify_worker_function --> orders_postgresql
  notify_worker_function --> catalog_redis_cache
  notify_worker_function --> receipts_object_store
  notify_worker_function --> orders_bus
  notify_worker_function --> orders_events_topic
  notify_worker_function --> cart_redis
```

## Notes

Auto-generated C4 view. Refine edges and technology tags manually; link with `c4_view_of` / `zooms_into`.
