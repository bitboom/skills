import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
PIPELINE = SKILL / "scripts" / "pipeline.py"
RENDER_HELPER = SKILL / "scripts" / "render_deck.py"
SPEC = importlib.util.spec_from_file_location("to_deck_render_deck", RENDER_HELPER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load render helper: {RENDER_HELPER}")
RENDER_DECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDER_DECK)

PIPELINE_SPEC = importlib.util.spec_from_file_location("to_deck_pipeline", PIPELINE)
if PIPELINE_SPEC is None or PIPELINE_SPEC.loader is None:
    raise RuntimeError(f"cannot load pipeline: {PIPELINE}")
PIPELINE_MODULE = importlib.util.module_from_spec(PIPELINE_SPEC)
PIPELINE_SPEC.loader.exec_module(PIPELINE_MODULE)


def png_header(width: int, height: int) -> bytes:
    payload = bytearray(b"\x89PNG\r\n\x1a\n" + b"\0" * 16)
    payload[16:20] = width.to_bytes(4, "big")
    payload[20:24] = height.to_bytes(4, "big")
    return bytes(payload)


def manifest_payload(image: Path, *, slide_count: int = 1, slides=None) -> dict:
    return {
        "schema_version": 2,
        "renderer": "soffice",
        "renderer_version": "LibreOffice 26",
        "command": "soffice --headless",
        "generated_at": "2026-07-17T00:00:00Z",
        "toolchain": {
            "renderer": "soffice", "renderer_version": "LibreOffice 26",
            "command": "soffice --headless", "environment": "Darwin arm64",
        },
        "producer": {"kind": "manual", "command": "manual authoring"},
        "slide_count": slide_count,
        "slides": slides or [{
            "path": image.name, "width": 1600, "height": 900,
            "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
        }],
    }


