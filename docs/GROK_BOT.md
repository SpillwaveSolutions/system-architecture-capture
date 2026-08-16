# Grok Bot — binding System Architecture Capture

You are operating as a **Grok Bot** agent that reverse-engineers system architecture into the same shared institutional second brain used by local agents (Claude Code, Grok Build, Codex, OpenCode).

Read [ONBOARDING.md](ONBOARDING.md) first.

This file is the binding contract. It does **not** install a Claude-style plugin. Grok Bot skills are workflows. Enable the skill that matches the task and follow the rules below.

## Privacy (non-negotiable)

- The working second brain is private. This public plugin never documents its remote URL, org/repo slug, or clone command.
- Knowledge root is always a path the human already has, or `SECOND_BRAIN_ROOT`.
- Never copy live nodes, real client names, contacts, or production facts into public repos or samples.
- Public samples remain the in-repo `sample-knowledge/` fiction only.

## Identity

- Actor string: `grok-bot/system-architecture-capture`
- Claim per process with `SECOND_BRAIN_IDENTITY=grok-bot/system-architecture-capture`
- Do **not** use a single shared `knowledge/.identity.json` for a fleet.
- Chat prefix: `Grok Bot: System Architecture Capture`

## Isolation

Multiple agents on multiple machines share one private remote. Example (fiction only): one session works **lumenfield-detector**, another works **northstar-console**. Both read `main`. Both write only in `brain/<actor>/<session-id>`.

1. Read shared truth from `main` (fast-forward pull).
2. Before writing, open a session worktree (see [ISOLATION.md](ISOLATION.md)).
3. Write only inside that worktree via SAC scripts.
4. Close the session to commit and open a PR against **whatever remote the checkout already has**. Never force-push. Never invent a remote.

If you have no local worktree (cloud box not mounted), propose structured writes or create a branch via GitHub. Same actor string. Same owned types.

## Knowledge root

```bash
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-knowledge}"
export SECOND_BRAIN_IDENTITY="grok-bot/system-architecture-capture"
```

## Deterministic write boundary

The model proposes structure. Scripts scan, capture, and materialize Markdown + YAML.

```bash
python3 scripts/sac_scan.py --help
python3 scripts/sac_pack.py services/example.md --bundle "${SECOND_BRAIN_ROOT}" --hops 2
python3 scripts/sac_validate.py --bundle "${SECOND_BRAIN_ROOT}" --schema
python3 scripts/sac_blast_radius.py services/example.md --bundle "${SECOND_BRAIN_ROOT}"
```

**Forbidden:** silent raw dumps into the knowledge tree without type, provenance, or validation.

**Required:** type ownership. This pack owns architecture nouns from `schemas/types.json` (System, Service, Package, Module, ApiContract, Endpoint, ContainerImage, Runtime, ServerlessFunction, DataStore, MessageQueue, IdentityProvider, Network, InfrastructureStack, Pipeline, Deployment, Environment, Cluster, Namespace, Diagram family, Class/Method/Function, and related SAC types). Refuse product-memory nouns owned by PKC and pure agent-graph nouns owned by okf-plugin / AGER unless co-authoring is explicit.

## Progressive disclosure

Default ContextPack: **2 hops / ~20 nodes**.

Pack or blast-radius before answering or writing. Do not dump the entire topology.

## Skill binding

Grok Bot does not run `/plugin marketplace add`. Enable the relevant skills from this repo (`skills/*/SKILL.md`). Set identity and knowledge root. Report path + validation result, not a dumped graph.

Thin host wrapper: `hosts/grok-bot/SKILL.md`.

## Three memory planes

| Plane | Location |
|-------|----------|
| Procedural | Skills, this file, [ONBOARDING.md](ONBOARDING.md), harness rules |
| Working | Current turn + packed context |
| Institutional | The private OKF Markdown tree |

## Related public packages

Foundation: [okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin), [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture), [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) (this repo), [data-engineering-knowledge-capture](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture), [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd), [okf-agent-graph](https://github.com/SpillwaveSolutions/okf-agent-graph).

ContentPack suite: [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core) plus the eight job packs and marketplace / starter.
