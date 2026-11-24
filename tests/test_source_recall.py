"""Check a wiki-ingested fact, its origin, and its replacement offline."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sac_common import ensure_bundle, parse_frontmatter
from sac_ingest_wiki import ingest_dir
from sac_search import search
from sac_validate import validate_bundle


class SourceRecallTests(unittest.TestCase):
    def test_wiki_capture_to_original_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "knowledge"
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            ensure_bundle(bundle)
            west = wiki / "west.md"
            west.write_text("# West relay schedule\n\nThe west relay archives amber samples for 81 evenings. Retention record.\n")
            east = wiki / "east.md"
            expected_path = "discoveries/wiki-east.md"
            for days in (12, 37):
                fact = f"The east relay archives amber samples for {days} evenings."
                east.write_text(f"# East relay retention\n\n{fact}\n")
                stats = ingest_dir(bundle, wiki, author="fixture")
                if days == 12:
                    self.assertEqual(stats["created"], 2)
                else:
                    self.assertEqual(stats["updated"], 1)
                self.assertTrue(validate_bundle(bundle, schema=True)["ok"])
                for query in ("east relay retention", "amber samples east", "east archives evenings", "amber retention"):
                    with self.subTest(query=query, days=days):
                        hits = search(bundle, query, limit=3)["results"]
                        paths = [row["path"] for row in hits]
                        self.assertEqual(paths[:1], [expected_path], paths)
                        if query == "amber retention":
                            self.assertEqual(paths[1:], ["discoveries/wiki-west.md"])
                            self.assertGreater(hits[0]["score"], hits[1]["score"])
                        hit = hits[0]
                        fm, body = parse_frontmatter((bundle / hit["path"]).read_text())
                        cited = Path(fm["source_path"])
                        self.assertEqual(cited, east)
                        self.assertIn(fact, cited.read_text().splitlines())
                        self.assertIn(fact, body.splitlines())
                        self.assertNotIn("81 evenings", body)
                        if days == 37:
                            self.assertNotIn("12 evenings", body)
                self.assertEqual(search(bundle, "ultraviolet glacier", limit=3)["results"], [])


if __name__ == "__main__":
    unittest.main()
