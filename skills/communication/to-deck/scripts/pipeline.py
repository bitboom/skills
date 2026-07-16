#!/usr/bin/env python3
"""Deterministic run, slide-gate, freeze, and packaging utilities for To Deck."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

import yaml


SCORE_MAP = {
    "selection": {"visual_baseline_coverage": 10, "candidate_comparison_quality": 5},
    "semantic": {
        "point_coverage": 15,
        "causal_structure_visibility": 15,
        "diagram_accuracy": 10,
    },
    "reader": {"novice_comprehension": 15},
    "executive": {"executive_takeaway": 10},
    "writer": {"headline_clarity": 10},
    "visual": {"hierarchy": 5, "render_qa": 5},
}

RENDER_HARD_CHECKS = {
    "semantic_drift",
    "overflow",
    "unintended_overlap",
    "clipping",
    "broken_or_unreadable_text",
    "diagram_direction_errors",
    "missing_material_sources",
    "title_wrap",
    "body_below_16pt",
    "midlevel_below_24pt",
    "slide_title_below_35pt",
    "unsupported_glyphs",
    "critical_contrast_failure",
    "font_substitution",
    "color_only_encoding",
    "missing_alt_text",
    "invalid_reading_order",
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


def read_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected YAML object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_point_package(markdown: Path, model: Path, hash_file: Path, gate_file: Path) -> list[str]:
    failures: list[str] = []
    expected: dict[str, str] = {}
    try:
        for line in hash_file.read_text(encoding="utf-8").splitlines():
            digest, name = line.split(maxsplit=1)
            expected[name.strip()] = digest
    except (OSError, ValueError) as exc:
        raise SystemExit(f"invalid Point hash file {hash_file}: {exc}") from exc
    if expected.get("point.md") != sha256(markdown):
        failures.append("Point markdown hash does not match point.sha256")
    if expected.get("point.yaml") != sha256(model):
        failures.append("Point model hash does not match point.sha256")
    gate = read_json(gate_file)
    if gate.get("passed") is not True:
        failures.append("upstream Point gate did not pass")
    if gate.get("artifact_sha256") != sha256(markdown):
        failures.append("upstream Point gate is stale for markdown")
    if gate.get("model_sha256") != sha256(model):
        failures.append("upstream Point gate is stale for model")
    return failures


def pptx_slide_count(path: Path) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            return sum(
                1 for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide[0-9]+\.xml", name)
            )
    except (OSError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"invalid PPTX {path}: {exc}") from exc


def read_inspect(path: Path) -> list[dict]:
    records: list[dict] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {number} is not an object")
                records.append(value)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid deck inspection {path}: {exc}") from exc
    return records


def validate_render_manifest(path: Path, expected_slides: int) -> list[str]:
    failures: list[str] = []
    manifest = read_json(path)
    for name in ("renderer", "renderer_version", "command", "generated_at"):
        if not isinstance(manifest.get(name), str) or not manifest[name].strip():
            failures.append(f"render manifest {name} is missing")
    if manifest.get("slide_count") != expected_slides:
        failures.append("render manifest declared slide count does not match PPTX")
    slides = manifest.get("slides")
    if not isinstance(slides, list) or len(slides) != expected_slides:
        return ["render manifest slide count does not match PPTX"]
    for index, item in enumerate(slides, 1):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            failures.append(f"render manifest slide {index} is invalid")
            continue
        if not isinstance(item.get("width"), int) or not isinstance(item.get("height"), int):
            failures.append(f"render manifest slide {index} dimensions are missing")
        image = Path(item["path"])
        if not image.is_absolute():
            image = path.parent / image
        if not image.is_file():
            failures.append(f"rendered slide {index} is missing")
        elif item.get("sha256") != sha256(image):
            failures.append(f"rendered slide {index} hash is stale")
    return failures


def require_list(value: dict, name: str) -> list:
    result = value.get(name)
    if not isinstance(result, list):
        raise SystemExit(f"{name} must be an array")
    return result


def validate_scores(review: dict, weights: dict[str, int], label: str) -> tuple[float, list[str]]:
    scores = review.get("scores")
    if not isinstance(scores, dict):
        raise SystemExit(f"{label}.scores must be an object")
    weighted = 0.0
    failures: list[str] = []
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
    point_hash = Path(args.point_hash).resolve()
    point_gate = Path(args.point_gate).resolve()
    for source in (point_md, point_yaml, point_hash, point_gate):
        if not source.is_file():
            raise SystemExit(f"Point input does not exist: {source}")
    failures = verify_point_package(point_md, point_yaml, point_hash, point_gate)
    if failures:
        raise SystemExit("invalid Point package: " + "; ".join(failures))
    for directory in (root / "input", root / "slides", root / "final"):
        directory.mkdir(parents=True, exist_ok=True)
    out_md = root / "input" / "point.md"
    out_yaml = root / "input" / "point.yaml"
    shutil.copyfile(point_md, out_md)
    shutil.copyfile(point_yaml, out_yaml)
    shutil.copyfile(point_hash, root / "input" / "point.sha256")
    shutil.copyfile(point_gate, root / "input" / "point-gate.json")
    (root / "00-deck-brief.yaml").write_text(
        "run_id: \naudience: []\nslide_count: \nformat: pptx\nvenue: \nlanguage: \n"
        "reading_mode: standalone\nminimum_font_pt: 16\ntemplate: \naccessibility: \n"
        "prior_deck: \nuser_rejected_dimensions: []\nreview_mode: independent\n",
        encoding="utf-8",
    )
    print(root)
    return 0


def command_slide_gate(args: argparse.Namespace) -> int:
    paths = {name: Path(getattr(args, name.replace("-", "_"))).resolve() for name in (
        "point", "point-model", "point-hash-file", "point-gate", "deck",
        "render-manifest", "deck-inspect", "visual-query", "visual-baseline",
        "brief", "constraints", "candidate-a", "candidate-b", "visual-model",
    )}
    hashes = {name.replace("-", "_") + "_sha256": sha256(path) for name, path in paths.items()}
    reviews = {name: read_json(Path(getattr(args, name))) for name in (
        "selection", "semantic", "reader", "executive", "writer", "visual",
    )}
    failures: list[str] = []
    failures.extend(verify_point_package(
        paths["point"], paths["point-model"], paths["point-hash-file"], paths["point-gate"]
    ))
    point_model = read_yaml(paths["point-model"])
    model = point_model.get("model")
    if not isinstance(model, dict):
        raise SystemExit("Point model.model must be an object")
    point_nodes = model.get("nodes")
    point_edges = model.get("edges")
    point_boundaries = model.get("boundaries")
    for name, value in (("nodes", point_nodes), ("edges", point_edges), ("boundaries", point_boundaries)):
        if not isinstance(value, list):
            raise SystemExit(f"Point model {name} must be an array")
    point_structural = len(point_nodes) >= 3 or len(point_edges) >= 2
    brief = read_yaml(paths["brief"])

    slide_count = pptx_slide_count(paths["deck"])
    if slide_count < 1:
        failures.append("PPTX contains no slides")
    failures.extend(validate_render_manifest(paths["render-manifest"], slide_count))
    requested_slide_count = brief.get("slide_count")
    if not isinstance(requested_slide_count, int) or requested_slide_count < 1:
        raise SystemExit("brief slide_count must be a positive integer")
    if slide_count != requested_slide_count:
        failures.append("PPTX slide count does not match brief")
    inspect_records = read_inspect(paths["deck-inspect"])
    inspect_slides = {record.get("slide") for record in inspect_records if record.get("kind") == "slide"}
    if len(inspect_slides) != slide_count:
        failures.append("deck inspection slide count does not match PPTX")
    inspect_by_id = {record.get("id"): record for record in inspect_records if isinstance(record.get("id"), str)}

    visual_baseline = read_json(paths["visual-baseline"])
    must_see = visual_baseline.get("must_see")
    if not isinstance(must_see, list) or not must_see:
        raise SystemExit("visual baseline must_see must be a non-empty array")
    must_ids = {
        item.get("id") for item in must_see
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if len(must_ids) != len(must_see):
        failures.append("visual baseline must-see IDs are missing or duplicated")
    required_sets: dict[str, set[str]] = {}
    for name in (
        "semantic_required_ids", "gist_required_ids", "reconstruction_required_ids",
        "executive_required_ids", "headline_required_ids",
    ):
        values = visual_baseline.get(name)
        if not isinstance(values, list) or not values:
            raise SystemExit(f"visual baseline {name} must be a non-empty array")
        required_sets[name] = {value for value in values if isinstance(value, str)}
        if len(required_sets[name]) != len(values) or not required_sets[name].issubset(must_ids):
            failures.append(f"visual baseline {name} contains invalid IDs")

    visual_model = read_json(paths["visual-model"])
    objects = visual_model.get("objects")
    if not isinstance(objects, list) or not objects:
        raise SystemExit("visual model objects must be a non-empty array")
    mapped_baseline: set[str] = set()
    semantic_records: list[dict] = []
    semantic_kinds = {"node", "connector", "boundary"}
    kind_counts = {kind: 0 for kind in semantic_kinds}
    for item in objects:
        if not isinstance(item, dict):
            raise SystemExit("visual model object must be an object")
        baseline_ids = item.get("baseline_ids", [])
        artifact_ids = item.get("artifact_object_ids", [])
        if not isinstance(baseline_ids, list) or not isinstance(artifact_ids, list):
            raise SystemExit("visual model mappings must be arrays")
        mapped_baseline.update(value for value in baseline_ids if isinstance(value, str))
        kind = item.get("kind")
        if kind in semantic_kinds:
            kind_counts[kind] += 1
            if not artifact_ids:
                failures.append(f"semantic visual object {item.get('id')} has no artifact object")
            for artifact_id in artifact_ids:
                record = inspect_by_id.get(artifact_id)
                if record is None:
                    failures.append(f"visual object {artifact_id} is absent from deck inspection")
                elif record.get("kind") == "textbox" and kind in {"connector", "boundary"}:
                    failures.append(f"{kind} {artifact_id} cannot be a textbox")
                elif isinstance(record.get("bbox"), list) and len(record["bbox"]) == 4:
                    semantic_records.append(record)
    missing_must = must_ids - mapped_baseline
    if missing_must:
        failures.append("visual model misses baseline IDs: " + ", ".join(sorted(missing_must)))
    if point_structural and kind_counts["connector"] < 2:
        failures.append("structural Point requires at least two real connector objects")
    if point_boundaries and kind_counts["boundary"] < 1:
        failures.append("Point trust boundaries require at least one visible boundary object")

    measured_share = 0.0
    if semantic_records:
        left = min(record["bbox"][0] for record in semantic_records)
        top = min(record["bbox"][1] for record in semantic_records)
        right = max(record["bbox"][0] + record["bbox"][2] for record in semantic_records)
        bottom = max(record["bbox"][1] + record["bbox"][3] for record in semantic_records)
        measured_share = ((right - left) * (bottom - top)) / (1280 * 560)
    if point_structural and measured_share < 0.55:
        failures.append("measured semantic visual share is below 0.55 of the core region")

    selection = reviews["selection"]
    if selection.get("point_sha256") != hashes["point_sha256"]:
        failures.append("selection is stale for Point")
    for name in ("visual_query", "visual_baseline", "brief", "constraints", "candidate_a", "candidate_b", "visual_model"):
        if selection.get(f"{name}_sha256") != hashes[f"{name}_sha256"]:
            failures.append(f"selection {name}_sha256 is stale")
    if require_list(selection, "critical_issues"):
        failures.append("selection has critical issues")
    selection_hard = selection.get("hard_checks")
    if not isinstance(selection_hard, dict):
        raise SystemExit("selection.hard_checks must be an object")
    for name in (
        "candidate_a_blind", "candidate_b_blind", "candidate_visual_grammars_distinct",
        "prior_deck_hidden", "selection_reasoned", "dominant_diagram_selected",
        "project_lens_secondary", "no_new_claims",
    ):
        if selection_hard.get(name) is not True:
            failures.append(f"selection hard check {name} must be true")
    if selection.get("selected_candidate") not in {"A", "B", "synthesis"}:
        failures.append("selected_candidate must be A, B, or synthesis")
    must_total = len(must_ids)
    must_mapped = selection.get("must_see_mapped")
    if selection.get("must_see_total") != must_total or must_mapped != must_total:
        failures.append("visual-baseline must-see coverage is incomplete")
    if len(require_list(selection, "coverage_rows")) < (must_total if isinstance(must_total, int) else 1):
        failures.append("selection coverage rows are incomplete")
    if not require_list(selection, "candidate_a_strengths"):
        failures.append("candidate A has no recorded strength")
    if not require_list(selection, "candidate_b_strengths"):
        failures.append("candidate B has no recorded strength")

    for label in ("semantic", "reader", "executive", "writer", "visual"):
        review = reviews[label]
        for hash_name in (
            "point_sha256", "point_model_sha256", "brief_sha256", "deck_sha256",
            "render_manifest_sha256", "deck_inspect_sha256", "visual_model_sha256",
        ):
            if review.get(hash_name) != hashes[hash_name]:
                failures.append(f"{label} review is stale for {hash_name.removesuffix('_sha256')}")
        if require_list(review, "critical_issues"):
            failures.append(f"{label} review has critical issues")
        for name in ("reviewer_id", "reviewer_model", "author_id", "author_model", "review_prompt_sha256"):
            value = review.get(name)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{label} {name} is missing")
        prompt_hash = review.get("review_prompt_sha256")
        if isinstance(prompt_hash, str) and not re.fullmatch(r"[0-9a-f]{64}", prompt_hash):
            failures.append(f"{label} review_prompt_sha256 is invalid")
        if review.get("reviewer_id") == review.get("author_id"):
            failures.append(f"{label} reviewer must differ from author")
    rounds = {reviews[label].get("round") for label in reviews}
    if len(rounds) != 1 or None in rounds:
        failures.append("reviews do not share one valid round")

    semantic = reviews["semantic"]
    elements = semantic.get("structural_elements")
    relationships = semantic.get("relationships")
    if not isinstance(elements, int) or not isinstance(relationships, int):
        raise SystemExit("semantic structural_elements and relationships must be integers")
    required = point_structural
    if semantic.get("structural_elements") != len(point_nodes):
        failures.append("semantic structural_elements does not match Point")
    if semantic.get("relationships") != len(point_edges):
        failures.append("semantic relationships does not match Point")
    if semantic.get("diagram_required") is not required:
        failures.append("diagram_required does not match Point structure")
    if required:
        if semantic.get("dominant_visual_present") is not True:
            failures.append("required meaning-bearing diagram is not dominant")
        share = semantic.get("semantic_visual_share")
        if not isinstance(share, (int, float)) or isinstance(share, bool):
            failures.append("semantic visual share must be numeric")
        elif abs(share - measured_share) > 0.05:
            failures.append("semantic visual share does not match measured geometry")
    for kind in ("nodes", "edges", "boundaries"):
        checked = semantic.get(f"{kind}_checked")
        total = semantic.get(f"{kind}_total")
        expected = kind_counts[{"nodes": "node", "edges": "connector", "boundaries": "boundary"}[kind]]
        if not isinstance(checked, int) or not isinstance(total, int) or checked != total or total != expected:
            failures.append(f"semantic {kind} coverage is incomplete")
    if semantic.get("diagram_direction_errors") != 0:
        failures.append("diagram direction errors must be zero")
    for name in ("visual_grammar_matches_job", "trust_roles_not_collapsed", "project_assessment_secondary"):
        if semantic.get(name) is not True:
            failures.append(f"semantic hard check {name} must be true")
    verified_semantic = set(require_list(semantic, "verified_semantic_ids"))
    if not required_sets["semantic_required_ids"].issubset(verified_semantic):
        failures.append("semantic review misses baseline semantic IDs")

    reader = reviews["reader"]
    if reader.get("reviewer_id") == reviews["executive"].get("reviewer_id"):
        failures.append("reader and executive must be independent reviewers")
    for label in ("reader", "executive"):
        review = reviews[label]
        if review.get("allowed_inputs") != ["rendered_slides"]:
            failures.append(f"{label} received non-render inputs")
        for name in ("point_context_seen", "storyboard_context_seen", "prior_scores_seen"):
            if review.get(name) is not False:
                failures.append(f"{label} isolation check {name} must be false")
    gist_seconds = reader.get("gist_exposure_seconds")
    reconstruction_seconds = reader.get("reconstruction_exposure_seconds")
    if not isinstance(gist_seconds, (int, float)) or isinstance(gist_seconds, bool) or not 5 <= gist_seconds <= 10:
        failures.append("reader gist exposure must be between 5 and 10 seconds")
    if not isinstance(reconstruction_seconds, (int, float)) or isinstance(reconstruction_seconds, bool) or not 20 <= reconstruction_seconds <= 30:
        failures.append("reader reconstruction exposure must be between 20 and 30 seconds")
    for name in ("raw_gist_answers", "raw_reconstruction_answers"):
        answers = reader.get(name)
        if not isinstance(answers, dict) or not answers or any(not str(value).strip() for value in answers.values()):
            failures.append(f"reader {name} are missing")
    if not required_sets["gist_required_ids"].issubset(set(require_list(reader, "gist_recovered_ids"))):
        failures.append("reader misses baseline gist IDs")
    if not required_sets["reconstruction_required_ids"].issubset(set(require_list(reader, "reconstruction_recovered_ids"))):
        failures.append("reader misses baseline reconstruction IDs")
    if reader.get("teach_back_match") is not True:
        failures.append("reader teach-back does not match")
    if require_list(reader, "critical_questions"):
        failures.append("reader has unanswered critical questions")

    executive = reviews["executive"]
    executive_answers = executive.get("raw_answers")
    if not isinstance(executive_answers, dict) or not executive_answers or any(not str(value).strip() for value in executive_answers.values()):
        failures.append("executive raw answers are missing")
    if not required_sets["executive_required_ids"].issubset(set(require_list(executive, "executive_recovered_ids"))):
        failures.append("executive misses baseline executive IDs")
    if require_list(executive, "critical_questions"):
        failures.append("executive has unanswered critical questions")

    writer = reviews["writer"]
    for name in (
        "headline_domain_first", "headline_is_assertion", "meta_evaluation_language_absent",
        "labels_plain_language", "compression_preserves_model",
    ):
        if writer.get(name) is not True:
            failures.append(f"writer hard check {name} must be true")
    if not required_sets["headline_required_ids"].issubset(set(require_list(writer, "headline_recovered_ids"))):
        failures.append("headline misses baseline headline IDs")
    if writer.get("unexplained_critical_terms") != 0:
        failures.append("unexplained critical terms must be zero")

    visual = reviews["visual"]
    for name in ("full_size_render_inspected", "thumbnail_render_inspected", "structural_test_passed", "slide_count_match"):
        if visual.get(name) is not True:
            failures.append(f"visual hard check {name} must be true")
    support_blocks = visual.get("non_diagram_support_blocks")
    if not isinstance(support_blocks, int) or support_blocks > 3:
        failures.append("non-diagram support blocks must be an integer no greater than 3")
    telemetry = visual.get("density_telemetry")
    if not isinstance(telemetry, dict):
        failures.append("visual density telemetry is missing")
    else:
        for name in (
            "visible_word_count", "perceptual_group_count", "min_font_pt",
            "direct_label_rate", "edge_crossings", "whitespace_ratio",
        ):
            if not isinstance(telemetry.get(name), (int, float)) or isinstance(telemetry.get(name), bool):
                failures.append(f"visual density telemetry {name} is missing")
    hard = visual.get("hard_checks")
    if not isinstance(hard, dict):
        raise SystemExit("visual.hard_checks must be an object")
    missing = RENDER_HARD_CHECKS - set(hard)
    if missing:
        failures.append("missing render hard checks: " + ", ".join(sorted(missing)))
    for name in sorted(RENDER_HARD_CHECKS & set(hard)):
        if hard[name] != 0:
            failures.append(f"{name} must be zero")

    prior_deck = brief.get("prior_deck")
    rejected_dimensions = brief.get("user_rejected_dimensions")
    regression_required = bool(prior_deck) or bool(rejected_dimensions)
    if regression_required and not args.regression:
        failures.append("brief requires a regression review")
    if args.regression:
        regression = read_json(Path(args.regression))
        for hash_name in (
            "point_sha256", "point_model_sha256", "brief_sha256", "deck_sha256",
            "render_manifest_sha256", "deck_inspect_sha256", "visual_model_sha256",
        ):
            if regression.get(hash_name) != hashes[hash_name]:
                failures.append(f"regression review is stale for {hash_name.removesuffix('_sha256')}")
        if regression.get("blind_review_completed_before_comparison") is not True:
            failures.append("regression comparison occurred before blind review")
        if regression.get("balanced_order_comparison") is not True or regression.get("order_results_agree") is not True:
            failures.append("regression comparison did not control order bias")
        rejected = set(require_list(regression, "user_rejected_dimensions"))
        improved = set(require_list(regression, "improvements"))
        if not rejected or not rejected.issubset(improved):
            failures.append("not every user-rejected dimension improved")
        if require_list(regression, "regressions"):
            failures.append("regression comparison found regressions")
        no_regression = regression.get("no_regression")
        if not isinstance(no_regression, dict):
            raise SystemExit("regression.no_regression must be an object")
        for name in ("accuracy", "readability", "scanability"):
            if no_regression.get(name) is not True:
                failures.append(f"baseline regression in {name}")

    total = 0.0
    for label, weights in SCORE_MAP.items():
        value, score_failures = validate_scores(reviews[label], weights, label)
        total += value
        failures.extend(score_failures)
    total = round(total, 2)
    if total < 90:
        failures.append("slide score below 90")

    result = {
        "gate": "slide",
        "round": reviews["semantic"].get("round"),
        "passed": not failures,
        "slide_score": total,
        **{name: hashes[name] for name in (
            "point_sha256", "point_model_sha256", "brief_sha256", "deck_sha256",
            "render_manifest_sha256", "deck_inspect_sha256", "visual_model_sha256",
        )},
        "measured_semantic_visual_share": round(measured_share, 4),
        "failures": failures,
    }
    write_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 2


def command_freeze(args: argparse.Namespace) -> int:
    deck = Path(args.deck).resolve()
    gate = read_json(Path(args.gate))
    if gate.get("passed") is not True:
        raise SystemExit("cannot freeze a deck without a passing gate")
    if gate.get("deck_sha256") != sha256(deck):
        raise SystemExit("passing gate is stale for deck")
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    final_deck = output / "final-deck.pptx"
    shutil.copyfile(deck, final_deck)
    (output / "final-deck.sha256").write_text(
        f"{sha256(final_deck)}  final-deck.pptx\n", encoding="utf-8"
    )
    print(output)
    return 0


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
    init.add_argument("--point-hash", required=True)
    init.add_argument("--point-gate", required=True)
    init.set_defaults(func=command_init)

    gate = commands.add_parser("slide-gate")
    for name in (
        "point", "point-model", "point-hash-file", "point-gate", "deck",
        "render-manifest", "deck-inspect", "visual-query", "visual-baseline",
        "brief", "constraints", "candidate-a", "candidate-b", "visual-model", "selection", "semantic",
        "reader", "executive", "writer", "visual", "output",
    ):
        gate.add_argument(f"--{name}", required=True)
    gate.add_argument("--regression")
    gate.set_defaults(func=command_slide_gate)

    freeze = commands.add_parser("freeze")
    freeze.add_argument("--deck", required=True)
    freeze.add_argument("--gate", required=True)
    freeze.add_argument("--output-dir", required=True)
    freeze.set_defaults(func=command_freeze)

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
