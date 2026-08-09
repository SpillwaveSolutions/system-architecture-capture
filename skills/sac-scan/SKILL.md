---
name: sac-scan
description: Run deterministic architecture scanners (packages, containers, IaC, K8s, CI/CD, identity) against a code root without writing knowledge.
---

# SAC Scan

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan.py" --root <path> --json
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sac_scan.py" --root <path> --domains packages,iac,cicd --json
```

Individual scanners: `sac_scan_packages.py`, `sac_scan_containers.py`, `sac_scan_iac.py`, `sac_scan_k8s.py`, `sac_scan_cicd.py`, `sac_scan_identity.py`.

Default scan domains include `diagrams` (Mermaid/PlantUML) and `code` (Module/Class/Method/Function).
