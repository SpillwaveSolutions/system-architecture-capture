# SAC Typed Edges

Inherits all PKC/OKF relations, plus architecture relations:

| rel | Meaning |
|-----|---------|
| `calls` | Runtime service invocation |
| `exposes_api` | Service exposes API contract |
| `consumes_api` | Client consumes API |
| `deploys_to` | Artifact/service deploys to env/target |
| `runs_in` | Runs in container/serverless/runtime |
| `hosted_on` | Hosted on platform/cluster |
| `authenticates_via` | Uses IdP |
| `authorizes_with` | Authz config |
| `reads_from` / `writes_to` | Data store access |
| `publishes_to` / `subscribes_to` | Messaging |
| `provisions` | IaC provisions resource |
| `configures` | Configures target |
| `builds` / `produces_artifact` | Pipeline/build |
| `depends_on_package` | Service depends on package |
| `impacts` | Blast radius |
| `flows_to` | Data flow |
| `controls` | Control flow |
| `contains` | Hierarchical containment |
| `connects_to` | Network connectivity |
| `secured_by` | Network/IAM/mesh security |
| `observed_by` | Observability |
| `flagged_by` | Feature flag targets |
| `owned_by` / `owns` | Ownership |
| `part_of` | Membership in system |
| `instantiates` | Instance of abstract type |

Rules match PKC: body Markdown link + frontmatter `links[]`; never invent edges.

## Data, events, clients, platform (SAC expansion)

| rel | Meaning |
|-----|---------|
| `caches` | Service uses Cache |
| `indexes` | Writes/reads SearchIndex |
| `stores_in` | Persists in Database/ObjectStorage/… |
| `backed_by` | Logical store backed by physical resource |
| `emits` / `publishes_event` | Produces Event |
| `consumes_event` / `subscribes` | Consumes Event / Subscription |
| `streams_to` | Data/event stream target |
| `registers_schema` | EventSchema in SchemaRegistry |
| `dlq_for` | DeadLetterQueue for a queue/subscription |
| `schedules` / `triggers` | Cron/Job triggers work |
| `migrates` | Migration applies to Database |
| `exposes_ui` | Service/Bff exposes WebApp/MobileApp |
| `served_by` / `served_by_cdn` | Edge delivery |
| `secured_by_waf` | Protected by WAF |
| `integrates_with` | ExternalSystem / Integration |
| `belongs_to_domain` / `in_context` | Domain / BoundedContext |
| `for_channel` | Product channel |
| `journeys_through` | UserJourney touches services |
| `measured_by` / `alerts_on` | SLO/SLI/AlertRule |
| `encrypts_with` / `trusts` | Keys / trust |
| `complies_with` | ComplianceControl |
| `tested_by` | TestSuite / ContractTest |
| `backs_up` / `replicates_to` | DR / replicas |

