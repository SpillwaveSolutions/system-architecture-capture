---
name: system-architecture-capture-deep-agents
description: Bind System Architecture Capture for LangChain Deep Agents / Deep Agents Code.
---

# System Architecture Capture for LangChain Deep Agents

Read and follow:

1. [docs/ONBOARDING.md](../../docs/ONBOARDING.md)
2. [docs/LANG_CHAIN_DEEP_AGENTS.md](../../docs/LANG_CHAIN_DEEP_AGENTS.md)
3. [docs/ISOLATION.md](../../docs/ISOLATION.md)

## Quick binding

Point `skills=` or SkillsMiddleware at this repo's `skills/` directory. Set:

```bash
export SECOND_BRAIN_IDENTITY="deep-agents/system-architecture-capture"
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-knowledge}"
```

Open an isolation session before writing a shared institutional tree. Prefer `scripts/sac_*.py` for deterministic scan / pack / blast-radius / validate.
