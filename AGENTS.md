# AGENTS.md — System Architecture Capture

SAC reverse-engineers modern application systems into OKF knowledge (extends PKC).

## Hosts

| Host | Manifest |
|------|----------|
| Claude Code | `.claude-plugin/` |
| Grok Build | `.grok-plugin/` (+ Claude zero-config) |
| Codex | `.codex-plugin/plugin.json` + `skills/` |
| OpenCode | `.opencode-plugin/plugin.json` + `skills/` |

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
bash tools/ci-local.sh
```
