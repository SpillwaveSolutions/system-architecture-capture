# AGENTS.md — System Architecture Capture

SAC builds a **second brain** for repos/monorepos by reverse-engineering modern application systems into OKF knowledge (extends PKC).

## Hosts

| Host | Manifest |
|------|----------|
| Claude Code | `.claude-plugin/` |
| Grok Build | `.grok-plugin/` (+ Claude zero-config) |
| Codex | `.codex-plugin/plugin.json` + `hooks/hooks.json` + `skills/` |
| OpenCode | `.opencode-plugin/plugin.json` + `skills/` |
| Agent Plugins 1.0 | Root `plugin.json` |
| Grok Bot | Skills + `docs/GROK_BOT.md` (not a Claude-style install) |
| LangChain Deep Agents | `skills=` / SkillsMiddleware — `docs/LANG_CHAIN_DEEP_AGENTS.md` |

Write isolation: `docs/ISOLATION.md`. Open `/sac-session` before writing a shared second brain.

## Entry points

- Agent: `architecture-orchestrator`
- Skill: `sac-reverse-engineer`
- CLI: `python3 scripts/sac_orchestrate.py --scan-root <repo> --system "Name"`

## Sub-agents

codebase-walker · iac-reverse-engineer · network-iam-topology · cicd-reverse-engineer · identity-auth-discoverer · wiki-ticket-ingester · graph-builder

## Invariants

OKF Markdown only · no invented edges · scrub secrets · cloud/stack agnostic patterns · progressive disclosure packs (2-hop default)

## Tests

```bash
python3 tests/test_sac.py
python3 tests/test_isolation.py
bash tools/ci-local.sh
```

## Provider connectivity

External systems (wiki, tickets, cloud APIs, IdP admin) are reached via host **skills/MCPs**. SAC normalizes exports and scans git trees — it does not re-implement every provider.

When designing new features/services/APIs/apps against a captured estate, use skill `sac-design-with` (load pack + blast radius first).
