"""Regression tests for the Point prose-preservation To Deck contract."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
DELIVERY = (ROOT / "references" / "delivery-modes.md").read_text(encoding="utf-8")
RUBRICS = (ROOT / "references" / "rubrics.md").read_text(encoding="utf-8")
PROSE = (ROOT / "references" / "prose-preservation.md").read_text(encoding="utf-8")
CONTRACT = (ROOT / "references" / "run-contract.md").read_text(encoding="utf-8")


class PointProsePreservationTests(unittest.TestCase):
    def test_skill_reads_canonical_point_before_any_projection(self) -> None:
        self.assertIn("canonical Point package", SKILL)
        self.assertIn("Read canonical `point.md` as the prose source", SKILL)
        self.assertIn("fail closed and return to Point", SKILL)

    def test_structural_contract_requires_a_prose_trace(self) -> None:
        self.assertIn("prose-trace.json", DELIVERY)
        self.assertIn("reader-visible slide sentence", DELIVERY)
        self.assertIn("context dependency", DELIVERY)
        self.assertIn("prose-trace.json", CONTRACT)

    def test_security_relation_cannot_be_reduced_to_labels(self) -> None:
        self.assertIn("actor → artifact → check → separate policy owner → action / failure outcome", PROSE)
        self.assertIn("diagram label", PROSE)
        self.assertIn("actor, concrete artifact, validation, separate policy owner, and action/failure", RUBRICS)

    def test_korean_prose_rules_preserve_explicit_agency(self) -> None:
        self.assertIn("Verifier가", PROSE)
        self.assertIn("RP/KMS가", PROSE)
        self.assertIn("local term onboarding", SKILL)


if __name__ == "__main__":
    unittest.main()
