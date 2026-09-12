---
name: sac-design-with
description: >-
  Use the SAC architecture second brain when designing new features, services,
  APIs, mobile apps, web apps, or infra. Loads progressive-disclosure packs
  (blast radius, contracts, deps, environments) so design work reuses existing
  topology instead of inventing in a vacuum. Trigger on design, new service,
  new API, new feature, architecture impact, or "how should we build".
---

# Design with the Architecture Second Brain

SAC is not only for reverse-engineering. **After** the second brain exists, use
it as the default context when proposing:

- New features / product slices  
- New services or packages  
- New APIs / contracts  
- New web or mobile clients  
- New pipelines, environments, or infra  

## Process

1. **Locate the bundle**  
   Prefer `knowledge/` in the target repo (or path the user names).

2. **Name the design intent**  
   One sentence: *what* is new and *where* it attaches (domain, client, backend).

3. **Retrieve a context card** (do not run search/pack in this parent):

   Spawn **`architecture-retriever`** via skill `sac-retrieve`. Pass the design
   intent as the query, an optional seed service/API path, and the bundle.
   Consume **only** the retrieval card. If the card says `deepen-2hop` or
   `blast-radius`, spawn the retriever again — do not run `sac_pack.py` /
   `sac_search.py` / `sac_blast_radius.py` here.

   Project-memory (meetings, decisions, features) is an orthogonal fan-out to
   PKC `knowledge-retriever`.

4. **Answer before inventing** (use pack + concepts):
   - Which **System / Service / Package** already owns this domain?
   - What **ApiContracts** exist? Extend vs new surface?
   - What **Database / Cache / ObjectStorage / SearchIndex / Event** surfaces would be touched?
   - Auth: existing **IdentityProvider / IamRole** patterns?
   - Deploy: which **Environment / Pipeline / InfrastructureStack**?
   - **Ownership** and **GlossaryTerm** for naming and team?

5. **Propose the design** grounded in the graph:
   - Author or update **diagrams** (sequence, component, ERD, wireframes) as Mermaid/PlantUML listings in diagram concepts.
   - Name new **Module / Class / Function** concepts when the design adds code shape.

   - Prefer extend/reuse edges (`calls`, `exposes_api`, `depends_on_package`) over greenfield silos.
   - Call out blast radius (what breaks if the new thing fails or the shared API changes).
   - List **new OKF concepts** to author after the design is accepted (Service, ApiContract, …).
   - Optionally write a `DecisionRecord` under `decisions/` once the choice is made.

6. **Do not** re-scan the whole monorepo unless the second brain is missing or stale — design from the knowledge graph first.

## Output shape

```markdown
## Design intent
…

## Existing landscape (from second brain)
- Services / packages / APIs touched
- Data & identity
- Deploy path

## Options
1. …
2. …

## Recommendation
…

## Blast radius
…

## Concepts to add/update after build
- …
```

## Connectivity

Live wiki/ticket/cloud detail still comes from host **skills/MCPs** when needed;
the second brain is the primary structured memory for *what already exists*.
