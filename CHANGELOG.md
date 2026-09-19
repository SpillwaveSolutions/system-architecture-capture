# Changelog

## Unreleased

### Fixed

- **`sac_search` rg path no longer walks the whole bundle.** It materialized
  `iter_concepts()` and called `Path.resolve()` per file regardless of how few
  hits rg returned — the same syscall storm PKC removed in v0.9.1. Hits are now
  filtered as strings against the concept rules (`is_concept_rel`, new in
  `sac_common`) with the bundle resolved once. Scoring and results are
  unchanged; `is_concept_path` now delegates to `is_concept_rel`.
- **`find_rg()` fails closed on an unusable override.** `SAC_RG_PATH` /
  `PKC_RG_PATH` / `OKF_RG_PATH` / `SECOND_BRAIN_RG_PATH` pointing at a missing
  or non-executable path now disables rg instead of falling through to
  `PATH` — the research-graph / PKC 0.9.5 rule, so one variable means one
  thing across plugins.
- `sac_search` breaks score ties by path, so result order is stable across
  engines.

## 0.5.6 — 2026-09-12

### Added

- Breadth-first reverse-engineering **plan** (`scripts/sac_plan.py`): repo map,
  ecosystems, ranked focus areas, per-area deep-dive checklists, suggested
  sub-agent assignment. Writes operational artifacts under the bundle
  (`.sac/re-plan.md`, `.sac/re-plan.json`, `.sac/re-plan-progress.json`).
- `sac_orchestrate.py --plan-only` and `--from-plan` / `--area` so hosts can
  pause after the plan, then fan out domain-scoped scans instead of repeating
  `full_scan` in every child. Unattended orchestrate still plans first, then
  captures only domains the plan detected.
- `sac_capture.py --domains` and `sac_materialize.py --domains` for scoped writes.
- Skill `sac-plan` / command `/sac-plan`. architecture-orchestrator and
  `sac-reverse-engineer` now teach plan → task list → parallel area walkers →
  graph-builder. Query-time `architecture-retriever` / `sac-retrieve` stay
  separate. Checklist items are marked `done` or `blocked` via `sac_plan.py mark`.
- Signal-gated **language specialists** (`java-codebase-walker` treats **Gradle
  and Maven as first-class** — spawn when either or both markers exist; mixed
  repos list both build systems — plus TypeScript, Python, Rust, and
  `other-codebase-walker`) and **IaC specialists** (Terraform, CDK, plus thin
  CloudFormation / Pulumi / Helm / Kustomize). The plan lists who to spawn; no
  Java walker without Gradle or Maven markers, no Terraform walker without
  `.tf`. Specialists enrich after the deterministic scan — they do not replace
  `sac_scan_packages.py` / `sac_scan_iac.py`.

## 0.5.5 — 2026-09-12

### Added

- Query-time **`architecture-retriever`** sub-agent and **`sac-retrieve`** skill.
  Search, scoring, pack/blast-radius, and deepen stay in the child. The parent
  spawns the retriever and consumes a retrieval card only — not hit lists or
  full pack markdown. Orthogonal fan-out to PKC `knowledge-retriever` for
  project-memory.
- `sac_pack.py --summary`: compact card-friendly stdout (bodies off, no mermaid),
  same fail-closed token budget as the full pack. JSON includes `edges` so the
  child can build the card without pasting mermaid.

## 0.5.4 — 2026-08-31

### Fixed

