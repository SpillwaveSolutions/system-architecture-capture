# Concept types (architecture second brain)

Authoritative machine registry: [`schemas/types.json`](../schemas/types.json)  
Gap analysis & rationale: [`concept-gaps.md`](./concept-gaps.md)  
Envelope: [`schemas/okf-concept-envelope.json`](../schemas/okf-concept-envelope.json)

Every concept is standard OKF Markdown. Prefer **specific** types over umbrellas
(`Database` not bare `DataStore` when you know it is a DB; `Cache` for Redis; `Event` + `EventSchema` for async contracts).

## Layers

### OKF core
`Dataset` · `Table` · `Metric` · `Playbook` · `Runbook` · `API` · `Reference` ·  
`AgentNode` · `Workflow` · `Harness` · `DecisionRecord` · `SharedState` · `ToolCapability` · `TicketLink`

### PKC project memory
`Meeting` · `Experiment` · `Discovery` · `Assumption` · `Question` · `Feature` ·  
`Requirement` · `Specification` · `Design` · `Release` · `CodeChange` · `Package` · `Risk` · `Acceptance`

### SAC — runtime topology
`System` · `Service` · `ApiContract` · `Endpoint` · `Package` · `BuildArtifact` ·  
`ContainerImage` · `Runtime` · `ServerlessFunction` · `Job` · `CronSchedule` ·  
`WebApp` · `MobileApp` · `DesktopApp` · `AdminApp` · `Bff` · `Sdk` · `Cli` · `ApiGateway` · `GraphQlSchema`

### SAC — data plane (was under-specified)
`Database` · `Cache` · `ObjectStorage` · `SearchIndex` · `DataWarehouse` · `DataLake` ·  
`VectorStore` · `FileSystem` · `DataStore` (umbrella only) · `Migration` · `SchemaRegistry` ·  
`BackupPolicy` · `Volume`

### SAC — events & async
`Event` · `EventSchema` · `EventStream` · `Topic` · `MessageQueue` · `Subscription` ·  
`DeadLetterQueue` · `Webhook` · `Saga`

### SAC — identity, security, network
`IdentityProvider` · `AuthConfig` · `IamRole` · `IamPolicy` · `ServiceAccount` · `Permission` ·  
`SecretStore` · `EncryptionKey` · `Certificate` · `PolicyDocument` · `Waf` · `AuditTrail` ·  
`ComplianceControl` · `Vpc` · `Subnet` · `SecurityGroup` · `LoadBalancer` · `DnsZone` ·  
`Cdn` · `PrivateLink` · `Vpn` · `NatGateway` · `ServiceMesh` · `Network`

### SAC — platform & delivery
`Repository` · `Monorepo` · `ArtifactRegistry` · `Cluster` · `Namespace` · `NodePool` ·  
`CloudAccount` · `Region` · `HelmChart` · `TerraformModule` · `InfrastructureStack` ·  
`Pipeline` · `Deployment` · `Environment` · `FeatureFlag` · `ConfigSource` · `ConfigMap` ·  
`RateLimit` · `Quota`

### SAC — reliability & domain
`Slo` · `Sla` · `Sli` · `AlertRule` · `Dashboard` · `TraceSource` · `LogSource` · `Incident` ·  
`DisasterRecoveryPlan` · `Domain` · `BoundedContext` · `BusinessCapability` · `Product` ·  
`Channel` · `Actor` · `UserJourney` · `Integration` · `ExternalSystem` ·  
`TestSuite` · `ContractTest` · `DataFlow` · `ControlFlow` · `BlastRadius` ·  
`GlossaryTerm` · `Ownership`

## Design rule

When designing new features/services/APIs/apps, pack from these types first:
surfaces (`WebApp`/`MobileApp`/`Service`/`ApiContract`), data (`Database`/`Cache`/`Event`),
identity, deploy (`Environment`/`Pipeline`/`Cluster`), ownership, blast radius.
