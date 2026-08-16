---
name: grok-bot-system-architecture-capture
description: Bind a Grok Bot agent to System Architecture Capture. Isolation, identity, deterministic reverse-engineering.
---

# Grok Bot / System Architecture Capture

Read `docs/ONBOARDING.md` first, then follow `docs/GROK_BOT.md`.

1. Identity: `grok-bot/system-architecture-capture`
2. Open an isolation session before writes (`scripts/brain_session.py open`) unless the human already pointed `SECOND_BRAIN_ROOT` at a session worktree.
3. Pack or blast-radius 2 hops, then write owned architecture types only via `scripts/sac_*.py`.
4. Close the session to PR. Report path + validation result.
5. Never document a private remote. Never write raw Markdown into the tree.
