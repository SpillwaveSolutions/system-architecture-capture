# SAC Design

## Stack position

```
OKF (graph format, impact, pack, validate)
  ↑
PKC (meetings, experiments, decisions, WikiTicket materialize)
  ↑
SAC (this plugin — reverse-engineer runtime & infrastructure topology)
```

## Principles

1. **Deterministic scanners first** — agents add judgment, not path logic.
2. **Zero pip deps** — hand-rolled YAML like PKC.
3. **Cloud/stack agnostic concepts** with tool tags (`terraform`, `auth0`, …).
4. **Multi-host plugins** — Claude, Grok, Codex, OpenCode share one skill tree.
5. **Progressive disclosure** — packs default 2 hops for LLM precision.

## Module map

| Module | Role |
|--------|------|
| sac_common.py | catalogs, frontmatter, bundle IO |
| sac_scan_*.py | domain scanners |
| sac_scan.py | unified scan |
| sac_capture.py | scan → concepts |
| sac_orchestrate.py | multi-repo pipeline |
| sac_graph.py / sac_blast_radius.py | graph analytics |
| sac_pack.py / sac_search.py | query surfaces |
| sac_ingest_*.py | wiki + tickets |
