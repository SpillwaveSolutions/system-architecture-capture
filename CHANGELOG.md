# Changelog

## 0.4.3 — 2026-08-17

- **Cursor host.** `.cursor-plugin/plugin.json` (Cursor Plugins) plus `.cursor/rules/second-brain.mdc`. Docs: `docs/CURSOR.md`. `docs/GROK_BOT.md` now covers Grok Bot spawning Cursor cloud agents.

Notable changes to **system-architecture-capture**. Newest first.

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
