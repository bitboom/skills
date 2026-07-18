import importlib.util
import json
import pathlib
import tempfile
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("to_site_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


class ProjectionTest(unittest.TestCase):
    def valid_input(self):
        return {
            "schema_version": "to-site.input.v1",
            "source_manifest": {"point_sha256": "a" * 64, "language": "ko"},
            "title": "검증된 제목",
            "thesis": "검증 결과와 공개 정책은 별도다.",
            "claims": [
                {
                    "id": "C-001",
                    "text": "Verifier가 Evidence를 평가한다.",
                    "qualifiers": ["허용 policy 아래"],
                    "proof_limits": ["자동 key release는 아니다."],
                    "evidence_status": "source-confirmed",
                    "source_refs": ["S-001"],
                }
            ],
            "sources": [
                {
                    "id": "S-001",
                    "title": "RFC 9334",
                    "canonical_url": "https://www.rfc-editor.org/rfc/rfc9334",
                    "locator": "Attestation architecture",
                }
            ],
            "models": {
                "nodes": [{"id": "N-001", "label": "Verifier", "source_refs": ["S-001"]}],
                "edges": [],
                "boundaries": [],
            },
            "does_not_prove": ["Code correctness"],
        }

    def test_valid_projection_writes_traceable_artifacts(self):
        with tempfile.TemporaryDirectory() as value:
            output = pathlib.Path(value)
            projection = pipeline.validate_projection(self.valid_input())
            self.assertEqual(projection["failures"], [])
            pipeline.write_projection(self.valid_input(), output)
            semantic_map = json.loads((output / "semantic-map.json").read_text())
            self.assertEqual(semantic_map["claims"]["C-001"], ["S-001"])
            self.assertTrue((output / "claims.generated.json").exists())
            self.assertTrue((output / "sources.generated.json").exists())

    def test_validate_cli_creates_a_missing_report_directory(self):
        with tempfile.TemporaryDirectory() as value:
            root = pathlib.Path(value)
            input_path = root / "input.json"
            report_path = root / "new" / "projection-gate.json"
            input_path.write_text(json.dumps(self.valid_input()))
            status = pipeline.command_validate(types.SimpleNamespace(input=str(input_path), output=str(report_path)))
            self.assertEqual(status, 0)
            self.assertTrue(report_path.exists())

    def test_missing_proof_limit_is_rejected(self):
        data = self.valid_input()
        data["claims"][0]["proof_limits"] = []
        failures = pipeline.validate_projection(data)["failures"]
        self.assertIn("claim C-001 has no proof_limits", failures)

    def test_private_or_noncanonical_source_is_rejected(self):
        data = self.valid_input()
        data["sources"][0]["canonical_url"] = "file:///Users/example/private.md"
        failures = pipeline.validate_projection(data)["failures"]
        self.assertIn("source S-001 canonical_url must be public http(s)", failures)

    def test_missing_model_source_mapping_is_rejected(self):
        data = self.valid_input()
        data["models"]["nodes"][0]["source_refs"] = []
        failures = pipeline.validate_projection(data)["failures"]
        self.assertIn("model node N-001 has no source_refs", failures)


if __name__ == "__main__":
    unittest.main()
