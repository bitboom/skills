#!/usr/bin/env python3
"""Fail-closed validation for the Intel RATS paired To Deck fixture."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input/to-site.input.json"
COVERAGE = ROOT / "final/structural-coverage-map.json"
CROSSWALK = ROOT / "final/summary-structural-crosswalk.json"
PROVENANCE = ROOT / "final/build-provenance.json"
REPORT = ROOT / "final/paired-deck-gate.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def slide_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("ppt/presentation.xml").decode("utf-8")
    return xml.count("<p:sldId ")


def main() -> int:
    failures: list[str] = []
    point = read_json(INPUT)
    coverage = read_json(COVERAGE)
    crosswalk = read_json(CROSSWALK)
    provenance = read_json(PROVENANCE)

    if coverage.get("point_sha256") != point["source_manifest"]["point_sha256"]:
        failures.append("coverage map does not use frozen point hash")
    if crosswalk.get("point_sha256") != point["source_manifest"]["point_sha256"]:
        failures.append("crosswalk does not use frozen point hash")
    if provenance.get("point_sha256") != point["source_manifest"]["point_sha256"]:
        failures.append("build provenance does not use frozen point hash")

    summary = ROOT / provenance["summary"]
    structural = ROOT / provenance["structural"]
    for deck, expected in ((summary, 2), (structural, 11)):
        if not deck.exists():
            failures.append(f"missing deck: {deck.relative_to(ROOT)}")
        elif slide_count(deck) != expected:
            failures.append(f"unexpected slide count: {deck.relative_to(ROOT)}")

    rows = coverage.get("coverage", [])
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        failures.append("coverage IDs are not unique")
    if any(not row.get("slide") or not row.get("object_ids") for row in rows):
        failures.append("coverage row missing slide or editable logical object ID")

    expected_ids = {
        *(claim["id"] for claim in point["claims"]),
        *(node["id"] for node in point["models"]["nodes"]),
        *(edge["id"] for edge in point["models"]["edges"]),
        *(boundary["id"] for boundary in point["models"]["boundaries"]),
        *(f"NP-{index:03d}" for index, _ in enumerate(point["does_not_prove"], 1)),
        *(f"O-{index:03d}" for index in range(1, 7)),
        *(source["id"] for source in point["sources"]),
    }
    missing = sorted(expected_ids - set(ids))
    if missing:
        failures.append(f"unmapped structural IDs: {', '.join(missing)}")

    source_ids = {source["id"] for source in point["sources"]}
    covered_sources = {row["id"] for row in rows if row.get("kind") == "source"}
    if covered_sources != source_ids:
        failures.append("source ledger is incomplete")
    for claim in point["claims"]:
        for source_id in claim["source_refs"]:
            if source_id not in covered_sources:
                failures.append(f"claim {claim['id']} source {source_id} lacks a source ledger row")

    must_see = set(crosswalk.get("summary_must_see_ids", []))
    crosswalk_ids = [row.get("id") for row in crosswalk.get("crosswalk", [])]
    if set(crosswalk_ids) != must_see or len(crosswalk_ids) != len(set(crosswalk_ids)):
        failures.append("summary crosswalk must map every must-see ID exactly once")
    for row in crosswalk.get("crosswalk", []):
        if not row.get("summary", {}).get("object_id") or not row.get("structural", {}).get("object_id"):
            failures.append(f"crosswalk mapping lacks an object ID: {row.get('id')}")

    invariants = crosswalk.get("semantic_invariants", [])
    if len(invariants) < 5:
        failures.append("crosswalk lacks required semantic invariants")

    report = {
        "schema_version": "to-deck.paired-gate.v1",
        "passed": not failures,
        "failures": failures,
        "point_sha256": point["source_manifest"]["point_sha256"],
        "summary_slide_count": slide_count(summary) if summary.exists() else None,
        "structural_slide_count": slide_count(structural) if structural.exists() else None,
        "structural_coverage_rows": len(rows),
        "summary_must_see_ids": sorted(must_see),
        "semantic_invariant_count": len(invariants),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
