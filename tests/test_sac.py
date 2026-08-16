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
    append_log,
    CATALOGS,
    dump_frontmatter,
    ensure_bundle,
    parse_frontmatter,
    refresh_catalog_index,
    resolve_knowledge_root,
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
AUTHOR = "claude-code/lumenfield-detector"


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
            stats = capture_scan(bundle, scan, system_name="Test System", author=AUTHOR)
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
                author=AUTHOR,
            )
            self.assertTrue(result["validation"]["ok"] or result["graph"]["node_count"] > 0)
            self.assertGreater(result["graph"]["node_count"], 5)


class TestIngest(unittest.TestCase):
    def test_wiki_and_tickets(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "k"
            ensure_bundle(bundle)
            w = ingest_dir(bundle, ROOT / "tests" / "fixtures" / "wiki", author=AUTHOR)
            self.assertGreater(w["created"] + w["updated"], 0)
            t = ingest_tickets(
                bundle,
                json.loads((ROOT / "tests" / "fixtures" / "tickets.json").read_text()),
                author=AUTHOR,
            )
            self.assertGreater(t["created"] + t["updated"], 0)


class TestTicketNormalization(unittest.TestCase):
    """Raw Jira REST nests everything but `key` under `fields{}`."""

    def test_jira_rest_shape(self):
        from sac_ingest_tickets import normalize_ticket
        got = normalize_ticket({
            "key": "ABC-1",
            "fields": {
                "summary": "Configure the widget",
                "status": {"name": "Done"},
                "labels": ["x"],
                "issuetype": {"name": "Epic"},
                "description": {"type": "doc", "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": "Body here"}]}]},
            },
        })
        self.assertEqual(got["title"], "Configure the widget")
        self.assertEqual(got["status"], "Done")
        self.assertEqual(got["labels"], ["x"])
        self.assertEqual(got["type"], "epic")
        self.assertIn("Body here", got["body"])

    def test_flat_status_is_not_discarded(self):
        """Independent precedence bug: a flat `"status": "Done"` became
        "unknown" whenever `state` was absent, because the conditional read
        `state` in the else branch."""
        from sac_ingest_tickets import normalize_ticket
        self.assertEqual(normalize_ticket({"key": "A-1", "status": "Done"})["status"], "Done")

    def test_github_shape_still_works(self):
        from sac_ingest_tickets import normalize_ticket
        got = normalize_ticket({"number": 7, "title": "T", "state": "open", "body": "b"})
        self.assertEqual(got["status"], "open")
        self.assertEqual(got["title"], "T")


class TestWikiClassify(unittest.TestCase):
    def test_runbook_gets_the_runbook_type(self):
        """`Runbook` is a registered type; returning `Design` looked like a
        leftover, and the skill advertises runbook handling."""
        from sac_ingest_wiki import classify
        from sac_validate import load_schema_registry
        self.assertIn("Runbook", {t["type"] for t in load_schema_registry()["types"]})
        self.assertEqual(classify("oncall-runbook.md", ""), "Runbook")

    def test_default_type_is_caller_controlled(self):
        from sac_ingest_wiki import classify
        self.assertEqual(classify("requirements.md", ""), "Discovery")
        self.assertEqual(classify("requirements.md", "", default="Requirement"), "Requirement")


class TestCurateHook(unittest.TestCase):
    def test_hook_script_is_not_a_no_op(self):
        """It previously consisted of `exit 0`, so the registered PostToolUse
        hook fired and did nothing. Guard against silently reverting to that."""
        script = (ROOT / "scripts" / "sac-curate.sh").read_text(encoding="utf-8")
        self.assertIn("refresh_catalog_index", script)

    def test_hook_refreshes_the_edited_files_catalog(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "knowledge"
            (bundle / "services").mkdir(parents=True)
            (bundle / "index.md").write_text(
                "---\ntype: Bundle\ntitle: T\n---\n\n# T\n", encoding="utf-8")
            edited = bundle / "services" / "x.md"
            edited.write_text(
                "---\ntype: Service\ntitle: Alpha Service\n---\n\n# Alpha\n", encoding="utf-8")
            env = {
                **__import__("os").environ,
                "CLAUDE_PLUGIN_ROOT": str(ROOT),
                "CLAUDE_TOOL_FILE_PATH": str(edited),
            }
            subprocess.run(["bash", str(ROOT / "scripts" / "sac-curate.sh")],
                           env=env, capture_output=True, timeout=60)
            index = bundle / "services" / "index.md"
            self.assertTrue(index.is_file(), "hook did not create the catalog index")
            self.assertIn("Alpha Service", index.read_text(encoding="utf-8"))


class TestAppendLog(unittest.TestCase):
    def test_entries_are_not_lost(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td)
            ensure_bundle(bundle)
            for i in range(6):
                append_log(bundle, f"entry {i}")
            body = (bundle / "log.md").read_text(encoding="utf-8")
        for i in range(6):
            self.assertIn(f"entry {i}", body)

    def test_no_sidecar_lock_file_is_left_in_the_bundle(self):
        """The lock targets the log itself; a `.lock` sidecar would show up in
        git status and in any directory walk over the bundle."""
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td)
            ensure_bundle(bundle)
            append_log(bundle, "one")
            self.assertEqual(list(bundle.glob("*.lock")), [])