class RenderDeckCommandTest(unittest.TestCase):
    def test_render_helper_exposes_a_cli_contract(self):
        result = subprocess.run(
            [sys.executable, str(RENDER_HELPER), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--deck", result.stdout)
        self.assertIn("--manifest", result.stdout)
        self.assertIn("--output-dir", result.stdout)
    def test_manifest_rejects_duplicate_paths_and_nonpositive_dimensions(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            image = root / "slide-1.png"
            image.write_bytes(png_header(1600, 900))
            slide = {
                "path": image.name,
                "width": -1,
                "height": 0,
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
            }
            manifest = root / "render-manifest.json"
            manifest.write_text(json.dumps(manifest_payload(
                image, slide_count=2, slides=[slide, dict(slide)]
            )), encoding="utf-8")
            failures = PIPELINE_MODULE.validate_render_manifest(manifest, 2)
            self.assertTrue(any("duplicates" in item for item in failures))
            self.assertTrue(any("positive" in item for item in failures))

    def test_manifest_rejects_dimensions_that_disagree_with_png_metadata(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            image = root / "slide-1.png"
            image.write_bytes(png_header(1600, 900))
            manifest = root / "render-manifest.json"
            payload = manifest_payload(image)
            payload["slides"][0]["width"] = 1601
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            failures = PIPELINE_MODULE.validate_render_manifest(manifest, 1)
            self.assertTrue(any("dimensions do not match" in item for item in failures))

    def test_manifest_rejects_symlink_that_resolves_outside_manifest_directory(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            outside = root.parent / f"{root.name}-outside.png"
            self.addCleanup(lambda: outside.unlink(missing_ok=True))
            outside.write_bytes(png_header(1600, 900))
            render = root / "render"
            render.mkdir()
            link = render / "slide-1.png"
            link.symlink_to(outside)
            manifest = root / "render-manifest.json"
            payload = manifest_payload(link)
            payload["slides"][0]["path"] = "render/slide-1.png"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            failures = PIPELINE_MODULE.validate_render_manifest(manifest, 1)
            self.assertTrue(any("resolves outside" in item for item in failures))

    def test_verify_package_emits_a_failed_gate_for_invalid_pptx(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            archive = root / "invalid-deck.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("slides/v02-deck.pptx", "not a PPTX")
                bundle.writestr("slides/v02-render-manifest.json", "{}")
            output = root / "verify.json"
            result = subprocess.run([
                sys.executable, str(PIPELINE), "verify-package", "--archive", str(archive),
                "--deck", "slides/v02-deck.pptx", "--render-manifest", "slides/v02-render-manifest.json",
                "--output", str(output),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertFalse(json.loads(output.read_text())["passed"])

    def test_verify_package_rejects_a_high_compression_member_before_extraction(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            archive = root / "compressed.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr("padding.bin", b"0" * (1024 * 1024))
            output = root / "verify.json"
            result = subprocess.run([
                sys.executable, str(PIPELINE), "verify-package", "--archive", str(archive),
                "--deck", "slides/v02-deck.pptx", "--render-manifest", "slides/v02-render-manifest.json",
                "--output", str(output),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            payload = json.loads(output.read_text())
            self.assertTrue(any("compression ratio" in item for item in payload["failures"]))

    def test_verify_package_accepts_a_clean_extracted_relative_manifest(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            deck = root / "slides" / "v02-deck.pptx"
            image = root / "slides" / "v02-render" / "slide-1.png"
            manifest = root / "slides" / "v02-render-manifest.json"
            deck.parent.mkdir(parents=True)
            image.parent.mkdir(parents=True)
            with zipfile.ZipFile(deck, "w") as pptx:
                pptx.writestr("ppt/slides/slide1.xml", "<slide/>")
            image.write_bytes(png_header(1600, 900))
            manifest.write_text(json.dumps({
                "schema_version": 2,
                "renderer": "soffice",
                "renderer_version": "LibreOffice 26",
                "command": "soffice --headless",
                "generated_at": "2026-07-17T00:00:00Z",
                "toolchain": {
                    "renderer": "soffice", "renderer_version": "LibreOffice 26",
                    "command": "soffice --headless", "environment": "Darwin arm64",
                },
                "producer": {"kind": "manual", "command": "manual authoring"},
                "slide_count": 1,
                "slides": [{
                    "path": "v02-render/slide-1.png", "width": 1600, "height": 900,
                    "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                }],
            }, indent=2), encoding="utf-8")
            archive = root / "review-trail.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                for path in (deck, image, manifest):
                    bundle.write(path, path.relative_to(root).as_posix())
            result_path = root / "verify.json"
            result = subprocess.run([
                sys.executable, str(PIPELINE), "verify-package", "--archive", str(archive),
                "--deck", "slides/v02-deck.pptx", "--render-manifest", "slides/v02-render-manifest.json",
                "--output", str(result_path),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result_path.read_text())["passed"])

    def test_verify_package_rejects_archive_member_path_escape(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("../escape.txt", "not allowed")
            result_path = root / "verify.json"
            result = subprocess.run([
                sys.executable, str(PIPELINE), "verify-package", "--archive", str(archive),
                "--deck", "slides/v02-deck.pptx", "--render-manifest", "slides/v02-render-manifest.json",
                "--output", str(result_path),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result_path.read_text())
            self.assertTrue(any("escapes extraction root" in item for item in payload["failures"]))

    def test_rendered_slide_paths_use_numeric_order_and_reject_gaps(self):
        with tempfile.TemporaryDirectory() as value:
            output = Path(value)
            for number in (1, 2, 10):
                (output / f"slide-{number}.png").write_bytes(png_header(1600, 900))
            with self.assertRaisesRegex(RuntimeError, "contiguous"):
                RENDER_DECK.rendered_slide_paths(output)
            (output / "slide-3.png").write_bytes(png_header(1600, 900))
            for number in range(4, 10):
                (output / f"slide-{number}.png").write_bytes(png_header(1600, 900))
            self.assertEqual(
                [path.name for path in RENDER_DECK.rendered_slide_paths(output)],
                [f"slide-{number}.png" for number in range(1, 11)],
            )

    def test_remove_stale_render_outputs_removes_prior_gate_inputs(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            output = root / "render"
            output.mkdir()
            pdf = output / "deck.pdf"
            text = root / "deck-text.md"
            manifest = root / "render-manifest.json"
            for path in (output / "slide-1.png", pdf, text, manifest):
                path.write_bytes(b"stale")
            RENDER_DECK.remove_stale_render_outputs(output, pdf, text, manifest)
            self.assertFalse(any(output.glob("slide-*.png")))
            self.assertFalse(pdf.exists())
            self.assertFalse(text.exists())
            self.assertFalse(manifest.exists())

    def test_build_manifest_keeps_rendered_paths_inside_manifest_directory(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            manifest_path = root / "slides" / "v02-render-manifest.json"
            image = root / "slides" / "v02-render" / "slide-1.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"rendered-slide")
            manifest = RENDER_DECK.build_manifest(
                manifest_path=manifest_path,
                rendered_slides=[image],
                slide_size=(1600, 900),
                toolchain={
                    "renderer": "soffice", "renderer_version": "LibreOffice 26",
                    "command": "soffice --headless", "environment": "Darwin arm64",
                },
                producer={"kind": "manual", "command": "manual authoring"},
                generated_at="2026-07-17T00:00:00Z",
            )
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["slides"][0]["path"], "v02-render/slide-1.png")

    def test_build_manifest_rejects_rendered_paths_outside_manifest_directory(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            manifest_path = root / "slides" / "v02-render-manifest.json"
            image = root / "outside" / "slide-1.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"rendered-slide")
            with self.assertRaises(ValueError):
                RENDER_DECK.build_manifest(
                    manifest_path=manifest_path,
                    rendered_slides=[image],
                    slide_size=(1600, 900),
                    toolchain={
                        "renderer": "soffice", "renderer_version": "LibreOffice 26",
                        "command": "soffice --headless", "environment": "Darwin arm64",
                    },
                    producer={"kind": "manual", "command": "manual authoring"},
                    generated_at="2026-07-17T00:00:00Z",
                )


if __name__ == "__main__":
    unittest.main()
