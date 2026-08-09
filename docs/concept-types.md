# SAC Concept Types

## Architecture types

| Type | Directory | Role |
|------|-----------|------|
| System | systems/ | Top-level system boundary |
| Service | services/ | Deployable runtime unit |
| ApiContract / Endpoint | apis/ | Interface contracts |
| Package / Module | packages/ | Build unit (npm/maven/gradle/go/…) |
| BuildArtifact | build-artifacts/ | Produced artifact |
| ContainerImage | containers/ | Image definition |
| Runtime | runtimes/ | Docker/containerd/CRI-O hints |
| ServerlessFunction | serverless/ | Lambda/Cloud Functions/Azure Functions |
| DataStore | datastores/ | DB/cache/search |
| MessageQueue / Topic | messaging/ | Async messaging |
| IdentityProvider / AuthConfig | identity/ | SSO/OAuth |
| IamRole / IamPolicy | iam/ | Identity & access |
| Vpc / Subnet / SecurityGroup / LoadBalancer / Network | networks/ | Networking |
| ServiceMesh | meshes/ | Mesh |
| SecretStore | secrets/ | Secrets management |
| Pipeline / Workflow | pipelines/ | CI/CD |
| Deployment | deployments/ | Deployed release unit |
| Environment | environments/ | dev/stage/prod |
| FeatureFlag | feature-flags/ | Flags |
| Metric / TraceSource / LogSource | observability/ | Telemetry |
| ConfigSource | config/ | Configuration |
| InfrastructureStack | infrastructure/ | CFN/TF/CDK/Pulumi/Helm/Kustomize |
| DataFlow | dataflows/ | Data path map |
| ControlFlow | controlflows/ | Control/deploy path map |
| BlastRadius | blast-radius/ | Impact analysis |
| GlossaryTerm | glossary/ | Business/tech terms |
| Ownership | ownership/ | Team ownership |

Plus full PKC types (Meeting, DecisionRecord, Feature, …).
