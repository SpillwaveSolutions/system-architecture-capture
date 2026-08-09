---
name: sac-c4
description: >-
  C4 model integration for the architecture second brain. Map System/Person/
  SoftwareContainer/Component/Code, generate L1–L4 Mermaid views, import
  Structurizr DSL, and avoid Docker vs C4 Container confusion.
---

# SAC × C4 model

## Critical naming

- **C4 Container** = `SoftwareContainer` (or Service/WebApp/Database stand-ins)
- **Docker/OCI** = `ContainerImage` — different concept

## Commands

```bash
# Inventory how the bundle maps to C4 abstractions
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_c4.py" --bundle knowledge --inventory

# Generate L1–L4 diagram concepts + Structurizr DSL export
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_c4.py" --bundle knowledge --generate --system "My System"

# Print DSL only
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_c4.py" --bundle knowledge --dsl

# Scan existing Structurizr workspaces
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan_structurizr.py" --root . --json
```

## When designing

1. L1 — who uses the system; external systems  
2. L2 — where does the new app/service/DB sit as a **SoftwareContainer**?  
3. L3 — components inside that container  
4. L4 — modules/classes when coding  

Deep doc: `docs/c4-integration.md`.
