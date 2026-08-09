workspace "Northstar Commerce" {
  model {
    customer = person "Customer"
    northstar_commerce = softwareSystem "Northstar Commerce" {
      catalog_redis_cache = container "Catalog Redis cache" "Hot product catalog cache." "Cache"
      storefront_ios = container "Storefront iOS" "Native iOS commerce client." "MobileApp"
      storefront_web = container "Storefront Web" "Customer-facing commerce web application." "WebApp"
      storefront_web_container = container "Storefront Web Container" "C4 container for the Next.js storefront (maps to WebApp)" "SoftwareContainer"
      cart_redis = container "cart-redis" "Redis cluster for carts" "DataStore"
      orders_postgresql = container "Orders PostgreSQL" "Primary relational store for orders and line items." "Database"
      nightly_settlement_job = container "Nightly settlement job" "Batch job reconciling payments and ledgers." "Job"
      orders_bus = container "orders-bus" "Kafka topic family for order domain events" "MessageQueue"
      orders_events_topic = container "Orders events topic" "Orders events topic" "Topic"
      product_search_index = container "Product search index" "OpenSearch index for product discovery." "SearchIndex"
      notify_worker_function = container "notify-worker function" "Lambda/Cloud Function for notifications" "ServerlessFunction"
      api_gateway = container "API Gateway" "Edge gateway (Kong/Envoy) terminating TLS and routing to internal services" "Service"
      cart_service = container "Cart Service" "Session shopping carts backed by Redis" "Service"
      catalog_service = container "Catalog Service" "Product catalog read API and search index writer" "Service"
      notify_worker = container "Notify Worker" "Serverless-style worker consuming order events and sending email/SMS" "Service"
      order_service = container "Order Service" "Order lifecycle orchestration; publishes domain events" "Service"
      payment_service = container "Payment Service" "Payment authorization and capture via Stripe; PCI-scoped" "Service"
      receipts_object_store = container "Receipts object store" "S3 bucket for order receipts and invoices." "ObjectStorage"
    }
    auth0 = softwareSystem "Auth0" {
      tags "External"
    }
    stripe = softwareSystem "Stripe" {
      tags "External"
    }
    customer -> northstar_commerce "Uses"
  }
  views {
    theme default
  }
}
