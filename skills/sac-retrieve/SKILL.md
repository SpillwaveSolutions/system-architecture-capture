---
name: sac-retrieve
description: >-
  Query-time retrieval of SAC architecture context without contaminating the
  parent. Spawn architecture-retriever for topology (Service, ApiContract,
  Package, Runtime, Pipeline, IdentityProvider, blast radius). Do not run
  sac_search or sac_pack in the parent. Consume only the retrieval card.
---

# SAC Retrieve

Parent-facing. This is **query-time retrieve**, not reverse-engineering.

Do **not** run `sac_search.py`, `sac_pack.py`, or `sac_blast_radius.py` in the
parent for retrieval. Hit lists and full pack markdown must stay out of the
parent working context. Progressive disclosure clips the graph; it does not
isolate the parent.

## Spawn

Spawn the **`architecture-retriever`** agent (host Task / sub-agent).

Pass through:

- **query** — what the parent needs (topology, contract, runtime, impact)
- **seed** — optional concept path when already known (`services/order-service.md`)
- **bundle** / **repo** — knowledge root the human already owns, or `sample-knowledge/`

The child owns search, scoring, `--tiny` / `--hops 2` pack, optional blast-radius,
and up to two deepen steps. It returns a **retrieval card only**.

## Consume

Read only the card. Do not ask the child for full hits, mermaid, or pack bodies.

```markdown
## Retrieval card
- Query: …
- Seed: `/path` (`Type`) — why chosen
- Fit: high|medium|low — one sentence
- Engine: rg|scan
- Pack: hops=N nodes=N tokens=N/budget  (or Blast: hops=N)
- Lead nodes: (5–8 bullets: title · type · path · one-line why)
- Critical edges: (up to 5 typed edges that matter) or none
- Open gaps: unverified / missing owners / orphans or none
- Next: stay|deepen-2hop|blast-radius|try-alt-seed `/other`
```

If **Next** is `deepen-2hop`, `blast-radius`, or `try-alt-seed`, spawn the
retriever again with that instruction. Do not run the engine yourself.

## Orthogonal fan-out

Architecture topology is SAC. Project-memory (Meeting, Feature, DecisionRecord,
Experiment, TicketLink) is PKC. If the parent also needs that plane, fan out
to PKC **`knowledge-retriever`** in a separate child. Do not merge the two
engines in this parent turn.

## Design-time

Skill `sac-design-with` should spawn this retriever (and blast-radius via the
child) before proposing new services, APIs, or apps.