class TestWriteConceptModes(unittest.TestCase):
    def _bundle(self, td):
        b = Path(td)
        ensure_bundle(b)
        return b

    def test_create_only_does_not_touch_an_existing_body(self):
        """`merge` protects frontmatter, never the body — a non-empty body
        always wins. Right for re-capture, catastrophic for a scaffolding pass
        re-run after enrichment, which flattens every concept back to a stub and
        reports "updated" for each one."""
        with tempfile.TemporaryDirectory() as td:
            b = self._bundle(td)
            fm = {"type": "Service", "title": "X"}
            write_concept(b, "services/x.md", fm, "# X\n\nEnriched body\n")
            _, action = write_concept(b, "services/x.md", fm, "# X\n\nStub\n",
                                      create_only=True)
            self.assertEqual(action, "exists")
            self.assertIn("Enriched body", (b / "services" / "x.md").read_text(encoding="utf-8"))

    def test_default_still_replaces_the_body(self):
        """Unchanged behaviour: this is what re-capture depends on."""
        with tempfile.TemporaryDirectory() as td:
            b = self._bundle(td)
            fm = {"type": "Service", "title": "X"}
            write_concept(b, "services/x.md", fm, "# X\n\nOld\n")
            _, action = write_concept(b, "services/x.md", fm, "# X\n\nNew\n")
            self.assertEqual(action, "updated")
            self.assertIn("New", (b / "services" / "x.md").read_text(encoding="utf-8"))

    def test_truth_state_refusal_is_distinguishable_from_a_no_op(self):
        """Both used to return "skipped", so a caller could not tell "already
        correct" from "refused to write, your change was discarded"."""
        with tempfile.TemporaryDirectory() as td:
            b = self._bundle(td)
            write_concept(b, "services/x.md",
                          {"type": "Service", "title": "X", "truth_state": "superseded"},
                          "# X\n\nBody\n")
            _, refused = write_concept(b, "services/x.md",
                                       {"type": "Service", "title": "X"}, "# X\n\nNew\n")
            self.assertEqual(refused, "refused")

            b2 = Path(td) / "b2"
            ensure_bundle(b2)
            fm = {"type": "Service", "title": "Y", "stable_timestamp": True}
            write_concept(b2, "services/y.md", fm, "# Y\n\nSame\n")
            _, noop = write_concept(b2, "services/y.md", {**fm}, "# Y\n\nSame\n")
            self.assertEqual(noop, "skipped")


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


class TestCatalogIndex(unittest.TestCase):
    def _bundle(self, td, title):
        bundle = Path(td)
        ensure_bundle(bundle)
        (bundle / "services").mkdir(exist_ok=True)
        (bundle / "services" / "x.md").write_text(
            f"---\ntype: Service\ntitle: {title}\n---\n\n# X\n", encoding="utf-8")
        refresh_catalog_index(bundle, "services")
        return (bundle / "services" / "index.md").read_text(encoding="utf-8")

    def test_bracketed_title_still_yields_a_parseable_link(self):
        """A title like `[AREA] Thing` must not render as `[[AREA] Thing](...)`.

        okf-graph's link regex cannot match a nested-bracket label, and the
        result is a MISSING edge, not a broken one — validate only reports
        broken edges, so the concept silently loses its catalog backlink."""
        import re
        with tempfile.TemporaryDirectory() as td:
            body = self._bundle(td, "[AREA] Thing")
        line = [l for l in body.splitlines() if l.startswith("- [")][0]

        # 1. The brackets are backslash-escaped, which is what CommonMark asks
        #    for and what stops the label from opening a nested pair.
        self.assertIn(r"\[AREA\]", line, f"label not escaped: {line!r}")

        # 2. A bracket-aware reader recovers the target.
        aware = re.compile(r"\[((?:\\.|\[[^\[\]]*\]|[^\]])+)\]\(([^)]+)\)")
        found = aware.findall(line)
        self.assertTrue(found, f"unparseable catalog entry: {line!r}")
        self.assertEqual(found[0][1], "/services/x.md")

        # 3. Worth stating explicitly: escaping alone does NOT rescue a reader
        #    whose label class is `[^\]]+`, because that class has no notion of
        #    an escape and still stops at the literal `]`. This fix therefore
        #    depends on the matching reader change landing too — neither half
        #    is sufficient alone.
        strict = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.assertFalse(strict.findall(line))

    def test_refuses_a_catalog_this_plugin_does_not_declare(self):
        """Bundles are shared with sibling plugins that own other catalogs and
        render them differently. Rewriting one of theirs into our format is not
        ours to do."""
        self.assertNotIn("lakehouses", CATALOGS)
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td)
            ensure_bundle(bundle)
            foreign = bundle / "lakehouses"
            foreign.mkdir()
            marker = "- [Untouched](/lakehouses/a.md) · annotated\n"
            (foreign / "index.md").write_text(marker, encoding="utf-8")
            refresh_catalog_index(bundle, "lakehouses")
            self.assertEqual((foreign / "index.md").read_text(encoding="utf-8"), marker)


