#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m py_compile scripts/*.py
python3 tests/test_sac.py -v
python3 tests/test_isolation.py
python3 scripts/sac_validate.py --bundle sample-knowledge --schema --json | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['errors']==0 and d['node_count']>=20, d"
python3 scripts/sac_doctor.py --bundle sample-knowledge --json | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['node_count']>=20, d"
python3 scripts/sac_search.py "order payment" --bundle sample-knowledge --json | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['count']>=1, d"
python3 scripts/sac_pack.py services/order-service.md --bundle sample-knowledge --json | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['node_count']>=3, d"
python3 scripts/sac_graph.py --bundle sample-knowledge --mermaid | grep -q flowchart
python3 scripts/sac_scan.py --root tests/fixtures/demo-repo --json | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['summary']['packages']>=1, d"
echo "CI OK"
