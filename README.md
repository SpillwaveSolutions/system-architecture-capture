# System Architecture Capture (SAC)

**The second brain for system architecture information.**

SAC is the **specialized second brain** for this class of knowledge: reverse-engineered services, packages, APIs, IaC, containers, serverless, CI/CD, networking, IAM, identity, ownership, and architectural context from monorepos or multi-repo estates.

It materializes that information as a durable [OKF](https://github.com/SpillwaveSolutions/okf-plugin) graph using a **standard OKF schema pack** (plus [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture)) so agents and humans can query topology, ownership, and blast radius with precision.

Works as a **Claude Code**, **Grok Build**, **Codex**, and **OpenCode** plugin.

| | |
|---|---|
| **Plugin name** | `system-architecture-capture` |
| **Version** | 0.1.0 |
| **License** | MIT |
| **Depends on** | [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture) · [OKF](https://github.com/SpillwaveSolutions/okf-plugin) |

## What this second brain is for

| In scope (SAC) | Adjacent (other second brains) |
|----------------|--------------------------------|
| Services, packages, APIs, deps | Product narrative only (PKC) |
| Containers, serverless, runtime | Meeting notes without system links |
| IaC, network, IAM, secrets | Pure agent/harness graphs (okf-plugin) |
| Pipelines, deploys, environments | |
| IdP / OAuth / SSO evidence | |
| Wiki + tickets as architecture context | |
| Glossary, ownership, blast radius | |

SAC does not replace PKC or OKF — it **is** the second brain **for system/architecture information**, built on their schemas and tooling.

## Why SAC

**Goal:** a living **second brain** for project information about the repos (or monorepo) you point it at — stored as a **standard set of OKF schemas** (plus PKC + SAC architecture types), not a one-shot report or proprietary DB.

PKC captures *why* (meetings, experiments, decisions). SAC captures *what is actually running*:

- Microservices, web apps, APIs, packages, monorepos / multi-repos
- Dependency graphs and build artifacts (npm · maven · gradle · go · cargo · pip — common model)
- Containers (Docker/containerd/CRI-O) and serverless (Lambda, Cloud Functions, Azure Functions)
- CloudFormation · Terraform · CDK · Pulumi · Helm · Kustomize · Kubernetes
- IAM roles/policies · VPCs · subnets · security groups · load balancers · service meshes
- SSO/OAuth (Auth0, Cognito, Okta, Azure AD, Keycloak)
- Secrets, CI/CD (GitHub Actions, GitLab CI, Jenkins, CircleCI, Argo, Tekton)
- Environments, deployments, feature flags, observability
- Wiki/ADR/runbook ingest + Jira/Linear/ADO/GitHub Issues
- Data-flow, control-flow, **blast-radius**, glossary, ownership

Cloud-agnostic and stack-agnostic — deep pattern awareness without locking to one vendor.

**Connectivity:** SAC does not ship deep clients for every wiki/ticket/cloud/IdP.
Host **skills and MCPs** connect and export; SAC ingests those exports and scans
repo-local code/IaC. You do not need SAC to re-implement provider APIs.


## When designing (use the second brain)

After capture, **design against the graph** — new features, services, APIs, web/mobile apps, pipelines:

```bash
# Context pack around a service
python3 scripts/sac_pack.py --bundle knowledge --focus services/order-service.md --hops 2

# Impact of changing something
python3 scripts/sac_blast_radius.py --bundle knowledge --from apis/orders-api.md

# Agent skill
# /sac-design "add returns API for mobile checkout"
```

Skill: `sac-design-with` · Command: `/sac-design`

The second brain answers: what already exists, what to reuse, who owns it, and blast radius — before you invent a parallel stack.

## Install

### Claude Code

```bash
claude plugin marketplace add SpillwaveSolutions/system-architecture-capture
claude plugin install system-architecture-capture@sac-plugin-marketplace
```

Recommended companions:

```bash
claude plugin marketplace add SpillwaveSolutions/project-knowledge-capture
claude plugin install project-knowledge-capture@pkc-plugin-marketplace
claude plugin marketplace add SpillwaveSolutions/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
```

### Grok Build

Grok discovers Claude-compatible plugins automatically (`.claude-plugin/`). Native listing also in `.grok-plugin/`.

### Codex

```text
# Plugin manifest: .codex-plugin/plugin.json
# Skills load from skills/*/SKILL.md
```

### OpenCode

```text
# Plugin manifest: .opencode-plugin/plugin.json
# Same shared skills/ and agents/
```

## Quick start

Point the orchestrator at one or more repo roots:

```bash
python3 scripts/sac_orchestrate.py \
  --repo . \
  --system "Northstar Commerce" \
  --scan-root /path/to/service-repo \
  --scan-root /path/to/infra-repo \
  --wiki /path/to/wiki-export \
  --tickets /path/to/issues.json \
  --json
```

Or slash command / skill: **`/sac-reverse-engineer`**

```bash
python3 scripts/sac_validate.py --bundle sample-knowledge
python3 scripts/sac_pack.py services/order-service.md --bundle sample-knowledge --hops 2
python3 scripts/sac_blast_radius.py services/order-service.md --bundle sample-knowledge --hops 3
python3 tests/test_sac.py
```

## Agents

| Agent | Role |
|-------|------|
| **architecture-orchestrator** | Lead RE pipeline across repos |
| **codebase-walker** | Packages, modules, service boundaries |
| **iac-reverse-engineer** | CFN / TF / CDK / Pulumi / Helm / Kustomize / K8s |
| **network-iam-topology** | VPC, SG, LB, mesh, IAM |
| **cicd-reverse-engineer** | Pipelines & deploy strategies |
| **identity-auth-discoverer** | SSO/OAuth/IdP/JWT |
| **wiki-ticket-ingester** | Wiki + issue trackers |
| **graph-builder** | Graphs, flows, blast radius, packs |

## Skills / commands

| Skill | Purpose |
|-------|---------|
| `sac-init` | Scaffold knowledge bundle |
| `sac-reverse-engineer` | Full autonomous RE |
| `sac-scan` | Deterministic scanners only |
| `sac-capture` | Scan → OKF concepts |
| `sac-graph` | Dependency graph / Mermaid |
| `sac-blast-radius` | Impact analysis |
| `sac-pack` | Progressive disclosure packs |
| `sac-search` | Full-text search |
| `sac-doctor` | Bundle health |
| `sac-link` | Typed edges |
| `sac-ingest-wiki` | Wiki/ADR ingest |
| `sac-ingest-tickets` | Ticket ingest |

## Sample knowledge

[`sample-knowledge/`](./sample-knowledge/) — **Northstar Commerce**: multi-service checkout topology with gateway, cart, order, payment, notify worker, Auth0, Istio, Terraform, Helm, Argo, GitHub Actions, blast radius, and ADRs.

## Architecture position

```
OKF  ← graph format / impact / pack
PKC  ← meetings / experiments / decisions / WikiTicket
SAC  ← reverse-engineered runtime & infrastructure topology  (this repo)
```

## Docs

- [PRD](./docs/prd.md) · [Design](./docs/design.md) · [OKF schemas](./docs/okf-schemas.md) · [Concept types](./docs/concept-types.md) · [Typed edges](./docs/typed-edges.md)
- Machine registry: [`schemas/types.json`](./schemas/types.json)

## License

MIT — see [LICENSE](./LICENSE).
