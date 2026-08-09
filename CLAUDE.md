# CLAUDE.md

**SAC** is a *plugin*, not an app. It reverse-engineers application systems into OKF knowledge graphs on top of PKC.

Hosts: Claude Code (`.claude-plugin/`), Grok (`.grok-plugin/` + Claude zero-config), Codex (`.codex-plugin/`), OpenCode (`.opencode-plugin/`). **Never diverge packaging.**

## Commands

```bash
python3 tests/test_sac.py
npm test
npm run typecheck
npm run validate
npm run doctor
npm run dev          # preview on :8080
bash tools/ci-local.sh
```

## Rules

1. Zero pip deps — extend `sac_common._parse_simple_yaml` if needed.
2. All writes via `write_concept()`.
3. Never invent edges; scrub secrets on ingest.
4. Adding a capability = skill + command + script + CI typecheck list + README.
5. Version bumps: `.claude-plugin/*`, `.grok-plugin/*`, `.codex-plugin/*`, `.opencode-plugin/*`, `marketplace.json`, `package.json`, README.
6. Depends on PKC + OKF conceptually; scanners run standalone.

## Reference

- `sample-knowledge/` is the golden fixture.
- Scanners: `scripts/sac_scan_*.py`
- Orchestrator: `scripts/sac_orchestrate.py`

## Provider connectivity

External systems (wiki, tickets, cloud APIs, IdP admin) are reached via host **skills/MCPs**. SAC normalizes exports and scans git trees — it does not re-implement every provider.
