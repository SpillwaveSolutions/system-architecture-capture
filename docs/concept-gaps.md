# Concept coverage gaps & expansions

`DataStore` alone is too coarse for a second brain used at design time.
The registry now promotes common runtime building blocks to **first-class types**
(still OKF envelope + typed edges). Tags may refine vendor/engine.

## Was thin / missing (now first-class)

### Data plane
| Type | Why |
|------|-----|
| `Database` | Relational / document / graph primary stores (Postgres, MySQL, Mongo, Dynamo, Neo4j, …) |
| `Cache` | Redis, Memcached, CDN edge cache, app caches |
| `ObjectStorage` | S3, GCS, Azure Blob, MinIO |
| `SearchIndex` | Elasticsearch, OpenSearch, Solr, Algolia |
| `DataWarehouse` | Snowflake, BigQuery, Redshift, … |
| `DataLake` | Lakehouse / raw object + table formats |
| `VectorStore` | Embeddings / RAG indexes |
| `FileSystem` | NFS, EFS, shared volumes |
| `SchemaRegistry` | Avro/Protobuf/JSON Schema registry |
| `Migration` | Schema/data migration sets (Flyway, Liquibase, alembic) |

### Events & async
| Type | Why |
|------|-----|
| `Event` | Named domain/integration event |
| `EventSchema` | Payload contract (Avro/JSON Schema/Protobuf) |
| `EventStream` | Durable log stream (Kafka topic family, Kinesis stream) |
| `Subscription` | Consumer subscription / consumer group |
| `DeadLetterQueue` | DLQ / poison queue |
| `Saga` | Long-running multi-service process |
| `Job` | Batch / scheduled / queue worker job |
| `CronSchedule` | Time trigger definition |
| `Webhook` | Outbound/inbound HTTP callback contract |

### Application surfaces
| Type | Why |
|------|-----|
| `WebApp` | Browser SPA/MPA / SSR app |
| `MobileApp` | iOS/Android/React Native/Flutter |
| `DesktopApp` | Electron etc. |
| `AdminApp` | Back-office UI |
| `Bff` | Backend-for-frontend |
| `ApiGateway` | Edge API gateway (distinct from L4/L7 LB) |
| `GraphQlSchema` | GraphQL schema surface |
| `Sdk` | Client SDK / published library API |
| `Cli` | CLI tool surface |

### Platform & compute
| Type | Why |
|------|-----|
| `Repository` | Git repo (multi-repo map) |
| `Monorepo` | Monorepo root / workspace map |
| `ArtifactRegistry` | Container/npm/maven/PyPI registry |
| `Cluster` | K8s / ECS / nomad cluster |
| `Namespace` | K8s namespace / project isolation |
| `HelmChart` | Chart package |
| `TerraformModule` | Reusable TF module |
| `CloudAccount` | AWS account / GCP project / Azure sub |
| `Region` | Cloud region |
| `NodePool` | Compute node group |
| `Volume` | Persistent volume claim / disk |

### Network edge (beyond VPC/SG/LB)
| Type | Why |
|------|-----|
| `DnsZone` | DNS zone / records ownership |
| `Cdn` | CloudFront, Fastly, Cloudflare |
| `Certificate` | TLS cert |
| `Waf` | WAF / bot protection |
| `PrivateLink` | Private service connectivity |
| `Vpn` | Site-to-site / client VPN |
| `NatGateway` | Egress NAT |
| `ServiceAccount` | K8s/GCP/Azure workload identity SA |

### Security & trust
| Type | Why |
|------|-----|
| `EncryptionKey` | KMS CMK / key ring |
| `PolicyDocument` | OPA/Cedar/IAM-as-doc / admission policy |
| `ComplianceControl` | SOC2/ISO control mapping |
| `AuditTrail` | Audit log stream/config |
| `Permission` | Fine-grained authz unit (when modeled) |

### Reliability & ops
| Type | Why |
|------|-----|
| `Slo` | Service level objective |
| `Sla` | External/internal agreement |
| `Sli` | Indicator definition |
| `AlertRule` | Alerting rule |
| `Dashboard` | Ops/product dashboard |
| `Incident` | Incident record (linkable) |
| `BackupPolicy` | Backup/DR policy |
| `DisasterRecoveryPlan` | DR run posture |

### Domain / product (design-time)
| Type | Why |
|------|-----|
| `Domain` | DDD domain / sub-domain |
| `BoundedContext` | Bounded context |
| `BusinessCapability` | Capability map node |
| `Product` | Product surface |
| `Channel` | web / mobile / partner / store |
| `Actor` | User/system actor |
| `UserJourney` | Journey that spans services |
| `Integration` | External partner/system integration |
| `ExternalSystem` | SaaS / third-party system |

### Config & quality
| Type | Why |
|------|-----|
| `ConfigMap` | K8s-style config map / app config blob |
| `RateLimit` | Throttle policy |
| `Quota` | Resource quota |
| `TestSuite` | Automated test suite (contract/e2e) |
| `ContractTest` | Consumer-driven contract test |

## Keep as tags / subtypes (not every vendor)

Engine tags on concepts: `postgres`, `redis`, `kafka`, `dynamodb`, `s3`, …
Cloud tags: `aws`, `gcp`, `azure`, `on-prem`.
Do **not** create one type per AWS resource name — prefer the pattern types above.

## Still optional / future

- Full FinOps (`CostCenter`, `Budget`) — add when needed  
- Physical DC / rack — rare for this second brain  
- ML feature stores beyond `VectorStore` + `DataWarehouse` — extend when ML-heavy estates appear  

## Relations added for data/events

`caches`, `indexes`, `stores_in`, `streams_to`, `emits`, `consumes_event`, `schedules`, `backs_up`, `replicates_to`, `integrates_with`, `exposes_ui`, `served_by_cdn`, `secured_by_waf`, `measured_by`, `alerts_on`, `belongs_to_domain`, `in_context`, `for_channel`, `invokes`, `migrates`

## Code structure & diagrams (v1.2)

| Type | Why |
|------|-----|
| `Module` | Source module ≠ build `Package` |
| `Class` / `Interface` / `Enum` | Type-level design & blast radius |
| `Method` / `Function` | Behavioral units agents reason about |
| `Wireframe` | PlantUML salt UI mockups |
| `ArchitectureDiagram` … `ErdDiagram` | Design artifacts as first-class knowledge |
| `SequenceDiagram` / `C4Diagram` | Interaction & C4 views |

Scanners: `sac_scan_diagrams.py`, `sac_scan_code_structure.py`.

