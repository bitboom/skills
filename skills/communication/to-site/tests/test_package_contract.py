import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PackageContractTest(unittest.TestCase):
    def test_skill_declares_required_delivery_and_gates(self):
        contract = (ROOT / "references" / "run-contract.md").read_text()
        for required in (
            "dist/",
            "semantic-map.json",
            "desktop.png",
            "mobile.png",
            "data-claim-id",
            "data-source-id",
        ):
            self.assertIn(required, contract)


if __name__ == "__main__":
    unittest.main()
