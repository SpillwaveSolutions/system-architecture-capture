#!/usr/bin/env python3
"""Tests for System Architecture Capture."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sac_common import (  # noqa: E402
    dump_frontmatter,
    ensure_bundle,
    parse_frontmatter,
    slugify,
    scrub_text,
    write_concept,
)
from sac_scan_packages import scan_packages  # noqa: E402
from sac_scan_containers import scan_containers  # noqa: E402
from sac_scan_iac import scan_iac  # noqa: E402
from sac_scan_k8s import scan_k8s  # noqa: E402
from sac_scan_cicd import scan_cicd  # noqa: E402
from sac_scan_identity import scan_identity  # noqa: E402
from sac_scan import full_scan  # noqa: E402
from sac_capture import capture_scan  # noqa: E402
from sac_graph import load_graph, mermaid  # noqa: E402
from sac_blast_radius import blast_radius  # noqa: E402
from sac_validate import validate_bundle  # noqa: E402
from sac_search import search  # noqa: E402
from sac_pack import pack  # noqa: E402
from sac_orchestrate import orchestrate  # noqa: E402
from sac_ingest_wiki import ingest_dir  # noqa: E402
from sac_ingest_tickets import ingest_tickets  # noqa: E402


FIXTURE = ROOT / "tests" / "fixtures" / "demo-repo"
SAMPLE = ROOT / "sample-knowledge"


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Order Service"), "order-service")

    def test_empty(self):
        self.assertEqual(slugify("???"), "untitled")


class TestScrub(unittest.TestCase):
    def test_aws_key(self):
        clean, labels = scrub_text("key=AKIAIOSFODNN7EXAMPLE")
        self.assertIn("[REDACTED_AWS_KEY]", clean)
        self.assertTrue(labels)


class TestScanners(unittest.TestCase):
    def test_packages(self):
        pkgs = scan_packages(FIXTURE)
        names = {p["name"] for p in pkgs}
        self.assertTrue(any("@northstar" in n or "order-service" in n for n in names))
        self.assertTrue(any(p["ecosystem"] in ("npm", "maven") for p in pkgs))

    def test_containers(self):
        data = scan_containers(FIXTURE)
        self.assertGreaterEqual(len(data["images"]), 1)

    def test_iac(self):
        stacks = scan_iac(FIXTURE)
        tools = {s["tool"] for s in stacks}
        self.assertIn("terraform", tools)
        self.assertIn("helm", tools)

    def test_k8s(self):
        docs = scan_k8s(FIXTURE)
        kinds = {d["kind"] for d in docs}
        self.assertIn("Deployment", kinds)

    def test_cicd(self):
        pipes = scan_cicd(FIXTURE)
        self.assertTrue(any(p["platform"] == "github-actions" for p in pipes))

    def test_identity(self):
        data = scan_identity(FIXTURE)
        providers = {p["provider"] for p in data["identity_providers"]}
        self.assertIn("auth0", providers)


class TestCaptureAndGraph(unittest.TestCase):
    def test_capture_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "knowledge"
            ensure_bundle(bundle, "Test System")
            scan = full_scan(FIXTURE)
            stats = capture_scan(bundle, scan, system_name="Test System")
            self.assertGreater(stats["created"] + stats["updated"], 0)
            g = load_graph(bundle)
            self.assertGreater(g["node_count"], 3)
            m = mermaid(g)
            self.assertIn("flowchart", m)
            v = validate_bundle(bundle)
            self.assertTrue(v["ok"], v["issues"][:5])


class TestSampleKnowledge(unittest.TestCase):
    def test_sample_valid(self):
        v = validate_bundle(SAMPLE)
        self.assertGreaterEqual(v["node_count"], 20)
        self.assertGreaterEqual(v["edge_count"], 20)
        self.assertEqual(v["errors"], 0, v["issues"])

    def test_sample_search(self):
        r = search(SAMPLE, "payment kafka")
        self.assertGreater(r["count"], 0)

    def test_sample_pack(self):
        p = pack(SAMPLE, "services/order-service.md", hops=2)
        self.assertGreaterEqual(p["node_count"], 3)
        self.assertIn("flowchart", p["mermaid"])

    def test_blast_radius(self):
        g = load_graph(SAMPLE)
        br = blast_radius(g, "/services/order-service.md", hops=2)
        self.assertGreater(br["impacted_count"], 0)


class TestOrchestrate(unittest.TestCase):
    def test_orchestrate_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            host = Path(td)
            result = orchestrate(
                host,
                [FIXTURE],
                system_name="Fixture System",
                bundle_name="knowledge",
                wiki=ROOT / "tests" / "fixtures" / "wiki",
                tickets=ROOT / "tests" / "fixtures" / "tickets.json",
            )
            self.assertTrue(result["validation"]["ok"] or result["graph"]["node_count"] > 0)
            self.assertGreater(result["graph"]["node_count"], 5)


class TestIngest(unittest.TestCase):
    def test_wiki_and_tickets(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "k"
            ensure_bundle(bundle)
            w = ingest_dir(bundle, ROOT / "tests" / "fixtures" / "wiki")
            self.assertGreater(w["created"] + w["updated"], 0)
            t = ingest_tickets(
                bundle,
                json.loads((ROOT / "tests" / "fixtures" / "tickets.json").read_text()),
            )
            self.assertGreater(t["created"] + t["updated"], 0)


class TestC4(unittest.TestCase):
    def test_inventory_and_generate(self):
        from sac_c4 import inventory, generate_views, classify_c4
        self.assertEqual(classify_c4("Service"), "Container")
        self.assertEqual(classify_c4("ContainerImage"), None)  # Docker ≠ C4 container
        self.assertEqual(classify_c4("SoftwareContainer"), "Container")
        self.assertEqual(classify_c4("Person"), "Person")
        inv = inventory(SAMPLE)
        self.assertGreaterEqual(len(inv["SoftwareSystem"]), 1)
        views = generate_views(SAMPLE, system="Northstar Commerce", write=False)
        self.assertIn("flowchart", views["context"]["mermaid"])
        self.assertIn("workspace", views["structurizr_dsl"])

    def test_structurizr_scan(self):
        from sac_scan_structurizr import scan_structurizr
        # scan sample dsl if present
        data = scan_structurizr(SAMPLE)
        self.assertIn("containers", data)


class TestDiagramsAndCode(unittest.TestCase):
    def test_scan_diagrams_from_sample(self):
        from sac_scan_diagrams import scan_diagrams
        # sample-knowledge has mermaid fences
        found = scan_diagrams(ROOT / "sample-knowledge")
        self.assertGreaterEqual(len(found), 5)
        formats = {d["format"] for d in found}
        self.assertTrue("mermaid" in formats or "plantuml" in formats)
        kinds = {d["kind"] for d in found}
        self.assertTrue(any(k.endswith("Diagram") or k == "Wireframe" for k in kinds))

    def test_scan_code_structure_on_scripts(self):
        from sac_scan_code_structure import scan_code_structure
        data = scan_code_structure(ROOT / "scripts")
        self.assertGreater(len(data["modules"]), 0)
        self.assertGreater(len(data["functions"]), 0)

    def test_types_include_code_and_diagrams(self):
        from sac_validate import load_schema_registry
        types = {t["type"] for t in load_schema_registry()["types"]}
        for name in ("Module", "Class", "Method", "Function", "Wireframe",
                     "ArchitectureDiagram", "ClassDiagram", "ErdDiagram",
                     "SequenceDiagram", "StateMachineDiagram"):
            self.assertIn(name, types)


class TestSchemaPack(unittest.TestCase):
    def test_registry_loads(self):
        from sac_validate import load_schema_registry
        reg = load_schema_registry()
        types = {x["type"] for x in reg["types"]}
        self.assertIn("Service", types)
        self.assertIn("Database", types)
        self.assertIn("Cache", types)
        self.assertIn("Event", types)
        self.assertIn("WebApp", types)
        self.assertIn("DecisionRecord", types)
        self.assertIn("TicketLink", types)
        self.assertIn("calls", reg["relations"]["all"])

    def test_sample_schema_validate(self):
        v = validate_bundle(SAMPLE, schema=True)
        self.assertEqual(v["errors"], 0)
        self.assertGreaterEqual(v["node_count"], 20)


class TestFrontmatterRoundTrip(unittest.TestCase):
    """parse(dump(x)) == x.

    Regression: `_fmt_scalar` escaped backslashes and quotes on write, `_scalar`
    stripped only the surrounding quotes on read. Every write-modify-write cycle
    re-escaped already-escaped text, doubling the backslash count each pass, so
    any maintenance script that edited one field corrupted every quoted string
    in the file. It was self-concealing too: reading back with the same parser
    returned a value that looked correct.
    """

    VALUES = [
        '[{"a":"b"}]',          # JSON payload — the case that surfaced this
        "back\\slash",
        'quote"inside',
        'both\\"mixed',
        ":colon",               # forces quoting via the punctuation test
        "plain",
    ]

    def test_single_round_trip_is_identity(self):
        for v in self.VALUES:
            with self.subTest(value=v):
                fm = {"type": "Concept", "title": "T", "v": v}
                self.assertEqual(parse_frontmatter(dump_frontmatter(fm))[0]["v"], v)

    def test_repeated_round_trips_do_not_grow(self):
        fm = {"type": "Concept", "title": "T", "sources_json": '[{"a":"b"}]'}
        first = None
        for _ in range(5):
            text = dump_frontmatter(fm)
            line = [l for l in text.splitlines() if l.startswith("sources_json")][0]
            if first is None:
                first = line
            self.assertEqual(line, first, "escaping grew across a round trip")
            fm, _ = parse_frontmatter(text)


class TestWriteConcept(unittest.TestCase):
    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td)
            ensure_bundle(bundle)
            fm = {"type": "Service", "title": "X", "truth_state": "current", "stable_timestamp": True}
            _, a = write_concept(bundle, "services/x.md", fm, "# X\n\nBody\n")
            _, b = write_concept(bundle, "services/x.md", {**fm}, "# X\n\nBody\n")
            self.assertEqual(a, "created")
            self.assertEqual(b, "skipped")


if __name__ == "__main__":
    unittest.main()