class TestResolveKnowledgeRoot(unittest.TestCase):
    def test_configured_root_wins_when_initialized(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            for name in ("knowledge", "sample-knowledge"):
                (repo / name).mkdir()
                (repo / name / "index.md").write_text("# x\n", encoding="utf-8")
            self.assertEqual(resolve_knowledge_root(repo).name, "knowledge")

    def test_falls_back_to_sample_only_when_intended_root_is_not_a_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "knowledge").mkdir()          # exists but has no index.md
            (repo / "sample-knowledge").mkdir()
            (repo / "sample-knowledge" / "index.md").write_text("# x\n", encoding="utf-8")
            self.assertEqual(resolve_knowledge_root(repo).name, "sample-knowledge")


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


class TestRequiredIdentity(unittest.TestCase):
    def test_resolve_author_fail_closed(self):
        import os
        from sac_common import resolve_author

        prev = os.environ.pop("SECOND_BRAIN_IDENTITY", None)
        try:
            with self.assertRaises(SystemExit):
                resolve_author(None)
            with self.assertRaises(SystemExit):
                resolve_author("")
            self.assertEqual(
                resolve_author("grok-bot/northstar-console"),
                "grok-bot/northstar-console",
            )
        finally:
            if prev is not None:
                os.environ["SECOND_BRAIN_IDENTITY"] = prev

    def test_flag_beats_env(self):
        import os
        from sac_common import resolve_author

        prev = os.environ.get("SECOND_BRAIN_IDENTITY")
        os.environ["SECOND_BRAIN_IDENTITY"] = "grok-bot/northstar-console"
        try:
            self.assertEqual(resolve_author(None), "grok-bot/northstar-console")
            self.assertEqual(resolve_author(AUTHOR), AUTHOR)
        finally:
            if prev is None:
                os.environ.pop("SECOND_BRAIN_IDENTITY", None)
            else:
                os.environ["SECOND_BRAIN_IDENTITY"] = prev

    def test_capture_stamps_author_and_emits_event(self):
        from sac_common import parse_frontmatter, path_for_type

        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "knowledge"
            ensure_bundle(bundle, "Test System")
            scan = full_scan(FIXTURE)
            capture_scan(bundle, scan, system_name="Test System", author=AUTHOR)
            rel = path_for_type("System", "test-system")
            fm, _ = parse_frontmatter((bundle / rel.lstrip("/")).read_text(encoding="utf-8"))
            self.assertEqual(fm.get("author"), AUTHOR)
            events = [
                p
                for p in (bundle / "write-events").glob("*.md")
                if p.name != "index.md"
            ]
            self.assertGreater(len(events), 0, "expected WriteEvent nodes")
            ev_fm, _ = parse_frontmatter(events[0].read_text(encoding="utf-8"))
            self.assertEqual(ev_fm.get("type"), "WriteEvent")
            self.assertEqual(ev_fm.get("author"), AUTHOR)

    def test_cli_capture_without_identity_fails(self):
        import os
        import subprocess

        env = os.environ.copy()
        env.pop("SECOND_BRAIN_IDENTITY", None)
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sac_capture.py"),
                    "--repo",
                    td,
                    "--root",
                    str(FIXTURE),
                    "--system",
                    "X",
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("identity", (r.stdout + r.stderr).lower())


if __name__ == "__main__":
    unittest.main()