- Catalog refresh now renders typed YAML title scalars safely. Integer,
  boolean, and date-like titles no longer crash Markdown link escaping, and
  falsey values such as `false` and `0` retain their textual labels.
  ([#35](https://github.com/SpillwaveSolutions/system-architecture-capture/issues/35))
- The ripgrep-backed reverse index now canonicalizes both match and bundle
  paths before relativizing them. Inbound edges are no longer silently dropped
  when the same bundle is addressed through symlink aliases such as `/var` and
  `/private/var`.
  ([#36](https://github.com/SpillwaveSolutions/system-architecture-capture/issues/36))

## 0.5.3 — 2026-08-30

- **rg-backed reverse index** in `sac_pack.py`. Inbound/backlink discovery is
  O(subgraph) when `rg` is on PATH (`SAC_RG_PATH` / `PKC_RG_PATH` / `OKF_RG_PATH`);
  otherwise the previous full scan. Outbound is always parsed from the current
  file, so the graph matches `--no-rg`. `--rg` / `--no-rg` flags. Result JSON
  includes `reverse_index` (`rg` | `scan`). Never installed from a hook.

## 0.5.2 — 2026-08-30

- `sac_search.py` uses ripgrep as a candidate prefilter when `rg` is on PATH
  (`SAC_RG_PATH` / `PKC_RG_PATH` / `OKF_RG_PATH`). `--no-rg` forces a full scan.
  Ranking stays in Python. `sac_doctor.py` reports whether rg was found.

## 0.5.1 — 2026-08-24

- Noun-ownership migration guide:
  [`docs/user_guide/noun-ownership-migration.md`](docs/user_guide/noun-ownership-migration.md).

## 0.5.0 — 2026-08-24

### Changed

- **Noun ownership.** SAC types.json 1.4.0 is architecture/runtime topology
  only. PKC / DEKC / AGER / okf-plugin own their own types. Validators merge
  sibling schema packs.
- README lists all 139 SAC nouns (comma-delimited + grouped by catalog).
- Dual-owned names documented: `Package` (also PKC), `Dashboard` / `DataLake` /
  `GlossaryTerm` (also DEKC), `RateLimit` (also AGER).

## 0.4.4

- Three-host hooks: Codex + Cursor-native when Claude hooks exist.


Notable changes to **system-architecture-capture**. Newest first.

## Unreleased

### Fixed

- Re-synced `.opencode-plugin/plugin.json` (0.4.2 → 0.4.3) and the README version table, both missed by the 0.4.3 bump. The OpenCode manifest had been skipped by three consecutive releases.
- Restored the CHANGELOG intro line to directly under the title; the 0.4.3 entry had been inserted above it.
- `.claude-plugin/plugin.json` and `package.json` descriptions now list Cursor alongside the other hosts.
- README now documents the Cursor host (intro list + Multi-host table); 0.4.3 shipped `.cursor-plugin`, `docs/CURSOR.md` and `hosts/cursor/` without any README mention.

### Added

- `tools/check_consistency.py` (`npm run consistency`, wired into CI): asserts every published version site matches `package.json` and that the Rule 4 typecheck list covers `scripts/*.py`. Version sites are discovered by glob, so a new host manifest is covered the day it lands.

## 0.4.3 — 2026-08-17

- **Cursor host.** `.cursor-plugin/plugin.json` (Cursor Plugins) plus `.cursor/rules/second-brain.mdc`. Docs: `docs/CURSOR.md`. `docs/GROK_BOT.md` now covers Grok Bot spawning Cursor cloud agents.


## 0.4.2 — 2026-08-16

### Added

- ContextPack token budget matches second-brain-core 0.3.3 / PKC 0.7.2: default 1/4 of `SECOND_BRAIN_WINDOW_TOKENS` (128000 → 32000). Override with `--max-tokens` or `SECOND_BRAIN_PACK_MAX_TOKENS`.
- Pack is **fail-closed** when the rendered subgraph exceeds the budget. `--write` is skipped.
- Bodies off unless that node is the pack root. Neighbors keep title, type, path, and frontmatter `description` only.
- Node clip (`--max-nodes` / `--tiny`) is not a token budget.
- Implements part of [okf-plugin#55](https://github.com/SpillwaveSolutions/okf-plugin/issues/55).

## 0.4.1 — 2026-08-16

### Added

- Required identity on every knowledge write: `--author` or `SECOND_BRAIN_IDENTITY`.
- `write_knowledge()` stamps `author` and emits a `WriteEvent`. `write_concept` stays pure.
- Wired through capture, materialize, orchestrate, wiki/ticket ingest, C4 `--generate`, blast-radius `--write`, and link.
- Fail-closed tests. Print-only / scan paths do not require identity.

## 0.4.0 — 2026-08-15

### Added

- **Multi-host bindings + write isolation.** Root Agent Plugins 1.0 `plugin.json`, Grok Bot / Deep Agents / isolation / onboarding docs, host wrappers, vendored `scripts/brain_session.py`, and `sac-session` skill/command.
- Concurrent writers read `main` and write `brain/<actor>/<session-id>`. Close via PR against the checkout's existing remote.
- Isolation tests use fictional **lumenfield-detector** / **northstar-console** actors only.

### Changed

- Version stamps aligned to **0.4.0** across plugin manifests and marketplace metadata.
- `.codex-plugin` now references `hooks/hooks.json` explicitly.

## 0.3.1 — 2026-08-13

### Changed

- **`okf-concept-envelope.json` `truth_state`** now accepts the union of PKC/SAC
  and DEKC values so a mixed second brain validates.

## 0.3.0 — 2026-08-10


Ten fixes, all found by running this plugin alongside `project-knowledge-capture`
and `data-engineering-knowledge-capture` against a single shared bundle.

### Fixed

- **Frontmatter round-trip doubled backslash escaping.** `_fmt_scalar` escaped
  backslashes and quotes; `_scalar` stripped only the surrounding quotes. Every
  write-modify-write cycle re-escaped already-escaped text, so a script editing
  one field corrupted every quoted string in the file. Self-concealing: reading
  back with the same parser returned a value that looked correct, so the damage
  lived only in the bytes on disk. (#2)

- **A bracketed concept title dropped the catalog edge.** `[AREA] Thing` rendered
  as `[[AREA] Thing](/cat/x.md)`, which the graph reader's link regex cannot
  match — producing a *missing* edge rather than a broken one, which `validate`
  does not report. Note this half needs the matching reader change to take
  effect: escaping does not rescue a reader whose label class is `[^\]]+`. (#1)

- **`refresh_catalog_index` accepted any catalog name**, so a caller could drive
  this renderer over a sibling plugin's catalog. It now refuses catalogs this
  plugin does not declare. This alone does *not* stabilise a shared bundle — for
  a catalog two plugins both declare it passes in both. (#4)

- **`resolve_knowledge_root` fell through to `sample-knowledge/` in silence.**
  It now names the intended and actual root on stderr. This repo ships a
  `sample-knowledge/`, so a capture run inside a clone wrote there. The
  configured root still wins whenever it is usable. (#3)

- **The `PostToolUse` hook was registered and did nothing.** `sac-curate.sh`
  ended in an unconditional `exit 0`. Now implemented to match the sibling
  plugin: refresh only the catalog holding the edited file. (#8)

- **`append_log` lost concurrent updates.** Whole-file read-modify-write with no
  synchronisation — and with the hook above now firing, no longer theoretical.
  Takes an advisory `flock` on the target file itself, so no sidecar `.lock` is
  left in the bundle. `O_APPEND` is not usable: entries are inserted under
  today's heading mid-file. (#7)

- **Ticket ingest could not read Jira.** Jira nests everything but `key` under
  `fields{}`, so every ticket fell through to `str(key)` for its title and lost
  description, status, labels and type — while reporting success. Descriptions
  are ADF document trees, now flattened. A second, independent precedence bug
  discarded a flat `"status": "Done"` whenever `state` was absent. (#10)

- **Wiki ingest filed runbooks as `Design`.** `Runbook` is a registered type and
  the skill advertises runbook handling. (#9)

### Added

- **`write_concept(..., create_only=True)`.** `merge` protects frontmatter, never
  the body — correct for re-capture, and the reason a scaffolding pass re-run
  after enrichment flattens concepts back to stubs. Default behaviour unchanged
  and now pinned by a test. (#5)

- **A `"refused"` return value**, distinct from `"skipped"`. A `truth_state`
  refusal previously returned the same value as a byte-identical no-op, so a
  caller could not tell "already correct" from "your write was discarded".
  `sac_materialize` now counts and prints it. (#6)

- **`--default-type` on wiki ingest**, plus an `unclassified` count. The
  fallback type is a guess and nothing downstream could tell it apart from a
  match; type drives catalog placement, which drives what `impact` and `pack`
  return. (#9)

### Notes

- The `0.2.0` section previously sat *above* the `# Changelog` header and no
  version manifest was ever bumped to match it, so its content shipped inside
  `0.1.0`. That content is folded into the history below and this release is
  `0.3.0` to avoid reusing a version number that was already published in a
  changelog.

## 0.2.0 — diagrams & code structure (never released; shipped within 0.1.0)

- Mermaid + PlantUML diagram concepts (wireframe through ERD/C4)
- Module / Class / Method / Function reverse-engineering
- Scanners + skill sac-capture-diagrams

## 0.1.0 — 2026-08-09

- Initial System Architecture Capture plugin
- Multi-host: Claude Code, Grok, Codex, OpenCode
- Scanners: packages, containers, IaC, K8s, CI/CD, identity
- Orchestrator + capture + graph + blast radius + packs
- Wiki + ticket ingest
- Sample: Northstar Commerce architecture knowledge
- Depends on PKC + OKF conceptually
