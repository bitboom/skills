#!/usr/bin/env python3
"""Deterministic run, slide-gate, freeze, and packaging utilities for To Deck."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
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

RENDER_MANIFEST_SCHEMA_VERSION = 2
RENDER_TOOLCHAIN_FIELDS = {"renderer", "renderer_version", "command", "environment"}
MAX_PACKAGE_MEMBERS = 1_000
MAX_PACKAGE_MEMBER_BYTES = 100 * 1024 * 1024
MAX_PACKAGE_TOTAL_BYTES = 500 * 1024 * 1024
MAX_PACKAGE_COMPRESSION_RATIO = 100
VISUAL_BUG_HUNT_CHECKS = {
    "overlap",
    "clipping",
    "label_clearance",
    "footer_collision",
    "contrast",
    "text_wrapping",
    "placeholder_content",
    "reading_order",
}
SECURITY_BOUNDARY_TRACE_ROLES = {
    "role": "role_object_ids",
    "artifact": "artifact_object_ids",
    "checker": "checker_object_ids",
    "decision": "decision_object_ids",
    "failure": "failure_object_ids",
}
TRACE_DIRECTIONS = {"left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top", "radial"}
CRITICAL_ARTIFACT_TRACE_ROLES = {
    "producer": "producer_object_ids",
    "checker": "checker_object_ids",
    "consumer": "consumer_object_ids",
    "connector": "connector_object_ids",
}

INDIVIDUAL_COMPONENT_WEIGHTS = {
    "semantic_coverage": 25,
    "structural_fidelity": 20,
    "causal_directional_boundary_expressiveness": 15,
    "novice_developer_comprehension": 10,
    "technical_executive_usefulness": 10,
    "density_legibility_fit": 10,
    "visual_hierarchy": 5,
    "editability_accessibility": 5,
}

ENSEMBLE_WEIGHTS = {
    "complete_must_see_coverage": 30,
    "causal_closure_structural_correctness": 20,
    "complementarity_incremental_value": 15,
    "low_redundancy": 10,
    "cognitive_load_readability": 10,
    "one_coherent_dominant_visual_argument": 10,
    "accessibility_editability": 5,
}

DEFAULT_DOMINANT_FAMILIES = {
    "causal-pipeline",
    "sequence-or-handshake-diagram",
    "system-architecture",
    "trust-boundary-and-data-flow-diagram",
    "decision-tree",
    "state-machine",
    "lifecycle-or-timeline",
    "layered-stack",
    "comparison-matrix",
    "knowledge-graph-or-topology",
    "evidence-and-verification-chain",
    "custom-domain-diagram",
}

DEFAULT_SUPPORTING_FAMILIES = {
    "definition",
    "key-characteristics",
    "actor-legend",
    "inputs-and-outputs",
    "proof-and-non-proof",
    "benefits",
    "limitations-and-risks",
    "decision-and-next-action",
    "use-cases",
    "source-project-lens",
    "bottom-takeaway",
}

NON_SEMANTIC_FAMILIES = {"page-number", "decorative-icon", "simple-background"}

VISUAL_JOB_TYPES = {
    "definition",
    "mechanism",
    "actor-relationship",
    "causal-path",
    "sequence",
    "trust-boundary",
    "artifact-movement",
    "decision-or-branching",
    "state-transition",
    "comparison",
    "proof",
    "non-proof",
    "limitation",
    "action",
    "project-lens",
}

STRUCTURAL_VISUAL_JOBS = {
    "mechanism",
    "actor-relationship",
    "causal-path",
    "sequence",
    "trust-boundary",
    "artifact-movement",
    "decision-or-branching",
    "state-transition",
}

REQUIRED_COMPONENT_HARD_FAILURES = {
    "semantic-distortion",
    "collapsed-distinct-roles-or-boundaries",
    "causal-or-message-direction-missing",
    "evidence-result-action-path-broken",
    "proof-non-proof-confused",
    "source-project-dominates-domain",
    "decorative-card-listing",
    "unreadable-at-required-size",
    "color-only-encoding",
    "new-material-claim",
}

REQUIRED_BASELINE_SETS = (
    "semantic_required_ids",
    "gist_required_ids",
    "reconstruction_required_ids",
    "executive_required_ids",
    "headline_required_ids",
)

COMPONENT_BUNDLE_PATHS = (
    "point",
    "point-model",
    "visual-baseline",
    "constraints",
    "component-rubric",
    "component-catalog",
    "visual-jobs-a",
    "visual-jobs-b",
    "component-score-a",
    "component-score-b",
    "component-ensemble-a",
    "component-ensemble-b",
    "candidate-a",
    "candidate-b",
    "component-selection-audit",
)


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


def png_dimensions(path: Path) -> tuple[int, int]:
    try:
        with path.open("rb") as source:
            header = source.read(24)
    except OSError as exc:
        raise ValueError(f"cannot read PNG {path}: {exc}") from exc
    if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) < 24:
        raise ValueError(f"not a PNG: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def resolve_manifest_file(base: Path, relative: Path, label: str, failures: list):
    candidate = base / relative
    if not candidate.is_file():
        failures.append(f"{label} is missing")
        return None
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(base.resolve())
    except (OSError, ValueError):
        failures.append(f"{label} resolves outside the manifest directory")
        return None
    return resolved


def validate_render_manifest(path: Path, expected_slides: int) -> list[str]:
    failures: list[str] = []
    manifest = read_json(path)
    if manifest.get("schema_version") != RENDER_MANIFEST_SCHEMA_VERSION:
        failures.append(
            f"render manifest schema_version must be {RENDER_MANIFEST_SCHEMA_VERSION}"
        )
    for name in ("renderer", "renderer_version", "command", "generated_at"):
        if not isinstance(manifest.get(name), str) or not manifest[name].strip():
            failures.append(f"render manifest {name} is missing")
    toolchain = manifest.get("toolchain")
    if not isinstance(toolchain, dict):
        failures.append("render manifest toolchain is missing")
    else:
        for name in sorted(RENDER_TOOLCHAIN_FIELDS):
            if not isinstance(toolchain.get(name), str) or not toolchain[name].strip():
                failures.append(f"render manifest toolchain {name} is missing")
        for name in ("renderer", "renderer_version", "command"):
            if isinstance(toolchain.get(name), str) and manifest.get(name) != toolchain[name]:
                failures.append(f"render manifest top-level {name} disagrees with toolchain")
    producer = manifest.get("producer")
    if not isinstance(producer, dict):
        failures.append("render manifest producer is missing")
    else:
        kind = producer.get("kind")
        command = producer.get("command")
        if kind not in {"manual", "script"}:
            failures.append("render manifest producer kind must be manual or script")
        if not isinstance(command, str) or not command.strip():
            failures.append("render manifest producer command is missing")
        if kind == "script":
            for field in ("source_path", "source_sha256"):
                if not isinstance(producer.get(field), str) or not producer[field].strip():
                    failures.append(f"render manifest script producer {field} is missing")
            source_text = producer.get("source_path")
            if isinstance(source_text, str) and source_text.strip():
                source = Path(source_text)
                if source.is_absolute() or ".." in source.parts:
                    failures.append("render manifest producer source path must stay inside the manifest directory")
                else:
                    source = resolve_manifest_file(
                        path.parent, source, "render manifest producer source", failures,
                    )
                    if source is not None and producer.get("source_sha256") != sha256(source):
                        failures.append("render manifest producer source hash is stale")
            lock_path = producer.get("lockfile_path")
            lock_hash = producer.get("lockfile_sha256")
            if (lock_path is None) != (lock_hash is None):
                failures.append("render manifest producer lockfile path and hash must appear together")
            elif isinstance(lock_path, str) and lock_path.strip():
                lockfile = Path(lock_path)
                if lockfile.is_absolute() or ".." in lockfile.parts:
                    failures.append("render manifest producer lockfile path must stay inside the manifest directory")
                else:
                    lockfile = resolve_manifest_file(
                        path.parent, lockfile, "render manifest producer lockfile", failures,
                    )
                    if lockfile is not None and lock_hash != sha256(lockfile):
                        failures.append("render manifest producer lockfile hash is stale")
    if manifest.get("slide_count") != expected_slides:
        failures.append("render manifest declared slide count does not match PPTX")
    slides = manifest.get("slides")
    if not isinstance(slides, list) or len(slides) != expected_slides:
        return [*failures, "render manifest slide count does not match PPTX"]
    seen_paths: set[str] = set()
    for index, item in enumerate(slides, 1):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            failures.append(f"render manifest slide {index} is invalid")
            continue
        width = item.get("width")
        height = item.get("height")
        if (
            not isinstance(width, int) or isinstance(width, bool)
            or not isinstance(height, int) or isinstance(height, bool)
            or width <= 0 or height <= 0
        ):
            failures.append(f"render manifest slide {index} dimensions must be positive integers")
        image_path = Path(item["path"])
        if image_path.is_absolute():
            failures.append(f"render manifest slide {index} uses an absolute path")
            continue
        if ".." in image_path.parts:
            failures.append(f"render manifest slide {index} escapes the manifest directory")
            continue
        canonical = image_path.as_posix()
        if canonical in seen_paths:
            failures.append(f"render manifest slide {index} duplicates an earlier slide path")
            continue
        seen_paths.add(canonical)
        image = resolve_manifest_file(path.parent, image_path, f"rendered slide {index}", failures)
        if image is None:
            continue
        if item.get("sha256") != sha256(image):
            failures.append(f"rendered slide {index} hash is stale")
            continue
        if isinstance(width, int) and not isinstance(width, bool) and isinstance(height, int) and not isinstance(height, bool) and width > 0 and height > 0:
            try:
                actual_width, actual_height = png_dimensions(image)
            except ValueError as exc:
                failures.append(f"rendered slide {index} is invalid: {exc}")
            else:
                if (width, height) != (actual_width, actual_height):
                    failures.append(f"rendered slide {index} dimensions do not match PNG metadata")
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


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require_object(value: dict, name: str) -> dict:
    result = value.get(name)
    if not isinstance(result, dict):
        raise SystemExit(f"{name} must be an object")
    return result


def require_string(value: dict, name: str) -> str:
    result = value.get(name)
    if not isinstance(result, str) or not result.strip():
        raise SystemExit(f"{name} must be a non-empty string")
    return result


def unique_strings(value: dict, name: str) -> list[str]:
    result = require_list(value, name)
    if any(not isinstance(item, str) or not item.strip() for item in result):
        raise SystemExit(f"{name} must contain non-empty strings")
    if len(set(result)) != len(result):
        raise SystemExit(f"{name} must not contain duplicates")
    return result


def validate_hash_fields(value: dict, expected: dict[str, str], label: str) -> list[str]:
    failures: list[str] = []
    for name, digest in expected.items():
        if value.get(name) != digest:
            failures.append(f"{label} is stale for {name.removesuffix('_sha256')}")
    return failures


def point_id_sets(point_model: dict) -> tuple[set[str], set[str], set[str], set[str]]:
    claims: set[str] = set()
    for name in ("domain_core", "project_lens"):
        values = point_model.get(name, [])
        if not isinstance(values, list):
            raise SystemExit(f"Point {name} must be an array")
        for item in values:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                claims.add(item["id"])
    source_map = point_model.get("source_map", {})
    if isinstance(source_map, dict):
        claims.update(name for name in source_map if isinstance(name, str))
    model = require_object(point_model, "model")
    groups: dict[str, set[str]] = {}
    for name in ("nodes", "edges", "boundaries"):
        values = model.get(name)
        if not isinstance(values, list):
            raise SystemExit(f"Point model {name} must be an array")
        groups[name] = {
            item["id"] for item in values
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        if len(groups[name]) != len(values):
            raise SystemExit(f"Point model {name} require unique string IDs")
    return claims, groups["nodes"], groups["edges"], groups["boundaries"]


def score_criteria(
    value: dict,
    weights: dict[str, int],
    label: str,
    minimum_each: int | None = None,
) -> tuple[float, list[str]]:
    criteria = require_object(value, "criteria")
    failures: list[str] = []
    if set(criteria) != set(weights):
        failures.append(f"{label} criteria do not match the fixed rubric")
    total = 0.0
    for name, weight in weights.items():
        row = criteria.get(name)
        if not isinstance(row, dict):
            raise SystemExit(f"{label}.{name} must be an object")
        score = row.get("score")
        justification = row.get("justification")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 1 <= score <= 5:
            raise SystemExit(f"{label}.{name}.score must be from 1 to 5")
        if not isinstance(justification, str) or not justification.strip():
            failures.append(f"{label}.{name} lacks evidence-based justification")
        if minimum_each is not None and score < minimum_each:
            failures.append(f"{label}.{name} below {minimum_each}/5")
        total += score / 5.0 * weight
    return round(total, 2), failures


def validate_component_rubric(rubric: dict) -> list[str]:
    failures: list[str] = []
    if require_object(rubric, "individual_weights") != INDIVIDUAL_COMPONENT_WEIGHTS:
        failures.append("component rubric individual weights changed")
    if require_object(rubric, "ensemble_weights") != ENSEMBLE_WEIGHTS:
        failures.append("component rubric ensemble weights changed")
    thresholds = require_object(rubric, "thresholds")
    expected_thresholds = {
        "dominant_component_minimum": 80,
        "supporting_component_minimum": 70,
        "ensemble_minimum": 90,
        "maximum_non_diagram_support_blocks": 3,
        "final_slide_gate_minimum": 90,
        "final_criterion_minimum": 4,
    }
    for name, expected in expected_thresholds.items():
        if thresholds.get(name) != expected:
            failures.append(f"component rubric threshold {name} must remain {expected}")
    hard_failures = set(unique_strings(rubric, "hard_failure_codes"))
    if not REQUIRED_COMPONENT_HARD_FAILURES.issubset(hard_failures):
        failures.append("component rubric omits required hard-failure codes")
    anchors = require_object(rubric, "anchors")
    for criterion in set(INDIVIDUAL_COMPONENT_WEIGHTS) | set(ENSEMBLE_WEIGHTS):
        rows = anchors.get(criterion)
        if not isinstance(rows, dict):
            failures.append(f"component rubric lacks anchors for {criterion}")
            continue
        for score in range(1, 6):
            text = rows.get(str(score))
            if not isinstance(text, str) or not text.strip():
                failures.append(f"component rubric lacks {criterion} anchor {score}")
    source_hash = rubric.get("rubric_source_sha256")
    if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", source_hash):
        failures.append("component rubric source hash is invalid")
    else:
        source_path = Path(__file__).resolve().parents[1] / "references" / "component-selection.md"
        if source_hash != sha256(source_path):
            failures.append("component rubric source hash is stale")
    return failures


def component_candidate_seed(branch: str, hashes: dict[str, str]) -> str:
    return canonical_sha256({
        "branch": branch,
        "point_sha256": hashes["point_sha256"],
        "point_model_sha256": hashes["point_model_sha256"],
        "visual_baseline_sha256": hashes["visual_baseline_sha256"],
        "constraints_sha256": hashes["constraints_sha256"],
        "component_rubric_sha256": hashes["component_rubric_sha256"],
    })


def validate_component_catalog(catalog: dict) -> tuple[list[str], dict[str, dict]]:
    failures: list[str] = []
    source_hash = catalog.get("catalog_source_sha256")
    source_path = Path(__file__).resolve().parents[1] / "references" / "component-catalog.md"
    if source_hash != sha256(source_path):
        failures.append("visual component catalog source hash is stale")
    if catalog.get("open_catalog") is not True:
        failures.append("visual component catalog must remain open to custom extensions")
    families: dict[str, dict] = {}
    for key, role in (("dominant_families", "dominant"), ("supporting_families", "supporting")):
        rows = require_list(catalog, key)
        for row in rows:
            if not isinstance(row, dict):
                raise SystemExit(f"catalog {key} entries must be objects")
            family_id = require_string(row, "id")
            if family_id in families:
                failures.append(f"catalog family {family_id} is duplicated")
            if row.get("role") != role:
                failures.append(f"catalog family {family_id} has the wrong role")
            jobs = unique_strings(row, "visual_jobs")
            if not jobs:
                failures.append(f"catalog family {family_id} has no visual jobs")
            if row.get("meaning_bearing") is not True:
                failures.append(f"catalog family {family_id} must be meaning-bearing")
            families[family_id] = row
    if not DEFAULT_DOMINANT_FAMILIES.issubset(families):
        failures.append("visual component catalog omits a default dominant family")
    if not DEFAULT_SUPPORTING_FAMILIES.issubset(families):
        failures.append("visual component catalog omits a default supporting family")
    excluded = set(unique_strings(catalog, "non_semantic_exclusions"))
    if not NON_SEMANTIC_FAMILIES.issubset(excluded):
        failures.append("catalog must exclude page numbers, decorative icons, and simple backgrounds")
    return failures, families


def validate_visual_jobs(
    value: dict,
    label: str,
    valid_claims: set[str],
    valid_nodes: set[str],
    valid_edges: set[str],
    valid_boundaries: set[str],
    must_ids: set[str],
    required_sets: dict[str, set[str]],
    families: dict[str, dict],
) -> tuple[list[str], dict]:
    failures: list[str] = []
    jobs = require_list(value, "visual_jobs")
    job_ids: set[str] = set()
    covered_baseline: set[str] = set()
    covered_claims: set[str] = set()
    covered_model: set[str] = set()
    critical_baseline: set[str] = set()
    critical_job_ids: set[str] = set()
    job_types: dict[str, str] = {}
    job_claim_ids: dict[str, set[str]] = {}
    job_model_ids: dict[str, set[str]] = {}
    job_baseline_ids: dict[str, set[str]] = {}
    valid_model = valid_nodes | valid_edges | valid_boundaries
    for row in jobs:
        if not isinstance(row, dict):
            raise SystemExit(f"{label} visual jobs must be objects")
        job_id = require_string(row, "id")
        if job_id in job_ids:
            failures.append(f"{label} duplicates visual job {job_id}")
        job_ids.add(job_id)
        job_type = require_string(row, "visual_job")
        if job_type not in VISUAL_JOB_TYPES and not job_type.startswith("custom-"):
            failures.append(f"{label} uses unknown visual job {job_type} without custom- prefix")
        job_types[job_id] = job_type
        claim_ids = set(unique_strings(row, "claim_ids"))
        model_ids = set(unique_strings(row, "model_ids"))
        baseline_ids = set(unique_strings(row, "baseline_ids"))
        job_claim_ids[job_id] = claim_ids
        job_model_ids[job_id] = model_ids
        job_baseline_ids[job_id] = baseline_ids
        if not claim_ids or not model_ids or not baseline_ids:
            failures.append(f"{label} visual job {job_id} must link Claim, Model, and baseline IDs")
        if not claim_ids.issubset(valid_claims):
            failures.append(f"{label} visual job {job_id} references unknown Point claims")
        if not model_ids.issubset(valid_model):
            failures.append(f"{label} visual job {job_id} references unknown model IDs")
        if not baseline_ids.issubset(must_ids):
            failures.append(f"{label} visual job {job_id} references unknown baseline IDs")
        criticality = row.get("criticality")
        if criticality not in {"critical", "important", "supporting"}:
            failures.append(f"{label} visual job {job_id} has invalid criticality")
        audiences = set(unique_strings(row, "intended_audiences"))
        if not audiences or not audiences.issubset({"novice_developer", "technical_executive"}):
            failures.append(f"{label} visual job {job_id} has invalid intended audience")
        require_string(row, "expected_cold_read_answer")
        unique_strings(row, "distinction_ids")
        covered_claims.update(claim_ids)
        covered_model.update(model_ids)
        covered_baseline.update(baseline_ids)
        if criticality == "critical":
            critical_job_ids.add(job_id)
            critical_baseline.update(baseline_ids)
    if must_ids - covered_baseline:
        failures.append(f"{label} visual jobs miss baseline IDs: " + ", ".join(sorted(must_ids - covered_baseline)))
    for name, required in required_sets.items():
        if not required.issubset(covered_baseline):
            failures.append(f"{label} visual jobs miss {name}")
    critical_relationship_ids = set(unique_strings(value, "critical_relationship_ids"))
    critical_boundary_ids = set(unique_strings(value, "critical_boundary_ids"))
    if not critical_relationship_ids.issubset(valid_edges):
        failures.append(f"{label} has unknown critical relationship IDs")
    if not critical_boundary_ids.issubset(valid_boundaries):
        failures.append(f"{label} has unknown critical boundary IDs")
    if valid_edges and not critical_relationship_ids:
        failures.append(f"{label} must identify critical relationships")
    if valid_boundaries and not critical_boundary_ids:
        failures.append(f"{label} must identify critical trust boundaries")
    distinctions = require_list(value, "distinctions")
    distinction_ids: set[str] = set()
    critical_distinctions: set[str] = set()
    distinction_sides: dict[str, tuple[set[str], set[str]]] = {}
    valid_distinction_targets = valid_claims | valid_model
    for row in distinctions:
        if not isinstance(row, dict):
            raise SystemExit(f"{label} distinctions must be objects")
        distinction_id = require_string(row, "id")
        if distinction_id in distinction_ids:
            failures.append(f"{label} duplicates distinction {distinction_id}")
        distinction_ids.add(distinction_id)
        left = set(unique_strings(row, "left_ids"))
        right = set(unique_strings(row, "right_ids"))
        baseline_ids = set(unique_strings(row, "baseline_ids"))
        if not left or not right or left & right:
            failures.append(f"{label} distinction {distinction_id} does not separate two sides")
        if not (left | right).issubset(valid_distinction_targets):
            failures.append(f"{label} distinction {distinction_id} references unknown IDs")
        if not baseline_ids or not baseline_ids.issubset(must_ids):
            failures.append(f"{label} distinction {distinction_id} has invalid baseline IDs")
        if row.get("critical") is True:
            critical_distinctions.add(distinction_id)
        distinction_sides[distinction_id] = (left, right)
    for row in jobs:
        if not set(row["distinction_ids"]).issubset(distinction_ids):
            failures.append(f"{label} visual job {row['id']} references unknown distinctions")
    required_distinctions = set(unique_strings(value, "required_distinction_ids"))
    if required_distinctions != critical_distinctions:
        failures.append(f"{label} required distinctions do not match critical distinctions")
    applicable = unique_strings(value, "applicable_dominant_families")
    if len(applicable) < 2:
        failures.append(f"{label} must consider at least two dominant component families")
    for family_id in applicable:
        row = families.get(family_id)
        if row is None or row.get("role") != "dominant":
            failures.append(f"{label} applicable dominant family {family_id} is invalid")
    path_rows = require_list(value, "required_causal_path")
    expected_stages = ["evidence", "evaluation", "authenticated_result", "policy_action"]
    actual_stages: list[str] = []
    path_claim_ids: set[str] = set()
    path_model_ids: set[str] = set()
    path_baseline_ids: set[str] = set()
    for row in path_rows:
        if not isinstance(row, dict):
            raise SystemExit(f"{label} required causal path rows must be objects")
        stage = require_string(row, "stage")
        actual_stages.append(stage)
        claim_ids = set(unique_strings(row, "claim_ids"))
        model_ids = set(unique_strings(row, "model_ids"))
        baseline_ids = set(unique_strings(row, "baseline_ids"))
        if not claim_ids or not model_ids or not baseline_ids:
            failures.append(f"{label} causal stage {stage} must link Claim, Model, and baseline IDs")
        if not claim_ids.issubset(valid_claims) or not model_ids.issubset(valid_model) or not baseline_ids.issubset(must_ids):
            failures.append(f"{label} causal stage {stage} references unknown IDs")
        path_claim_ids.update(claim_ids)
        path_model_ids.update(model_ids)
        path_baseline_ids.update(baseline_ids)
    if actual_stages != expected_stages:
        failures.append(f"{label} must preserve Evidence → evaluation → authenticated Result → policy action")
    return failures, {
        "job_ids": job_ids,
        "job_types": job_types,
        "job_claim_ids": job_claim_ids,
        "job_model_ids": job_model_ids,
        "job_baseline_ids": job_baseline_ids,
        "critical_job_ids": critical_job_ids,
        "covered_baseline": covered_baseline,
        "covered_claims": covered_claims,
        "covered_model": covered_model,
        "critical_baseline": critical_baseline,
        "critical_relationship_ids": critical_relationship_ids,
        "critical_boundary_ids": critical_boundary_ids,
        "distinction_ids": distinction_ids,
        "required_distinction_ids": required_distinctions,
        "distinction_sides": distinction_sides,
        "applicable_dominant_families": set(applicable),
        "path_claim_ids": path_claim_ids,
        "path_model_ids": path_model_ids,
        "path_baseline_ids": path_baseline_ids,
    }


def validate_component_scores(
    value: dict,
    label: str,
    jobs: dict,
    families: dict[str, dict],
    valid_claims: set[str],
    valid_model: set[str],
    must_ids: set[str],
    point_structural: bool,
) -> tuple[list[str], dict[str, dict]]:
    failures: list[str] = []
    for name in ("other_candidate_seen", "other_scores_seen", "other_visual_grammar_seen"):
        if value.get(name) is not False:
            failures.append(f"{label} independence check {name} must be false")
    considered = set(unique_strings(value, "considered_dominant_families"))
    if considered != jobs["applicable_dominant_families"]:
        failures.append(f"{label} did not score every applicable dominant family")
    components: dict[str, dict] = {}
    scored_families: set[str] = set()
    for row in require_list(value, "components"):
        if not isinstance(row, dict):
            raise SystemExit(f"{label} components must be objects")
        component_id = require_string(row, "component_id")
        if component_id in components:
            failures.append(f"{label} duplicates component {component_id}")
        role = row.get("role")
        if role not in {"dominant", "supporting"}:
            failures.append(f"{label} component {component_id} has invalid role")
        family_id = require_string(row, "family")
        family = families.get(family_id)
        if family is None:
            extension = row.get("catalog_extension")
            if not isinstance(extension, dict) or not str(extension.get("definition", "")).strip() or not str(extension.get("job_fit", "")).strip():
                failures.append(f"{label} custom family {family_id} lacks an explicit catalog extension")
        elif family.get("role") != role:
            failures.append(f"{label} component {component_id} conflicts with catalog role")
        if family_id in NON_SEMANTIC_FAMILIES:
            failures.append(f"{label} scores non-semantic decoration as a component")
        visual_job_ids = set(unique_strings(row, "visual_job_ids"))
        if not visual_job_ids or not visual_job_ids.issubset(jobs["job_ids"]):
            failures.append(f"{label} component {component_id} has invalid visual-job coverage")
        covered_baseline = set(unique_strings(row, "covered_baseline_ids"))
        covered_point = set(unique_strings(row, "covered_point_ids"))
        covered_model = set(unique_strings(row, "covered_model_ids"))
        if not covered_baseline.issubset(must_ids):
            failures.append(f"{label} component {component_id} covers unknown baseline IDs")
        if not covered_point.issubset(valid_claims):
            failures.append(f"{label} component {component_id} covers unknown Point IDs")
        if not covered_model.issubset(valid_model):
            failures.append(f"{label} component {component_id} covers unknown model IDs")
        uncovered = require_object(row, "uncovered_ids")
        for key in ("baseline_ids", "point_ids", "model_ids"):
            unique_strings(uncovered, key)
        preserved = set(unique_strings(row, "preserved_distinction_ids"))
        if not preserved.issubset(jobs["distinction_ids"]):
            failures.append(f"{label} component {component_id} preserves unknown distinctions")
        risks = unique_strings(row, "risks")
        hard_failures = unique_strings(row, "hard_failures")
        assumptions = unique_strings(row, "assumptions")
        if not risks or not assumptions:
            failures.append(f"{label} component {component_id} must record risks and assumptions")
        for code in hard_failures:
            if code not in REQUIRED_COMPONENT_HARD_FAILURES and not code.startswith("custom-"):
                failures.append(f"{label} component {component_id} has an unregistered hard failure")
        normalized, score_failures = score_criteria(row, INDIVIDUAL_COMPONENT_WEIGHTS, f"{label}.{component_id}")
        failures.extend(score_failures)
        declared = row.get("normalized_score")
        if not isinstance(declared, (int, float)) or isinstance(declared, bool) or abs(declared - normalized) > 0.01:
            failures.append(f"{label} component {component_id} normalized score is wrong")
        auto_hard_failure = False
        if point_structural and family_id in {"generic-card-grid", "card-grid", "decorative-card-grid"}:
            auto_hard_failure = True
            if "decorative-card-listing" not in hard_failures:
                failures.append(f"{label} structural generic card grid lacks decorative-card-listing hard failure")
        if role == "dominant" and point_structural:
            types = {jobs["job_types"][job_id] for job_id in visual_job_ids}
            if not types & STRUCTURAL_VISUAL_JOBS:
                auto_hard_failure = True
                failures.append(f"{label} dominant component {component_id} cannot express the structural path")
        threshold = 80 if role == "dominant" else 70
        expected_eligible = normalized >= threshold and not hard_failures and not auto_hard_failure
        if row.get("eligible") is not expected_eligible:
            failures.append(f"{label} component {component_id} eligibility conflicts with score or hard failures")
        if role == "dominant":
            scored_families.add(family_id)
        components[component_id] = {
            **row,
            "role": role,
            "family": family_id,
            "visual_job_ids_set": visual_job_ids,
            "covered_baseline_set": covered_baseline,
            "covered_point_set": covered_point,
            "covered_model_set": covered_model,
            "preserved_distinction_set": preserved,
            "calculated_score": normalized,
            "eligible_value": expected_eligible,
        }
    if not considered.issubset(scored_families):
        failures.append(f"{label} lacks a scored component for an applicable dominant family")
    return failures, components


def validate_component_ensemble(
    value: dict,
    label: str,
    components: dict[str, dict],
    jobs: dict,
    required_sets: dict[str, set[str]],
) -> tuple[list[str], dict]:
    failures: list[str] = []
    for name in ("other_candidate_seen", "other_scores_seen", "other_visual_grammar_seen"):
        if value.get(name) is not False:
            failures.append(f"{label} independence check {name} must be false")
    dominant_id = require_string(value, "dominant_component_id")
    supporting_ids = unique_strings(value, "supporting_component_ids")
    selected_ids = unique_strings(value, "selected_component_ids")
    if selected_ids != [dominant_id, *supporting_ids]:
        failures.append(f"{label} selected components must list one dominant followed by supports")
    if len(supporting_ids) > 3:
        failures.append(f"{label} selects more than three supporting components")
    if len(selected_ids) > 4:
        failures.append(f"{label} overloads the slide with unnecessary components")
    selected: list[dict] = []
    for component_id in selected_ids:
        component = components.get(component_id)
        if component is None:
            failures.append(f"{label} selects unknown component {component_id}")
            continue
        if component["eligible_value"] is not True:
            failures.append(f"{label} selects ineligible component {component_id}")
        selected.append(component)
    dominant = components.get(dominant_id)
    if dominant is not None:
        if dominant["role"] != "dominant" or dominant["calculated_score"] < 80:
            failures.append(f"{label} dominant component is below 80 or has the wrong role")
    for component_id in supporting_ids:
        component = components.get(component_id)
        if component is not None and (component["role"] != "supporting" or component["calculated_score"] < 70):
            failures.append(f"{label} supporting component {component_id} is below 70 or has the wrong role")
    accumulated = set(dominant["covered_baseline_set"] if dominant is not None else set())
    contributions = require_list(value, "support_contributions")
    if len(contributions) != len(supporting_ids):
        failures.append(f"{label} support contribution count is wrong")
    contribution_by_id = {
        row.get("component_id"): row for row in contributions if isinstance(row, dict)
    }
    for component_id in supporting_ids:
        component = components.get(component_id)
        row = contribution_by_id.get(component_id)
        if component is None or not isinstance(row, dict):
            continue
        incremental = component["covered_baseline_set"] - accumulated
        declared = set(unique_strings(row, "incremental_baseline_ids"))
        if not incremental or declared != incremental:
            failures.append(f"{label} support {component_id} adds no correctly declared new baseline meaning")
        value_type = row.get("incremental_value")
        if value_type not in {"critical_coverage", "meaningful_new_baseline"}:
            failures.append(f"{label} support {component_id} lacks an incremental-value classification")
        require_string(row, "justification")
        accumulated.update(component["covered_baseline_set"])
    coverage = require_object(value, "coverage")
    declared_baseline = set(unique_strings(coverage, "baseline_ids"))
    declared_point = set(unique_strings(coverage, "point_ids"))
    declared_model = set(unique_strings(coverage, "model_ids"))
    union_baseline = set().union(*(item["covered_baseline_set"] for item in selected)) if selected else set()
    union_point = set().union(*(item["covered_point_set"] for item in selected)) if selected else set()
    union_model = set().union(*(item["covered_model_set"] for item in selected)) if selected else set()
    if declared_baseline != union_baseline or declared_point != union_point or declared_model != union_model:
        failures.append(f"{label} declared coverage does not equal selected component coverage")
    for name, required in required_sets.items():
        if not required.issubset(declared_baseline):
            failures.append(f"{label} misses required baseline set {name}")
    if not jobs["critical_relationship_ids"].issubset(declared_model):
        failures.append(f"{label} omits a critical relationship")
    if not jobs["critical_boundary_ids"].issubset(declared_model):
        failures.append(f"{label} omits a critical trust boundary")
    if not jobs["path_claim_ids"].issubset(declared_point):
        failures.append(f"{label} breaks the required causal path at a Point claim")
    if not jobs["path_model_ids"].issubset(declared_model):
        failures.append(f"{label} breaks the required causal path at a model relationship")
    if not jobs["path_baseline_ids"].issubset(declared_baseline):
        failures.append(f"{label} breaks the required causal path at a must-see ID")
    preserved = set(unique_strings(value, "preserved_distinction_ids"))
    actual_preserved = set().union(*(item["preserved_distinction_set"] for item in selected)) if selected else set()
    if preserved != actual_preserved or not jobs["required_distinction_ids"].issubset(preserved):
        failures.append(f"{label} collapses or omits a required distinction")
    occurrence_count: dict[str, int] = {}
    for component in selected:
        for baseline_id in component["covered_baseline_set"]:
            occurrence_count[baseline_id] = occurrence_count.get(baseline_id, 0) + 1
    duplicate_assignments = sum(max(0, count - 1) for count in occurrence_count.values())
    expected_penalty = min(20, duplicate_assignments * 5)
    if value.get("redundancy_penalty") != expected_penalty:
        failures.append(f"{label} redundancy penalty is wrong")
    raw_score, score_failures = score_criteria(value, ENSEMBLE_WEIGHTS, label, minimum_each=4)
    failures.extend(score_failures)
    normalized = round(raw_score - expected_penalty, 2)
    declared_score = value.get("ensemble_score")
    if not isinstance(declared_score, (int, float)) or isinstance(declared_score, bool) or abs(declared_score - normalized) > 0.01:
        failures.append(f"{label} ensemble score is wrong")
    if normalized < 90:
        failures.append(f"{label} ensemble score below 90")
    if unique_strings(value, "hard_failures"):
        failures.append(f"{label} ensemble has a hard failure")
    if unique_strings(value, "unnecessary_component_ids"):
        failures.append(f"{label} ensemble contains unnecessary components")
    require_string(value, "dominant_visual_argument")
    standard_eligible = [
        item for item in components.values()
        if item["role"] == "dominant" and item["family"] != "custom-domain-diagram" and item["eligible_value"]
    ]
    if dominant is not None and dominant["family"] == "custom-domain-diagram":
        if standard_eligible:
            failures.append(f"{label} uses custom fallback while an eligible standard dominant exists")
        require_string(value, "custom_fallback_reason")
    elif not standard_eligible:
        failures.append(f"{label} must fall back to a custom domain diagram")
    return failures, {
        "dominant_component_id": dominant_id,
        "supporting_component_ids": supporting_ids,
        "selected_component_ids": selected_ids,
        "coverage_baseline": declared_baseline,
        "coverage_point": declared_point,
        "coverage_model": declared_model,
        "preserved_distinction_ids": preserved,
        "distinction_sides": {
            distinction_id: jobs["distinction_sides"][distinction_id]
            for distinction_id in jobs["required_distinction_ids"]
        },
        "ensemble_score": normalized,
    }


def validate_storyboard_candidate(
    value: dict,
    label: str,
    ensemble: dict,
    jobs: dict,
    must_ids: set[str],
) -> tuple[list[str], dict]:
    failures: list[str] = []
    require_string(value, "visual_grammar")
    require_string(value, "narrative_job")
    require_string(value, "headline")
    if value.get("dominant_component_id") != ensemble["dominant_component_id"]:
        failures.append(f"{label} dominant component differs from its ensemble")
    if unique_strings(value, "selected_component_ids") != ensemble["selected_component_ids"]:
        failures.append(f"{label} selected components differ from its ensemble")
    object_map = require_list(value, "object_map")
    mapped_baseline: set[str] = set()
    mapped_point: set[str] = set()
    mapped_model: set[str] = set()
    for row in object_map:
        if not isinstance(row, dict):
            raise SystemExit(f"{label} object_map rows must be objects")
        require_string(row, "planned_object_id")
        mapped_baseline.update(unique_strings(row, "baseline_ids"))
        row_point = set(unique_strings(row, "point_ids"))
        row_model = set(unique_strings(row, "model_ids"))
        mapped_point.update(row_point)
        mapped_model.update(row_model)
        component_id = require_string(row, "component_id")
        if component_id not in ensemble["selected_component_ids"]:
            failures.append(f"{label} object map uses unselected component {component_id}")
        if not set(row["baseline_ids"]).issubset(must_ids):
            failures.append(f"{label} object map references unknown baseline IDs")
        if not row_point.issubset(ensemble["coverage_point"]):
            failures.append(f"{label} object map references unselected Point IDs")
        if not row_model.issubset(ensemble["coverage_model"]):
            failures.append(f"{label} object map references unselected model IDs")
        row_semantics = row_point | row_model
        for distinction_id in jobs["required_distinction_ids"]:
            left, right = jobs["distinction_sides"][distinction_id]
            if row_semantics & left and row_semantics & right:
                failures.append(f"{label} object map collapses distinction {distinction_id}")
    if not must_ids.issubset(mapped_baseline):
        failures.append(f"{label} object map misses baseline IDs")
    if not ensemble["coverage_point"].issubset(mapped_point):
        failures.append(f"{label} object map misses selected Point IDs")
    if not ensemble["coverage_model"].issubset(mapped_model):
        failures.append(f"{label} object map misses selected model IDs")
    signature = require_object(value, "visual_grammar_signature")
    for name in ("dominant_family", "composition_pattern", "primary_encoding", "path_topology"):
        require_string(signature, name)
    support_blocks = require_list(value, "support_blocks")
    if len(support_blocks) > 3:
        failures.append(f"{label} plans more than three support blocks")
    for name in ("reading_order", "omissions", "density_risks", "accessibility_risks"):
        unique_strings(value, name)
    return failures, {"signature": signature, "mapped_baseline": mapped_baseline}


def materially_different_grammar(a: dict, b: dict) -> bool:
    fields = ("dominant_family", "composition_pattern", "primary_encoding", "path_topology")
    differences = sum(a.get(name) != b.get(name) for name in fields)
    return a.get("dominant_family") != b.get("dominant_family") or differences >= 2


def validate_component_selection_bundle(paths: dict[str, Path]) -> tuple[list[str], dict]:
    failures: list[str] = []
    round_artifact_keys = (
        "visual_jobs_a", "visual_jobs_b", "component_score_a", "component_score_b",
        "component_ensemble_a", "component_ensemble_b", "candidate_a", "candidate_b",
        "component_selection_audit",
    )
    artifact_rounds: dict[str, int] = {}
    for key in round_artifact_keys:
        value = read_json(paths[key])
        round_value = value.get("round")
        if not isinstance(round_value, int) or isinstance(round_value, bool) or round_value < 1:
            failures.append(f"{key} has no valid immutable round")
        else:
            artifact_rounds[key] = round_value
    distinct_rounds = set(artifact_rounds.values())
    if len(artifact_rounds) != len(round_artifact_keys) or len(distinct_rounds) != 1:
        failures.append("visual component artifacts do not share one immutable round")
    bundle_round = next(iter(distinct_rounds)) if len(distinct_rounds) == 1 else None
    point_model = read_yaml(paths["point_model"])
    baseline = read_json(paths["visual_baseline"])
    must_see = require_list(baseline, "must_see")
    must_ids = {
        row.get("id") for row in must_see
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    if len(must_ids) != len(must_see) or not must_ids:
        failures.append("visual baseline must-see IDs are missing or duplicated")
    required_sets: dict[str, set[str]] = {}
    for name in REQUIRED_BASELINE_SETS:
        required_sets[name] = set(unique_strings(baseline, name))
        if not required_sets[name].issubset(must_ids):
            failures.append(f"visual baseline {name} contains invalid IDs")
    valid_claims, valid_nodes, valid_edges, valid_boundaries = point_id_sets(point_model)
    valid_model = valid_nodes | valid_edges | valid_boundaries
    point_structural = len(valid_nodes) >= 3 or len(valid_edges) >= 2
    hashes = {
        "point_sha256": sha256(paths["point"]),
        "point_model_sha256": sha256(paths["point_model"]),
        "visual_baseline_sha256": sha256(paths["visual_baseline"]),
        "constraints_sha256": sha256(paths["constraints"]),
        "component_rubric_sha256": sha256(paths["component_rubric"]),
        "component_catalog_sha256": sha256(paths["component_catalog"]),
    }
    rubric = read_json(paths["component_rubric"])
    failures.extend(validate_hash_fields(rubric, {
        name: hashes[name] for name in (
            "point_sha256", "point_model_sha256", "visual_baseline_sha256", "constraints_sha256"
        )
    }, "component rubric"))
    failures.extend(validate_component_rubric(rubric))
    catalog = read_json(paths["component_catalog"])
    failures.extend(validate_hash_fields(catalog, {
        name: hashes[name] for name in (
            "point_sha256", "point_model_sha256", "visual_baseline_sha256",
            "constraints_sha256", "component_rubric_sha256",
        )
    }, "component catalog"))
    catalog_failures, families = validate_component_catalog(catalog)
    failures.extend(catalog_failures)
    seeds = {branch: component_candidate_seed(branch, hashes) for branch in ("A", "B")}
    if catalog.get("candidate_seed_sha256") != seeds:
        failures.append("component catalog candidate seed hashes are stale")
    jobs_values: dict[str, dict] = {}
    jobs_summaries: dict[str, dict] = {}
    score_values: dict[str, dict] = {}
    component_maps: dict[str, dict[str, dict]] = {}
    ensemble_values: dict[str, dict] = {}
    ensemble_summaries: dict[str, dict] = {}
    candidate_values: dict[str, dict] = {}
    candidate_summaries: dict[str, dict] = {}
    branch_paths = {
        "A": ("visual_jobs_a", "component_score_a", "component_ensemble_a", "candidate_a"),
        "B": ("visual_jobs_b", "component_score_b", "component_ensemble_b", "candidate_b"),
    }
    base_expected = {
        name: hashes[name] for name in (
            "point_sha256", "point_model_sha256", "visual_baseline_sha256",
            "constraints_sha256", "component_rubric_sha256", "component_catalog_sha256",
        )
    }
    for branch, (jobs_key, score_key, ensemble_key, candidate_key) in branch_paths.items():
        jobs = read_json(paths[jobs_key])
        jobs_values[branch] = jobs
        expected = {**base_expected, "candidate_seed_sha256": seeds[branch]}
        failures.extend(validate_hash_fields(jobs, expected, f"visual jobs {branch}"))
        branch_failures, jobs_summary = validate_visual_jobs(
            jobs, f"visual jobs {branch}", valid_claims, valid_nodes, valid_edges,
            valid_boundaries, must_ids, required_sets, families,
        )
        failures.extend(branch_failures)
        jobs_summaries[branch] = jobs_summary
        scores = read_json(paths[score_key])
        score_values[branch] = scores
        expected_scores = {**expected, "visual_jobs_sha256": sha256(paths[jobs_key])}
        failures.extend(validate_hash_fields(scores, expected_scores, f"component scores {branch}"))
        score_failures, component_map = validate_component_scores(
            scores, f"component scores {branch}", jobs_summary, families,
            valid_claims, valid_model, must_ids, point_structural,
        )
        failures.extend(score_failures)
        component_maps[branch] = component_map
        ensemble = read_json(paths[ensemble_key])
        ensemble_values[branch] = ensemble
        expected_ensemble = {**expected_scores, "component_score_sha256": sha256(paths[score_key])}
        failures.extend(validate_hash_fields(ensemble, expected_ensemble, f"component ensemble {branch}"))
        ensemble_failures, ensemble_summary = validate_component_ensemble(
            ensemble, f"component ensemble {branch}", component_map, jobs_summary,
            {**required_sets, "complete_must_see_coverage": must_ids},
        )
        failures.extend(ensemble_failures)
        ensemble_summaries[branch] = ensemble_summary
        candidate = read_json(paths[candidate_key])
        candidate_values[branch] = candidate
        expected_candidate = {
            **expected_ensemble,
            "component_ensemble_sha256": sha256(paths[ensemble_key]),
        }
        failures.extend(validate_hash_fields(candidate, expected_candidate, f"candidate {branch}"))
        candidate_failures, candidate_summary = validate_storyboard_candidate(
            candidate, f"candidate {branch}", ensemble_summary, jobs_summary, must_ids,
        )
        failures.extend(candidate_failures)
        candidate_summaries[branch] = candidate_summary
    if not materially_different_grammar(
        candidate_summaries["A"]["signature"], candidate_summaries["B"]["signature"]
    ):
        failures.append("storyboard candidates use the same visual grammar")
    audit = read_json(paths["component_selection_audit"])
    audit_expected = {
        **base_expected,
        "visual_jobs_a_sha256": sha256(paths["visual_jobs_a"]),
        "visual_jobs_b_sha256": sha256(paths["visual_jobs_b"]),
        "component_score_a_sha256": sha256(paths["component_score_a"]),
        "component_score_b_sha256": sha256(paths["component_score_b"]),
        "component_ensemble_a_sha256": sha256(paths["component_ensemble_a"]),
        "component_ensemble_b_sha256": sha256(paths["component_ensemble_b"]),
        "candidate_a_sha256": sha256(paths["candidate_a"]),
        "candidate_b_sha256": sha256(paths["candidate_b"]),
    }
    failures.extend(validate_hash_fields(audit, audit_expected, "component selection audit"))
    for name in (
        "candidate_names_hidden", "author_information_hidden",
        "author_aggregate_scores_hidden", "score_evidence_verified",
        "semantic_fidelity_rechecked", "redundancy_rechecked",
    ):
        if audit.get(name) is not True:
            failures.append(f"component selection audit {name} must be true")
    if unique_strings(audit, "hard_failures"):
        failures.append("component selection audit has hard failures")
    if unique_strings(audit, "critical_issues"):
        failures.append("component selection audit has critical issues")
    recomputed = require_object(audit, "recomputed_scores")
    for branch in ("A", "B"):
        branch_scores = require_object(recomputed, branch)
        component_scores = require_object(branch_scores, "components")
        expected_component_scores = {
            component_id: row["calculated_score"]
            for component_id, row in component_maps[branch].items()
        }
        if component_scores != expected_component_scores:
            failures.append(f"component selection audit recomputed component scores for {branch} are wrong")
        if branch_scores.get("ensemble") != ensemble_summaries[branch]["ensemble_score"]:
            failures.append(f"component selection audit recomputed ensemble score for {branch} is wrong")
    audited_coverage = set(unique_strings(audit, "verified_baseline_ids"))
    if audited_coverage != must_ids:
        failures.append("component selection audit does not verify every must-see baseline ID")
    selected_candidate = audit.get("selected_candidate")
    if selected_candidate not in {"A", "B", "synthesis"}:
        failures.append("component selection audit selected_candidate is invalid")
    require_string(audit, "selection_reason")
    if selected_candidate in {"A", "B"}:
        chosen = ensemble_summaries[selected_candidate]
    else:
        synthesis = require_object(audit, "synthesis")
        adopted_components = unique_strings(synthesis, "adopted_components")
        rejected_components = unique_strings(synthesis, "rejected_components")
        if not adopted_components or not rejected_components:
            failures.append("component synthesis must record adopted and rejected components")
        decisions = require_list(synthesis, "component_decisions")
        decision_ids: set[str] = set()
        for row in decisions:
            if not isinstance(row, dict):
                raise SystemExit("component synthesis decisions must be objects")
            component_id = require_string(row, "component_id")
            decision_ids.add(component_id)
            if row.get("decision") not in {"adopt", "reject"}:
                failures.append(f"component synthesis decision for {component_id} is invalid")
            require_string(row, "reason")
        if decision_ids != set(adopted_components) | set(rejected_components):
            failures.append("component synthesis decisions do not explain every adoption and rejection")
        merged_components: dict[str, dict] = {}
        for branch in ("A", "B"):
            for component_id, component in component_maps[branch].items():
                if component_id in merged_components:
                    failures.append(f"component synthesis has ambiguous component ID {component_id}")
                merged_components[component_id] = component
        dominant_id = require_string(synthesis, "dominant_component_id")
        supporting_ids = unique_strings(synthesis, "supporting_component_ids")
        selected_ids = unique_strings(synthesis, "selected_component_ids")
        if selected_ids != [dominant_id, *supporting_ids] or adopted_components != selected_ids:
            failures.append("component synthesis selection does not match its adopted components")
        if len(supporting_ids) > 3:
            failures.append("component synthesis selects more than three supporting components")
        selected_components = [merged_components[item] for item in selected_ids if item in merged_components]
        if len(selected_components) != len(selected_ids):
            failures.append("component synthesis selects an unknown component")
        for component in selected_components:
            if not component["eligible_value"]:
                failures.append(f"component synthesis selects ineligible component {component['component_id']}")
        dominant = merged_components.get(dominant_id)
        if dominant is not None and dominant["role"] != "dominant":
            failures.append("component synthesis dominant component has the wrong role")
        if any(merged_components[item]["role"] != "supporting" for item in supporting_ids if item in merged_components):
            failures.append("component synthesis support has the wrong role")
        contributions = require_list(synthesis, "support_contributions")
        contribution_by_id = {
            row.get("component_id"): row for row in contributions if isinstance(row, dict)
        }
        accumulated = set(dominant["covered_baseline_set"] if dominant is not None else set())
        if len(contributions) != len(supporting_ids):
            failures.append("component synthesis support contribution count is wrong")
        for component_id in supporting_ids:
            component = merged_components.get(component_id)
            row = contribution_by_id.get(component_id)
            if component is None or not isinstance(row, dict):
                continue
            incremental = component["covered_baseline_set"] - accumulated
            if set(unique_strings(row, "incremental_baseline_ids")) != incremental or not incremental:
                failures.append(f"component synthesis support {component_id} adds no new baseline meaning")
            if row.get("incremental_value") not in {"critical_coverage", "meaningful_new_baseline"}:
                failures.append(f"component synthesis support {component_id} lacks incremental value")
            require_string(row, "justification")
            accumulated.update(component["covered_baseline_set"])
        raw_synthesis_score, synthesis_score_failures = score_criteria(
            synthesis, ENSEMBLE_WEIGHTS, "component synthesis", minimum_each=4,
        )
        failures.extend(synthesis_score_failures)
        occurrence_count: dict[str, int] = {}
        for component in selected_components:
            for baseline_id in component["covered_baseline_set"]:
                occurrence_count[baseline_id] = occurrence_count.get(baseline_id, 0) + 1
        expected_penalty = min(20, sum(max(0, count - 1) for count in occurrence_count.values()) * 5)
        if synthesis.get("redundancy_penalty") != expected_penalty:
            failures.append("component synthesis redundancy penalty is wrong")
        expected_score = round(raw_synthesis_score - expected_penalty, 2)
        if synthesis.get("ensemble_score") != expected_score or expected_score < 90:
            failures.append("component synthesis ensemble score below 90")
        synthesis_coverage = set(unique_strings(synthesis, "baseline_ids"))
        synthesis_point = set(unique_strings(synthesis, "point_ids"))
        synthesis_model = set(unique_strings(synthesis, "model_ids"))
        union_baseline = set().union(*(item["covered_baseline_set"] for item in selected_components)) if selected_components else set()
        union_point = set().union(*(item["covered_point_set"] for item in selected_components)) if selected_components else set()
        union_model = set().union(*(item["covered_model_set"] for item in selected_components)) if selected_components else set()
        if synthesis_coverage != must_ids or synthesis_coverage != union_baseline:
            failures.append("component synthesis misses must-see baseline IDs")
        if synthesis_point != union_point or synthesis_model != union_model:
            failures.append("component synthesis coverage does not equal adopted component coverage")
        required_relationships = set().union(*(jobs_summaries[branch]["critical_relationship_ids"] for branch in ("A", "B")))
        required_boundaries = set().union(*(jobs_summaries[branch]["critical_boundary_ids"] for branch in ("A", "B")))
        if not required_relationships.issubset(synthesis_model) or not required_boundaries.issubset(synthesis_model):
            failures.append("component synthesis omits a critical relationship or trust boundary")
        required_distinctions = set().union(*(jobs_summaries[branch]["required_distinction_ids"] for branch in ("A", "B")))
        if not required_distinctions.issubset(set(unique_strings(synthesis, "preserved_distinction_ids"))):
            failures.append("component synthesis collapses a required distinction")
        if unique_strings(synthesis, "hard_failures") or unique_strings(synthesis, "unnecessary_component_ids"):
            failures.append("component synthesis has hard failures or unnecessary components")
        chosen = {
            "selected_component_ids": selected_ids,
            "coverage_baseline": synthesis_coverage,
            "coverage_point": synthesis_point,
            "coverage_model": synthesis_model,
            "ensemble_score": synthesis.get("ensemble_score"),
            "distinction_sides": {
                distinction_id: sides
                for branch in ("A", "B")
                for distinction_id, sides in ensemble_summaries[branch]["distinction_sides"].items()
            },
        }
    return failures, {
        "round": bundle_round,
        "hashes": hashes,
        "candidate_seeds": seeds,
        "selected_candidate": selected_candidate,
        "selected_ensemble": chosen,
        "audit_sha256": sha256(paths["component_selection_audit"]),
        "must_ids": must_ids,
    }


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


def command_component_gate(args: argparse.Namespace) -> int:
    paths = {
        name.replace("-", "_"): Path(getattr(args, name.replace("-", "_"))).resolve()
        for name in COMPONENT_BUNDLE_PATHS
    }
    failures = verify_point_package(
        paths["point"],
        paths["point_model"],
        Path(args.point_hash_file).resolve(),
        Path(args.point_gate).resolve(),
    )
    component_failures, summary = validate_component_selection_bundle(paths)
    failures.extend(component_failures)
    if summary["round"] != args.round:
        failures.append("component gate round does not match the immutable artifact round")
    artifact_hashes = {
        f"{name.replace('-', '_')}_sha256": sha256(Path(getattr(args, name.replace("-", "_"))).resolve())
        for name in COMPONENT_BUNDLE_PATHS
    }
    result = {
        "gate": "visual-component-selection",
        "round": args.round,
        "passed": not failures,
        **artifact_hashes,
        "selected_candidate": summary["selected_candidate"],
        "selected_ensemble_score": summary["selected_ensemble"]["ensemble_score"],
        "selected_component_ids": summary["selected_ensemble"]["selected_component_ids"],
        "failures": failures,
    }
    write_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 2


def command_slide_gate(args: argparse.Namespace) -> int:
    paths = {name: Path(getattr(args, name.replace("-", "_"))).resolve() for name in (
        "point", "point-model", "point-hash-file", "point-gate", "deck",
        "render-manifest", "deck-inspect", "visual-query", "visual-baseline",
        "brief", "constraints", "component-rubric", "component-catalog",
        "visual-jobs-a", "visual-jobs-b", "component-score-a", "component-score-b",
        "component-ensemble-a", "component-ensemble-b", "candidate-a", "candidate-b",
        "component-selection-audit", "component-gate", "visual-model",
    )}
    hashes = {name.replace("-", "_") + "_sha256": sha256(path) for name, path in paths.items()}
    reviews = {name: read_json(Path(getattr(args, name))) for name in (
        "selection", "semantic", "reader", "executive", "writer", "visual",
    )}
    failures: list[str] = []
    failures.extend(verify_point_package(
        paths["point"], paths["point-model"], paths["point-hash-file"], paths["point-gate"]
    ))
    component_paths = {
        name.replace("-", "_"): paths[name]
        for name in COMPONENT_BUNDLE_PATHS
    }
    component_failures, component_summary = validate_component_selection_bundle(component_paths)
    failures.extend(component_failures)
    component_gate = read_json(paths["component-gate"])
    if component_gate.get("passed") is not True:
        failures.append("visual component selection gate did not pass")
    component_gate_hash_names = {
        f"{name.replace('-', '_')}_sha256": sha256(paths[name])
        for name in COMPONENT_BUNDLE_PATHS
    }
    for name, digest in component_gate_hash_names.items():
        if component_gate.get(name) != digest:
            failures.append(f"visual component selection gate is stale for {name.removesuffix('_sha256')}")
    if component_gate.get("selected_candidate") != component_summary["selected_candidate"]:
        failures.append("visual component selection gate selected candidate is stale")
    if component_gate.get("selected_component_ids") != component_summary["selected_ensemble"]["selected_component_ids"]:
        failures.append("visual component selection gate selected components are stale")
    if component_gate.get("round") != component_summary["round"]:
        failures.append("visual component selection gate round is stale")
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
    valid_claims, valid_node_ids, valid_edge_ids, valid_boundary_ids = point_id_sets(point_model)
    valid_model_ids = valid_node_ids | valid_edge_ids | valid_boundary_ids
    brief = read_yaml(paths["brief"])

    slide_count = pptx_slide_count(paths["deck"])
    if slide_count < 1:
        failures.append("PPTX contains no slides")
    failures.extend(validate_render_manifest(paths["render-manifest"], slide_count))
    render_manifest = read_json(paths["render-manifest"])
    manifest_slides = render_manifest.get("slides")
    expected_render_hashes = [
        item.get("sha256") for item in manifest_slides
        if isinstance(item, dict) and isinstance(item.get("sha256"), str)
    ] if isinstance(manifest_slides, list) else []
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
        "executive_required_ids", "headline_required_ids", "thumbnail_mechanism_required_ids",
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
    mapped_point: set[str] = set()
    mapped_model: set[str] = set()
    mapped_components: set[str] = set()
    artifact_semantics: dict[str, set[str]] = {}
    semantic_records: list[dict] = []
    semantic_kinds = {"node", "connector", "boundary"}
    kind_counts = {kind: 0 for kind in semantic_kinds}
    object_by_id: dict[str, dict] = {}
    for item in objects:
        if not isinstance(item, dict):
            raise SystemExit("visual model object must be an object")
        object_id = item.get("id")
        if not isinstance(object_id, str) or not object_id.strip():
            failures.append("visual model object id is missing")
        elif object_id in object_by_id:
            failures.append(f"visual model duplicates object {object_id}")
        else:
            object_by_id[object_id] = item
        baseline_ids = item.get("baseline_ids", [])
        point_ids = item.get("point_ids", [])
        model_ids = item.get("model_ids", [])
        component_ids = item.get("component_ids", [])
        artifact_ids = item.get("artifact_object_ids", [])
        if any(not isinstance(values, list) for values in (baseline_ids, point_ids, model_ids, component_ids, artifact_ids)):
            raise SystemExit("visual model mappings must be arrays")
        mapped_baseline.update(value for value in baseline_ids if isinstance(value, str))
        mapped_point.update(value for value in point_ids if isinstance(value, str))
        mapped_model.update(value for value in model_ids if isinstance(value, str))
        mapped_components.update(value for value in component_ids if isinstance(value, str))
        kind = item.get("kind")
        if kind in {"decoration", "page-number", "background", "decorative-icon"}:
            if baseline_ids or point_ids or model_ids or component_ids:
                failures.append(f"non-semantic visual object {item.get('id')} cannot claim coverage")
        elif not baseline_ids and not point_ids and not model_ids:
            failures.append(f"meaning-bearing visual object {item.get('id')} has no semantic mapping")
        elif not artifact_ids:
            failures.append(f"meaning-bearing visual object {item.get('id')} has no inspected artifact object")
        if not set(point_ids).issubset(valid_claims):
            failures.append(f"visual object {item.get('id')} references unknown Point IDs")
        if not set(model_ids).issubset(valid_model_ids):
            failures.append(f"visual object {item.get('id')} references unknown model IDs")
        if not set(baseline_ids).issubset(must_ids):
            failures.append(f"visual object {item.get('id')} references unknown baseline IDs")
        for artifact_id in artifact_ids:
            if artifact_id not in inspect_by_id:
                failures.append(f"visual object {artifact_id} is absent from deck inspection")
        if kind in semantic_kinds:
            kind_counts[kind] += 1
            if not artifact_ids:
                failures.append(f"semantic visual object {item.get('id')} has no artifact object")
            for artifact_id in artifact_ids:
                record = inspect_by_id.get(artifact_id)
                if record is not None and record.get("kind") == "textbox" and kind in {"connector", "boundary"}:
                    failures.append(f"{kind} {artifact_id} cannot be a textbox")
                elif record is not None and isinstance(record.get("bbox"), list) and len(record["bbox"]) == 4:
                    semantic_records.append(record)
        for artifact_id in artifact_ids:
            artifact_semantics.setdefault(artifact_id, set()).update(
                value for value in [*point_ids, *model_ids] if isinstance(value, str)
            )
    missing_must = must_ids - mapped_baseline
    if missing_must:
        failures.append("visual model misses baseline IDs: " + ", ".join(sorted(missing_must)))
    chosen_ensemble = component_summary["selected_ensemble"]
    for distinction_id, (left, right) in chosen_ensemble["distinction_sides"].items():
        for artifact_id, semantic_ids in artifact_semantics.items():
            if semantic_ids & left and semantic_ids & right:
                failures.append(
                    f"artifact object {artifact_id} collapses required distinction {distinction_id}"
                )
    if not chosen_ensemble["coverage_point"].issubset(mapped_point):
        failures.append("visual model misses Point IDs selected by the component ensemble")
    if not chosen_ensemble["coverage_model"].issubset(mapped_model):
        failures.append("visual model misses model IDs selected by the component ensemble")
    if not set(chosen_ensemble["selected_component_ids"]).issubset(mapped_components):
        failures.append("visual model misses a selected visual component")
    if not mapped_components.issubset(set(chosen_ensemble["selected_component_ids"])):
        failures.append("visual model references a component outside the selected ensemble")
    if point_structural and kind_counts["connector"] < 2:
        failures.append("structural Point requires at least two real connector objects")
    if point_boundaries and kind_counts["boundary"] < 1:
        failures.append("Point trust boundaries require at least one visible boundary object")

    def trace_objects(trace: dict, trace_label: str, field: str) -> list[dict]:
        values = trace.get(field)
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            failures.append(f"{trace_label} {field} must be a non-empty object ID list")
            return []
        unknown = [value for value in values if value not in object_by_id]
        if unknown:
            failures.append(f"{trace_label} references unknown visual objects: " + ", ".join(unknown))
        return [object_by_id[value] for value in values if value in object_by_id]

    def trace_paths(trace: dict, trace_label: str, connector_ids: set[str], stages: list[tuple[set[str], set[str]]]) -> None:
        rows = trace.get("connector_paths")
        if not isinstance(rows, list) or not rows:
            failures.append(f"{trace_label} connector_paths must be a non-empty array")
            return
        graph: dict[str, set[str]] = {}
        for row in rows:
            if not isinstance(row, dict):
                failures.append(f"{trace_label} connector_paths entries must be objects")
                continue
            connector_id = row.get("connector_object_id")
            source_id = row.get("from_object_id")
            target_id = row.get("to_object_id")
            if not all(isinstance(value, str) and value.strip() for value in (connector_id, source_id, target_id)):
                failures.append(f"{trace_label} connector_paths entries require connector, from, and to object IDs")
                continue
            if connector_id not in connector_ids:
                failures.append(f"{trace_label} connector path references an undeclared connector")
            if source_id not in object_by_id or target_id not in object_by_id:
                failures.append(f"{trace_label} connector path references an unknown endpoint")
                continue
            graph.setdefault(source_id, set()).add(target_id)
        for sources, targets in stages:
            frontier = set(sources)
            reached: set[str] = set()
            while frontier:
                current = frontier.pop()
                if current in reached:
                    continue
                reached.add(current)
                frontier.update(graph.get(current, set()) - reached)
            if targets and not reached.intersection(targets):
                failures.append(f"{trace_label} connector paths do not connect required trace stages")

    def trace_roles_are_distinct(trace_label: str, role_rows: dict, roles: tuple[str, ...]) -> None:
        seen: dict[str, str] = {}
        for role in roles:
            for row in role_rows.get(role, []):
                object_id = row["id"]
                previous = seen.get(object_id)
                if previous and previous != role:
                    failures.append(f"{trace_label} collapses {previous} and {role} into one visual object")
                else:
                    seen[object_id] = role

    trace_rows = visual_model.get("critical_artifact_traces")
    if not isinstance(trace_rows, list) or not trace_rows:
        failures.append("critical artifact trace is missing")
    else:
        trace_ids: set[str] = set()
        for trace in trace_rows:
            if not isinstance(trace, dict):
                failures.append("critical artifact trace must be an object")
                continue
            trace_id = trace.get("id")
            if not isinstance(trace_id, str) or not trace_id.strip():
                failures.append("critical artifact trace id is missing")
            elif trace_id in trace_ids:
                failures.append(f"critical artifact trace duplicates {trace_id}")
            else:
                trace_ids.add(trace_id)
            trace_label = f"critical artifact trace {trace_id or '<unknown>'}"
            trace_roles = {
                role: trace_objects(trace, trace_label, field)
                for role, field in CRITICAL_ARTIFACT_TRACE_ROLES.items()
            }
            direction = trace.get("visible_direction")
            if direction not in TRACE_DIRECTIONS:
                failures.append(f"{trace_label} visible_direction is invalid")
            trace_roles_are_distinct(trace_label, trace_roles, ("producer", "checker", "consumer"))
            connector_ids = {row["id"] for row in trace_roles["connector"]}
            trace_paths(
                trace,
                trace_label,
                connector_ids,
                [
                    ({row["id"] for row in trace_roles["producer"]}, {row["id"] for row in trace_roles["checker"]}),
                    ({row["id"] for row in trace_roles["checker"]}, {row["id"] for row in trace_roles["consumer"]}),
                ],
            )
            if trace_roles["connector"] and any(row.get("kind") != "connector" for row in trace_roles["connector"]):
                failures.append(f"{trace_label} connector_object_ids must map to connector objects")

    security_boundary_required = visual_baseline.get("security_boundary_required")
    if not isinstance(security_boundary_required, bool):
        failures.append("visual baseline security_boundary_required must be boolean")
    elif security_boundary_required:
        expected = visual_baseline.get("security_boundary_model_ids")
        if not isinstance(expected, dict):
            failures.append("visual baseline security_boundary_model_ids is missing")
            expected = {}
        trace = visual_model.get("security_boundary_trace")
        if not isinstance(trace, dict):
            failures.append("security boundary trace is missing")
        else:
            security_roles = {}
            for role, field in SECURITY_BOUNDARY_TRACE_ROLES.items():
                expected_ids = expected.get(role)
                if not isinstance(expected_ids, list) or not expected_ids or any(
                    not isinstance(value, str) or not value.strip() for value in expected_ids
                ):
                    failures.append(f"visual baseline security boundary {role} model IDs are invalid")
                    expected_ids = []
                elif not set(expected_ids).issubset(valid_model_ids):
                    failures.append(f"visual baseline security boundary {role} references unknown model IDs")
                rows = trace_objects(trace, "security boundary trace", field)
                security_roles[role] = rows
                mapped_ids = {
                    model_id
                    for row in rows
                    for model_id in row.get("model_ids", [])
                }
                if expected_ids and not set(expected_ids).issubset(mapped_ids):
                    failures.append(
                        f"security boundary trace {field} does not map every required model ID"
                    )
            direction = trace.get("visible_direction")
            if direction not in TRACE_DIRECTIONS:
                failures.append("security boundary trace visible_direction is invalid")
            trace_roles_are_distinct(
                "security boundary trace", security_roles, ("role", "checker", "decision", "failure"),
            )
            connector_rows = trace_objects(trace, "security boundary trace", "connector_object_ids")
            if connector_rows and any(row.get("kind") != "connector" for row in connector_rows):
                failures.append("security boundary trace connector_object_ids must map to connector objects")
            connector_ids = {row["id"] for row in connector_rows}
            trace_paths(
                trace,
                "security boundary trace",
                connector_ids,
                [
                    ({row["id"] for row in security_roles["role"]}, {row["id"] for row in security_roles["checker"]}),
                    ({row["id"] for row in security_roles["checker"]}, {row["id"] for row in security_roles["decision"]}),
                    ({row["id"] for row in security_roles["decision"]}, {row["id"] for row in security_roles["failure"]}),
                ],
            )

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
    for name in (
        "visual_query", "visual_baseline", "brief", "constraints", "component_rubric",
        "component_catalog", "visual_jobs_a", "visual_jobs_b", "component_score_a",
        "component_score_b", "component_ensemble_a", "component_ensemble_b",
        "candidate_a", "candidate_b", "component_selection_audit", "component_gate",
        "visual_model",
    ):
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
        "project_lens_secondary", "no_new_claims", "visual_component_selection_completed",
        "selection_audit_blind", "ensemble_threshold_met", "component_redundancy_zero",
        "component_hard_failures_zero",
    ):
        if selection_hard.get(name) is not True:
            failures.append(f"selection hard check {name} must be true")
    if selection.get("selected_candidate") not in {"A", "B", "synthesis"}:
        failures.append("selected_candidate must be A, B, or synthesis")
    if selection.get("selected_candidate") != component_summary["selected_candidate"]:
        failures.append("selection disagrees with the component selection audit")
    if selection.get("selected_component_ids") != component_summary["selected_ensemble"]["selected_component_ids"]:
        failures.append("selection selected components disagree with the chosen ensemble")
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
            "component_selection_audit_sha256", "component_gate_sha256",
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
    elif component_gate.get("round") not in rounds:
        failures.append("component artifacts, component gate, and reviews do not share one immutable round")

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
    for name in ("reviewer_provider", "reviewer_role", "reviewer_independence_basis", "author_provider"):
        if not isinstance(visual.get(name), str) or not visual[name].strip():
            failures.append(f"visual {name} is missing")
    review_pass = visual.get("review_pass")
    if not isinstance(review_pass, int) or isinstance(review_pass, bool) or review_pass < 2:
        failures.append("visual review_pass must record a render → fix → verify cycle (at least 2)")
    same_engine = (
        visual.get("reviewer_model") == visual.get("author_model")
        and visual.get("reviewer_provider") == visual.get("author_provider")
    )
    allowed_independence = {"different-provider", "human", "separate-session"}
    if visual.get("reviewer_independence_basis") not in allowed_independence:
        failures.append("visual reviewer_independence_basis is invalid")
    elif same_engine and visual.get("reviewer_independence_basis") != "separate-session":
        failures.append("same-model visual review must declare a separate-session independence basis")
    thumbnail_gist = visual.get("thumbnail_raw_gist")
    if not isinstance(thumbnail_gist, str) or not thumbnail_gist.strip():
        failures.append("visual thumbnail raw gist is missing")
    thumbnail_answers = visual.get("thumbnail_raw_mechanism_answers")
    if not isinstance(thumbnail_answers, dict) or not thumbnail_answers or any(
        not isinstance(value, str) or not value.strip() for value in thumbnail_answers.values()
    ):
        failures.append("visual thumbnail mechanism raw answers are missing")
    thumbnail_ids = visual.get("thumbnail_mechanism_recovered_ids")
    if not isinstance(thumbnail_ids, list) or any(not isinstance(value, str) or not value.strip() for value in thumbnail_ids):
        failures.append("visual thumbnail mechanism recovered IDs are missing")
    elif not required_sets["thumbnail_mechanism_required_ids"].issubset(set(thumbnail_ids)):
        failures.append("visual thumbnail mechanism misses required baseline IDs")
    rendered_hashes = visual.get("rendered_slide_sha256s")
    if rendered_hashes != expected_render_hashes:
        failures.append("visual rendered slide hashes do not match the render manifest")
    bug_hunt = visual.get("bug_hunt_checks")
    if not isinstance(bug_hunt, dict):
        failures.append("visual bug_hunt_checks are missing")
    else:
        missing_bug_hunts = VISUAL_BUG_HUNT_CHECKS - set(bug_hunt)
        if missing_bug_hunts:
            failures.append("visual bug hunt checks are missing: " + ", ".join(sorted(missing_bug_hunts)))
        for name in sorted(VISUAL_BUG_HUNT_CHECKS & set(bug_hunt)):
            if bug_hunt[name] is not True:
                failures.append(f"visual bug hunt {name} must be completed")
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
            "component_selection_audit_sha256", "component_gate_sha256",
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
            "component_selection_audit_sha256", "component_gate_sha256",
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


def validate_package_members(bundle: zipfile.ZipFile, root: Path) -> list[zipfile.ZipInfo]:
    members = bundle.infolist()
    if len(members) > MAX_PACKAGE_MEMBERS:
        raise ValueError(f"package has more than {MAX_PACKAGE_MEMBERS} members")
    total_bytes = 0
    names: set[str] = set()
    approved: list[zipfile.ZipInfo] = []
    for member in members:
        name = member.filename
        member_path = Path(name)
        if member.flag_bits & 0x1:
            raise ValueError(f"package member is encrypted: {name}")
        if stat.S_ISLNK(member.external_attr >> 16):
            raise ValueError(f"package member is a symlink: {name}")
        if member_path.is_absolute() or ".." in member_path.parts:
            raise ValueError(f"archive member escapes extraction root: {name}")
        canonical = member_path.as_posix()
        if not canonical or canonical == "." or canonical in names:
            raise ValueError(f"package has duplicate or invalid member path: {name}")
        names.add(canonical)
        target = (root / member_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"archive member escapes extraction root: {name}") from exc
        if member.is_dir():
            approved.append(member)
            continue
        if member.file_size > MAX_PACKAGE_MEMBER_BYTES:
            raise ValueError(f"package member exceeds byte limit: {name}")
        total_bytes += member.file_size
        if total_bytes > MAX_PACKAGE_TOTAL_BYTES:
            raise ValueError("package exceeds total uncompressed byte limit")
        if member.file_size and (
            not member.compress_size
            or member.file_size > member.compress_size * MAX_PACKAGE_COMPRESSION_RATIO
        ):
            raise ValueError(f"package member exceeds compression ratio limit: {name}")
        approved.append(member)
    return approved


def extract_package_members(bundle: zipfile.ZipFile, members: list[zipfile.ZipInfo], root: Path) -> None:
    for member in members:
        target = root / member.filename
        if member.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with bundle.open(member) as source, target.open("wb") as destination:
            shutil.copyfileobj(source, destination)
        if target.stat().st_size != member.file_size:
            raise OSError(f"extracted size does not match ZIP metadata: {member.filename}")


def command_verify_package(args: argparse.Namespace) -> int:
    archive = Path(args.archive).resolve()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_relative = Path(args.render_manifest)
    deck_relative = Path(args.deck)
    failures: list[str] = []
    archive_hash = None
    if not archive.is_file():
        failures.append(f"package archive is missing: {archive}")
    else:
        archive_hash = sha256(archive)
    if (
        manifest_relative.is_absolute() or deck_relative.is_absolute()
        or ".." in manifest_relative.parts or ".." in deck_relative.parts
    ):
        failures.append("package verification paths must be package-relative")
    if not failures:
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                with zipfile.ZipFile(archive) as bundle:
                    members = validate_package_members(bundle, root)
                    extract_package_members(bundle, members, root)
                manifest = root / manifest_relative
                deck = root / deck_relative
                if not manifest.is_file():
                    failures.append("packaged render manifest is missing")
                if not deck.is_file():
                    failures.append("packaged deck is missing")
                if not failures:
                    failures.extend(validate_render_manifest(manifest, pptx_slide_count(deck)))
        except (OSError, ValueError, SystemExit, zipfile.BadZipFile) as exc:
            failures.append(f"cannot verify package: {exc}")
    result = {
        "gate": "package-render-manifest",
        "archive_sha256": archive_hash,
        "passed": not failures,
        "failures": failures,
    }
    write_json(output, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 2


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

    component = commands.add_parser("component-gate")
    for name in COMPONENT_BUNDLE_PATHS:
        component.add_argument(f"--{name}", required=True)
    component.add_argument("--point-hash-file", required=True)
    component.add_argument("--point-gate", required=True)
    component.add_argument("--round", required=True, type=int)
    component.add_argument("--output", required=True)
    component.set_defaults(func=command_component_gate)

    gate = commands.add_parser("slide-gate")
    for name in (
        "point", "point-model", "point-hash-file", "point-gate", "deck",
        "render-manifest", "deck-inspect", "visual-query", "visual-baseline",
        "brief", "constraints", "component-rubric", "component-catalog",
        "visual-jobs-a", "visual-jobs-b", "component-score-a", "component-score-b",
        "component-ensemble-a", "component-ensemble-b", "candidate-a", "candidate-b",
        "component-selection-audit", "component-gate", "visual-model", "selection", "semantic",
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

    verify_package = commands.add_parser("verify-package")
    verify_package.add_argument("--archive", required=True)
    verify_package.add_argument("--deck", required=True, help="deck path relative to the package root")
    verify_package.add_argument("--render-manifest", required=True, help="manifest path relative to the package root")
    verify_package.add_argument("--output", required=True)
    verify_package.set_defaults(func=command_verify_package)
    return value


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
