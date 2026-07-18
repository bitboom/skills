import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "export_archify_svg.py"
SPEC = importlib.util.spec_from_file_location("to_site_archify_svg", MODULE_PATH)
archify_svg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archify_svg)


class ArchifySvgExportTest(unittest.TestCase):
    def test_export_inlines_style_and_writes_well_formed_svg(self):
        html = """<html><head><style>:root { --ink: #123; } .node { fill: var(--ink); }</style><script>bad()</script></head><body><svg viewBox='0 0 10 10'><rect class='node' width='10' height='10'/></svg></body></html>"""
        with tempfile.TemporaryDirectory() as value:
            source = pathlib.Path(value) / "source.html"
            target = pathlib.Path(value) / "out.svg"
            source.write_text(html)
            archify_svg.export_svg(source, target)
            rendered = target.read_text()
            self.assertIn('xmlns="http://www.w3.org/2000/svg"', rendered)
            self.assertIn('<style><![CDATA[', rendered)
            self.assertIn('data-theme="dark"', rendered)
            self.assertNotIn('<script>', rendered)


if __name__ == "__main__":
    unittest.main()
