#!/usr/bin/env python3
"""Fail-closed validation for the full-Point prose-preserving paired deck."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
FINAL = ROOT / "final"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slide_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("ppt/presentation.xml").decode("utf-8")
    return xml.count("<p:sldId ")


def main() -> int:
    failures: list[str] = []
    point_md = INPUT / "point.md"
    point_yaml = INPUT / "point.yaml"
    point_hash_file = INPUT / "point.sha256"
    point_gate = read_json(INPUT / "point-gate.json")
    expected_hash = point_hash_file.read_text(encoding="utf-8").split()[0]
    actual_hash = sha256(point_md)
    point = yaml.safe_load(point_yaml.read_text(encoding="utf-8"))
    provenance = read_json(FINAL / "build-provenance.json")
    coverage = read_json(FINAL / "structural-coverage-map.json")
    prose = read_json(FINAL / "prose-trace.json")
    crosswalk = read_json(FINAL / "summary-structural-crosswalk.json")

    if actual_hash != expected_hash:
        failures.append("point.md hash does not match point.sha256")
    if point_gate.get("passed") is not True or point_gate.get("artifact_sha256") != expected_hash:
        failures.append("Point gate is missing, failed, or bound to a different Point")
    for artifact in (provenance, coverage, prose, crosswalk):
        if artifact.get("canonical_point_sha256", artifact.get("point_sha256")) != expected_hash:
            failures.append("derived artifact does not use canonical Point hash")
    if provenance.get("projection_used") is not False:
        failures.append("prose-v2 build must not use a selective projection as its source")

    summary = ROOT / provenance["summary"]
    structural = ROOT / provenance["structural"]
    for deck, expected in ((summary, 2), (structural, 15)):
        if not deck.exists():
            failures.append(f"missing deck: {deck.relative_to(ROOT)}")
        elif slide_count(deck) != expected:
            failures.append(f"unexpected slide count: {deck.relative_to(ROOT)}")

    source_map = point["source_map"]
    claim_ids = set(source_map)
    model = point["model"]
    node_ids = {entry["id"] for entry in model["nodes"]}
    edge_ids = {entry["id"] for entry in model["edges"]}
    boundary_ids = {entry["id"] for entry in model["boundaries"]}
    context_ids = {entry["id"] for entry in model["context_dependencies"]}
    proof_ids = {f"P-{index:03d}" for index, _ in enumerate(point["proves"], 1)}
    nonproof_ids = {f"NP-{index:03d}" for index, _ in enumerate(point["does_not_prove"], 1)}
    developer_ids = {f"D-{index:03d}" for index, _ in enumerate(point["implications"]["developer"], 1)}
    executive_ids = {f"XEC-{index:03d}" for index, _ in enumerate(point["implications"]["technical_executive"], 1)}
    caveat_ids = {f"CV-{index:03d}" for index, _ in enumerate(point["caveats"] + point["exclusions"], 1)}
    source_ids = {source for refs in source_map.values() for source in refs}
    required_ids = claim_ids | node_ids | edge_ids | boundary_ids | context_ids | proof_ids | nonproof_ids | developer_ids | executive_ids | caveat_ids | source_ids
    rows = coverage.get("coverage", [])
    covered_ids = {row.get("id") for row in rows}
    missing = sorted(required_ids - covered_ids)
    duplicate_ids = [row.get("id") for row in rows if sum(other.get("id") == row.get("id") for other in rows) > 1]
    if missing:
        failures.append(f"unmapped canonical Point IDs: {', '.join(missing)}")
    if duplicate_ids:
        failures.append("coverage IDs must be unique")
    if any(not row.get("slides") or not row.get("object_ids") for row in rows):
        failures.append("coverage row is missing slide or logical object location")

    prose_rows = prose.get("rows", [])
    prose_claims = {row.get("point_id") for row in prose_rows}
    if prose.get("projection_complete") is not True:
        failures.append("prose trace does not declare canonical Point completeness")
    if not claim_ids.issubset(prose_claims):
        failures.append(f"claims without reader-visible prose: {', '.join(sorted(claim_ids - prose_claims))}")
    required_tokens = ("Verifier", "RP/KMS", "secret", "NO KEY")
    prose_text = "\n".join(str(row.get("sentence", "")) for row in prose_rows)
    if any(token not in prose_text for token in required_tokens):
        failures.append("prose trace lacks the required security-role/action vocabulary")

    must_see = set(crosswalk.get("summary_must_see_ids", []))
    required_must_see = {"C-001", "C-002", "C-004", "C-006", "C-007", "E-013", "E-015", "E-018", "B-006"}
    if must_see != required_must_see:
        failures.append("summary must-see IDs do not match full Point core mechanism")
    if len(crosswalk.get("semantic_invariants", [])) < 6:
        failures.append("crosswalk lacks full-Point semantic invariants")

    report = {
        "schema_version": "to-deck.prose-v2-gate.v1",
        "passed": not failures,
        "failures": failures,
        "canonical_point_sha256": expected_hash,
        "summary_slide_count": slide_count(summary) if summary.exists() else None,
        "structural_slide_count": slide_count(structural) if structural.exists() else None,
        "coverage_rows": len(rows),
        "canonical_required_ids": len(required_ids),
        "prose_claim_rows": len(prose_rows),
    }
    (FINAL / "paired-deck-gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
