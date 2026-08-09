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
