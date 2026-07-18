import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_site.py"
SPEC = importlib.util.spec_from_file_location("to_site_validate", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class SiteValidationTest(unittest.TestCase):
    def make_site(self, root, include_claim=True):
        dist = pathlib.Path(root) / "dist"
        (dist / "mechanism").mkdir(parents=True)
        (dist / "evidence").mkdir(parents=True)
        claim = ' data-claim-id="C-001" data-source-id="S-001"' if include_claim else ""
        (dist / "index.html").write_text(f"<main{claim}><a href='/mechanism/'>Mechanism</a></main>")
        (dist / "mechanism" / "index.html").write_text("<main><a href='/evidence/'>Evidence</a></main>")
        (dist / "evidence" / "index.html").write_text(f"<main{claim}></main>")
        semantic = {"claims": {"C-001": ["S-001"]}, "sources": ["S-001"]}
        semantic_path = pathlib.Path(root) / "semantic-map.json"
        semantic_path.write_text(json.dumps(semantic))
        return dist, semantic_path

    def test_valid_dist_passes(self):
        with tempfile.TemporaryDirectory() as value:
            dist, semantic = self.make_site(value)
            result = validator.validate_dist(dist, semantic)
            self.assertEqual(result["failures"], [])

    def test_missing_claim_hook_fails(self):
        with tempfile.TemporaryDirectory() as value:
            dist, semantic = self.make_site(value, include_claim=False)
            result = validator.validate_dist(dist, semantic)
            self.assertIn("claim C-001 is not rendered in dist", result["failures"])

    def test_data_urls_are_not_treated_as_internal_links(self):
        with tempfile.TemporaryDirectory() as value:
            dist, semantic = self.make_site(value)
            index = dist / "index.html"
            index.write_text(index.read_text() + "<link href='data:image/svg+xml,test'>")
            result = validator.validate_dist(dist, semantic)
            self.assertEqual(result["failures"], [])

    def test_private_path_leak_fails(self):
        with tempfile.TemporaryDirectory() as value:
            dist, semantic = self.make_site(value)
            (dist / "index.html").write_text("/Users/private/input.md")
            result = validator.validate_dist(dist, semantic)
            self.assertTrue(any("private path leak" in item for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
