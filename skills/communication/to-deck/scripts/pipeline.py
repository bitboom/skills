#!/usr/bin/env python3
"""Deterministic run, slide-gate, and packaging utilities for To Deck."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile


SCORE_MAP = {
    "diagram": {
        "point_coverage": 20,
        "structural_visibility": 20,
        "diagram_accuracy": 15,
    },
    "executive": {"first_glance_takeaway": 15},
    "reader": {"reader_comprehension": 10},
    "visual": {"hierarchy": 10, "traceability_qa": 10},
}

VISUAL_HARD_CHECKS = {
    "semantic_drift",
    "overflow",
    "unintended_overlap",
    "clipping",
    "broken_or_unreadable_text",
    "diagram_direction_errors",
    "missing_material_sources",
}


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_list(review: dict, name: str) -> list:
    value = review.get(name)
    if not isinstance(value, list):
        raise SystemExit(f"{name} must be an array")
    return value


def validate_scores(review: dict, weights: dict[str, int], label: str) -> tuple[float, list[str]]:
    scores = review.get("scores")
    if not isinstance(scores, dict):
        raise SystemExit(f"{label}.scores must be an object")
    weighted = 0.0
    failures = []
    for name, weight in weights.items():
        score = scores.get(name)
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 1 <= score <= 5:
            raise SystemExit(f"{label} score {name} must be a number from 1 to 5")
        weighted += score / 5.0 * weight
        if score < 4:
            failures.append(f"{label}.{name} below 4/5")
    return weighted, failures


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"run directory is not empty: {root}")
    point_md = Path(args.point_md).resolve()
    point_yaml = Path(args.point_yaml).resolve()
    for source in (point_md, point_yaml):
        if not source.is_file():
            raise SystemExit(f"Point input does not exist: {source}")
    for directory in (root / "input", root / "slides", root / "final"):
        directory.mkdir(parents=True, exist_ok=True)
    out_md = root / "input" / "point.md"
    out_yaml = root / "input" / "point.yaml"
    shutil.copyfile(point_md, out_md)
    shutil.copyfile(point_yaml, out_yaml)
    (root / "input" / "point.sha256").write_text(
        f"{sha256(out_md)}  point.md\n{sha256(out_yaml)}  point.yaml\n", encoding="utf-8"
    )
    (root / "00-deck-brief.yaml").write_text(
        "run_id: \naudience: []\nslide_count: \nformat: pptx\nvenue: \nlanguage: \n"
        "visual_constraints: \nbaseline_deck: \nreview_mode: independent\n",
        encoding="utf-8",
    )
    print(root)
    return 0


def command_slide_gate(args: argparse.Namespace) -> int:
    point_hash = sha256(Path(args.point).resolve())
    reviews = {
        "diagram": read_json(Path(args.diagram)),
        "reader": read_json(Path(args.reader)),
        "executive": read_json(Path(args.executive)),
        "visual": read_json(Path(args.visual)),
    }
    failures: list[str] = []
    for label, review in reviews.items():
        if review.get("point_sha256") != point_hash:
            failures.append(f"{label} review is stale for Point")
        if require_list(review, "critical_issues"):
            failures.append(f"{label} review has critical issues")

    diagram = reviews["diagram"]
    elements = diagram.get("structural_elements")
    relationships = diagram.get("relationships")
    if not isinstance(elements, int) or not isinstance(relationships, int):
        raise SystemExit("diagram structural_elements and relationships must be integers")
    required = elements >= 3 or relationships >= 2
    if diagram.get("diagram_required") is not required:
        failures.append("diagram_required does not match Point structure")
    if required:
        if diagram.get("dominant_visual_present") is not True:
            failures.append("required meaning-bearing diagram is not dominant")
        share = diagram.get("semantic_visual_share")
        if not isinstance(share, (int, float)) or isinstance(share, bool) or share < 0.5:
            failures.append("semantic visual share must be at least 0.5")
    for kind in ("nodes", "edges", "boundaries"):
        checked = diagram.get(f"{kind}_checked")
        total = diagram.get(f"{kind}_total")
        if not isinstance(checked, int) or not isinstance(total, int) or checked != total:
            failures.append(f"diagram {kind} coverage is incomplete")
    if diagram.get("diagram_direction_errors") != 0:
        failures.append("diagram direction errors must be zero")

    reader = reviews["reader"]
    for name in (
        "teach_back_match",
        "headline_paraphrase_match",
        "identified_input",
        "identified_decision_maker",
        "identified_action",
        "identified_outcome",
    ):
        if reader.get(name) is not True:
            failures.append(f"reader hard check {name} must be true")
    if require_list(reader, "critical_questions"):
        failures.append("reader has unanswered critical questions")

    executive = reviews["executive"]
    for name in ("so_what_clear", "decision_clear", "risk_or_constraint_clear", "next_action_clear"):
        if executive.get(name) is not True:
            failures.append(f"executive hard check {name} must be true")
    if require_list(executive, "critical_questions"):
        failures.append("executive has unanswered critical questions")

    visual = reviews["visual"]
    hard = visual.get("hard_checks")
    if not isinstance(hard, dict):
        raise SystemExit("visual.hard_checks must be an object")
    missing = VISUAL_HARD_CHECKS - set(hard)
    if missing:
        failures.append("missing visual hard checks: " + ", ".join(sorted(missing)))
    for name in sorted(VISUAL_HARD_CHECKS & set(hard)):
        if hard[name] != 0:
            failures.append(f"{name} must be zero")

    total = 0.0
    for label, weights in SCORE_MAP.items():
        value, score_failures = validate_scores(reviews[label], weights, label)
        total += value
        failures.extend(score_failures)
    total = round(total, 2)
    if total < 90:
        failures.append("slide score below 90")

    if args.baseline:
        baseline = read_json(Path(args.baseline))
        if baseline.get("point_sha256") != point_hash:
            failures.append("baseline review is stale for Point")
        if require_list(baseline, "critical_issues"):
            failures.append("baseline review has critical issues")
        if require_list(baseline, "regressions"):
            failures.append("baseline comparison found regressions")
        no_regression = baseline.get("no_regression")
        if not isinstance(no_regression, dict):
            raise SystemExit("baseline.no_regression must be an object")
        for name in ("mental_model_reconstruction", "scanability", "information_coverage"):
            if no_regression.get(name) is not True:
                failures.append(f"baseline regression in {name}")

    result = {
        "gate": "slide",
        "round": reviews["diagram"].get("round"),
        "passed": not failures,
        "slide_score": total,
        "point_sha256": point_hash,
        "failures": failures,
    }
    write_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 2


def command_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    entries = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path in {output, root / "review-trail.zip"}:
            continue
        entries.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    write_json(output, {"files": entries})
    print(len(entries))
    return 0


def command_package(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if path != output:
                archive.write(path, path.relative_to(root).as_posix())
    print(output)
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("--root", required=True)
    init.add_argument("--point-md", required=True)
    init.add_argument("--point-yaml", required=True)
    init.set_defaults(func=command_init)

    gate = commands.add_parser("slide-gate")
    for name in ("point", "diagram", "reader", "executive", "visual", "output"):
        gate.add_argument(f"--{name}", required=True)
    gate.add_argument("--baseline")
    gate.set_defaults(func=command_slide_gate)

    manifest = commands.add_parser("manifest")
    manifest.add_argument("--root", required=True)
    manifest.add_argument("--output", required=True)
    manifest.set_defaults(func=command_manifest)

    package = commands.add_parser("package")
    package.add_argument("--root", required=True)
    package.add_argument("--output", required=True)
    package.set_defaults(func=command_package)
    return value


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
