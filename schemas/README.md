# SAC OKF Schema Pack

**Goal:** a **second brain** for monorepo / multi-repo project information, expressed only as **standard OKF concepts** (Markdown + YAML frontmatter) that OKF tooling and PKC understand.

| Layer | Schemas |
|-------|---------|
| **OKF core** | Universal concept shape + base relations |
| **OKF knowledge / harness** | Dataset, API, Metric, Runbook, DecisionRecord, TicketLink, … |
| **PKC project memory** | Meeting, Feature, Experiment, Assumption, … |
| **SAC architecture** | System, Service, Package, InfrastructureStack, … |

All SAC-authored nodes **must** satisfy the [OKF concept envelope](./okf-concept-envelope.json) plus a declared `type` from [types.json](./types.json).

The envelope matches the shared okf-plugin `BaseConcept` (v1): required `type` + `title` only. `truth_state` accepts the union of PKC/SAC (`current|snapshot|superseded|archived`) and DEKC (`historical|proposed`) so mixed second brains validate.

When okf-plugin is a sibling checkout, `python3 ../okf-plugin/scripts/okf-graph.py validate <bundle>` loads this pack plus PKC/DEKC/AGER schemas.
