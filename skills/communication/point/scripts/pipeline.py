#!/usr/bin/env python3
"""Deterministic run, review-gate, and packaging utilities for Point."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile


SCORE_MAP = {
    "domain": {
        "conceptual_coverage": 20,
        "structural_completeness": 15,
    },
    "reader": {
        "audience_comprehension": 15,
        "mental_model_clarity": 15,
        "one_line_clarity": 10,
    },
    "writer": {
        "logical_coherence": 10,
        "unambiguity": 10,
        "compression_without_loss": 5,
    },
}

SYNTHESIS_WEIGHTS = {
    "domain_baseline_coverage": 40,
    "project_relevance": 30,
    "synthesis_gain": 30,
}

PROSE_WEIGHTS = {
    "reader_fit": 25,
    "terminology_onboarding": 25,
    "causal_cohesion": 25,
    "concision_without_loss": 25,
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


def validate_identity(review: dict, artifact_hash: str, model_hash: str, label: str) -> list[str]:
    failures = []
    if review.get("artifact_sha256") != artifact_hash:
        failures.append(f"{label} review is stale for point.md")
    if review.get("model_sha256") != model_hash:
        failures.append(f"{label} review is stale for point.yaml")
    return failures


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
    for directory in (root / "rounds", root / "final"):
        directory.mkdir(parents=True, exist_ok=True)
    (root / "00-brief.yaml").write_text(
        "run_id: \ncanonical_topic: \nproject_role: teaching_vehicle\n"
        "audience: [novice_developer, technical_executive]\nmode: domain_through_project\n"
        "question: \nscope: \n"
        "source_constraints: primary_or_authoritative\nlanguage: \n"
        "required_readers: [novice_developer, domain_engineer, technical_executive]\n"
        "content_balance: {domain_core: 0.60, project_lens: 0.25, assessment: 0.15}\n"
        "review_mode: independent\n",
        encoding="utf-8",
    )
    (root / "01-domain-query.md").write_text(
        "# Independent domain query\n\nCanonical topic: \nAudiences: novice developer; technical executive\n\n"
        "You know only the domain topic, not the repository or document. For a novice developer "
        "and a technical executive, identify the minimum complete mental model: what problem exists, "
        "what the technology is, actors and end-to-end mechanism, what it proves and does not prove, "
        "decisions enabled, operational value, trust assumptions, common misconceptions, and the five "
        "questions a good explanation must answer. Return candidate coverage, not factual authority.\n",
        encoding="utf-8",
    )
    (root / "01-source-ledger.jsonl").touch()
    print(root)
    return 0


def command_point_gate(args: argparse.Namespace) -> int:
    artifact = Path(args.draft).resolve()
    model = Path(args.model).resolve()
    artifact_hash = sha256(artifact)
    model_hash = sha256(model)
    query_path = Path(args.query).resolve()
    prior_path = Path(args.prior).resolve()
    baseline_path = Path(args.baseline).resolve()
    source_model_path = Path(args.source_model).resolve()
    query_hash = sha256(query_path)
    prior_hash = sha256(prior_path)
    baseline_hash = sha256(baseline_path)
    source_model_hash = sha256(source_model_path)
    prior = read_json(prior_path)
    baseline = read_json(baseline_path)
    source_model = read_json(source_model_path)
    synthesis = read_json(Path(args.synthesis))
    reviews = {
        "fact": read_json(Path(args.fact)),
        "domain": read_json(Path(args.domain)),
        "reader": read_json(Path(args.reader)),
        "writer": read_json(Path(args.writer)),
        "prose": read_json(Path(args.prose)),
    }
    if args.executive:
        reviews["executive"] = read_json(Path(args.executive))

    failures: list[str] = []

    expected_hashes = {
        "domain_query_sha256": query_hash,
        "prior_sha256": prior_hash,
        "baseline_sha256": baseline_hash,
        "source_model_sha256": source_model_hash,
        "artifact_sha256": artifact_hash,
        "model_sha256": model_hash,
    }
    for name, expected in expected_hashes.items():
        if synthesis.get(name) != expected:
            failures.append(f"synthesis {name} is stale")
    if require_list(synthesis, "critical_issues"):
        failures.append("synthesis review has critical issues")

    if prior.get("project_context_seen") is not False:
        failures.append("model prior must be blind to project context")
    if prior.get("is_evidence") is not False:
        failures.append("model prior must not be treated as evidence")
    if prior.get("status") != "coverage_hypothesis":
        failures.append("model prior status must be coverage_hypothesis")
    if prior.get("domain_query_sha256") != query_hash:
        failures.append("model prior is stale for the independent domain query")
    if not isinstance(prior.get("model_identity"), str) or not prior["model_identity"].strip():
        failures.append("model prior must record model_identity")
    if baseline.get("project_context_seen") is not False:
        failures.append("domain baseline must be blind to project context")
    if source_model.get("baseline_context_seen") is not False:
        failures.append("source model must be blind to domain baseline")

    synthesis_hard = synthesis.get("hard_checks")
    if not isinstance(synthesis_hard, dict):
        raise SystemExit("synthesis.hard_checks must be an object")
    for name in (
        "prior_used_as_evidence",
        "prior_project_context_seen",
        "baseline_project_context_seen",
        "source_baseline_context_seen",
    ):
        if synthesis_hard.get(name) is not False:
            failures.append(f"synthesis hard check {name} must be false")
    for name in (
        "authoritative_baseline",
        "domain_first",
        "project_value_statement_present",
        "blind_comparison_completed",
        "final_domain_coverage_not_below_baseline",
        "final_project_fidelity_not_below_source",
    ):
        if synthesis_hard.get(name) is not True:
            failures.append(f"synthesis hard check {name} must be true")
    if synthesis_hard.get("unresolved_critical_domain_gaps") != 0:
        failures.append("unresolved critical domain gaps must be zero")
    baseline_strengths = synthesis.get("baseline_strengths_adopted")
    source_strengths = synthesis.get("source_strengths_adopted")
    if not isinstance(baseline_strengths, list) or not baseline_strengths:
        failures.append("at least one domain-baseline strength must be adopted")
    if not isinstance(source_strengths, list) or len(source_strengths) < 2:
        failures.append("at least two source-model strengths must be adopted")

    balance = synthesis.get("content_balance")
    if not isinstance(balance, dict):
        raise SystemExit("synthesis.content_balance must be an object")
    domain_share = balance.get("domain_core_share")
    assessment_share = balance.get("assessment_share")
    if not isinstance(domain_share, (int, float)) or isinstance(domain_share, bool) or domain_share < 0.5:
        failures.append("domain core share must be at least 0.50")
    if not isinstance(assessment_share, (int, float)) or isinstance(assessment_share, bool) or assessment_share > 0.2:
        failures.append("assessment share must be at most 0.20")

    essentials = baseline.get("critical_essentials")
    if not isinstance(essentials, list) or not essentials:
        raise SystemExit("baseline.critical_essentials must be a non-empty array")
    essential_ids = []
    for item in essentials:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise SystemExit("every baseline critical essential needs an id")
        essential_ids.append(item["id"])
    if len(set(essential_ids)) != len(essential_ids):
        raise SystemExit("baseline critical essential ids must be unique")

    project_insights = source_model.get("project_insights")
    if not isinstance(project_insights, list):
        raise SystemExit("source_model.project_insights must be an array")
    insight_ids = set()
    for item in project_insights:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise SystemExit("every source-model project insight needs an id")
        insight_ids.add(item["id"])

    rows = synthesis.get("coverage_rows")
    if not isinstance(rows, list):
        raise SystemExit("synthesis.coverage_rows must be an array")
    rows_by_id = {}
    selected_insights = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("concept_id"), str):
            raise SystemExit("every synthesis coverage row needs concept_id")
        concept_id = row["concept_id"]
        rows_by_id[concept_id] = row
        if row.get("relationship") not in {"aligned", "missing", "conflict", "source_addition"}:
            failures.append(f"invalid relationship for {concept_id}")
        if row.get("selection") not in {"must", "should", "exclude"}:
            failures.append(f"invalid selection for {concept_id}")
        if row.get("selected_from") not in {"baseline", "source", "both"}:
            failures.append(f"invalid selected_from for {concept_id}")
        if row.get("relationship") == "conflict" and not row.get("resolution"):
            failures.append(f"conflict {concept_id} needs a resolution")
        if concept_id in insight_ids and row.get("selection") in {"must", "should"}:
            selected_insights.add(concept_id)
    for concept_id in essential_ids:
        row = rows_by_id.get(concept_id)
        if not row:
            failures.append(f"baseline essential {concept_id} missing from synthesis")
            continue
        if row.get("selection") != "must":
            failures.append(f"baseline essential {concept_id} must be selected as must")
        final_ids = row.get("final_ids")
        if not isinstance(final_ids, list) or not final_ids:
            failures.append(f"baseline essential {concept_id} needs final_ids")
    if len(selected_insights) < 2:
        failures.append("at least two source-specific insights must be selected")

    synthesis_score, synthesis_score_failures = validate_scores(
        synthesis, SYNTHESIS_WEIGHTS, "synthesis"
    )
    synthesis_score = round(synthesis_score, 2)
    failures.extend(synthesis_score_failures)
    if synthesis_score < 90:
        failures.append("synthesis score below 90")

    for label, review in reviews.items():
        failures.extend(validate_identity(review, artifact_hash, model_hash, label))
        if require_list(review, "critical_issues"):
            failures.append(f"{label} review has critical issues")

    prose = reviews["prose"]
    if not isinstance(prose.get("language"), str) or not prose["language"].strip():
        failures.append("prose review must record language")
    prose_hard = prose.get("hard_checks")
    if not isinstance(prose_hard, dict):
        raise SystemExit("prose.hard_checks must be an object")
    for name in (
        "claim_ids_preserved",
        "citations_and_qualifiers_preserved",
        "critical_terms_defined_or_known",
        "actors_and_actions_explicit",
        "paragraphs_answer_one_reader_question",
        "language_is_natural_for_audience",
    ):
        if prose_hard.get(name) is not True:
            failures.append(f"prose hard check {name} must be true")
    if prose_hard.get("unresolved_literal_translation_count") != 0:
        failures.append("prose review has unresolved literal translations")
    boundary_explanation_required = prose_hard.get("security_boundary_explanation_required")
    if not isinstance(boundary_explanation_required, bool):
        failures.append("prose hard check security_boundary_explanation_required must be boolean")
    elif boundary_explanation_required is True:
        if prose_hard.get("security_boundary_explanation_complete") is not True:
            failures.append("required security-boundary explanation is incomplete")

    fact = reviews["fact"]
    for checked, total, label in (
        (fact.get("claims_checked"), fact.get("claims_total"), "claim coverage"),
        (fact.get("model_elements_checked"), fact.get("model_elements_total"), "model coverage"),
        (fact.get("time_sensitive_checked"), fact.get("time_sensitive_total"), "freshness coverage"),
    ):
        if not isinstance(checked, int) or not isinstance(total, int) or checked != total:
            failures.append(f"{label} is incomplete")
    for name in (
        "critical_unsupported",
        "critical_conflicts",
        "critical_authoritative_source_gaps",
    ):
        if fact.get(name) != 0:
            failures.append(f"{name} must be zero")

    domain = reviews["domain"]
    hard = domain.get("hard_checks")
    if not isinstance(hard, dict):
        raise SystemExit("domain.hard_checks must be an object")
    for name in ("what_how_why_action_complete", "essentials_defined", "exclusions_defined"):
        if hard.get(name) is not True:
            failures.append(f"domain hard check {name} must be true")
    if hard.get("problem_threat_model_flow_proof_limits_policy_complete") is not True:
        failures.append("domain teaching model is incomplete")
    if hard.get("context_dependencies_required") is True and hard.get("context_dependencies_closed") is not True:
        failures.append("domain context dependencies are not causally closed")
    if hard.get("cross_boundary_result_auth_required") is True and hard.get("cross_boundary_results_authenticated") is not True:
        failures.append("decision-bearing cross-boundary results are not authenticated and bound")
    if hard.get("threat_model_required") is True and hard.get("threat_assumptions_explicit") is not True:
        failures.append("security threat and trust assumptions are not explicit")
    if hard.get("trust_semantics_required") is True and hard.get("trust_semantics_not_collapsed") is not True:
        failures.append("components with different trust semantics are collapsed")
    if hard.get("result_identity_required") is True and hard.get("decision_result_identifies_evidence_and_policy") is not True:
        failures.append("decision result does not identify the relevant Evidence and policy")
    if hard.get("structural_topic") is True:
        if not isinstance(hard.get("model_nodes"), int) or hard["model_nodes"] < 2:
            failures.append("structural topic requires at least two model nodes")
        if not isinstance(hard.get("model_edges"), int) or hard["model_edges"] < 1:
            failures.append("structural topic requires at least one model edge")
    if hard.get("trust_boundaries_required") is True:
        if not isinstance(hard.get("model_boundaries"), int) or hard["model_boundaries"] < 1:
            failures.append("trust topic requires an explicit boundary")

    reader = reviews["reader"]
    if reader.get("teach_back_match") is not True:
        failures.append("target reader teach-back does not match")
    for name in (
        "can_explain_problem",
        "can_explain_flow",
        "can_explain_proves_and_limits",
        "can_explain_project_value",
    ):
        if reader.get(name) is not True:
            failures.append(f"reader hard check {name} must be true")
    if require_list(reader, "critical_questions"):
        failures.append("target reader has unanswered critical questions")

    total = 0.0
    for label, weights in SCORE_MAP.items():
        value, score_failures = validate_scores(reviews[label], weights, label)
        total += value
        failures.extend(score_failures)
    total = round(total, 2)
    if total < 90:
        failures.append("Point score below 90")

    prose_score, prose_score_failures = validate_scores(
        prose, PROSE_WEIGHTS, "prose"
    )
    prose_score = round(prose_score, 2)
    failures.extend(prose_score_failures)
    if prose_score < 90:
        failures.append("prose score below 90")

    executive_score = None
    if "executive" in reviews:
        executive_score, score_failures = validate_scores(
            reviews["executive"], {"decision_relevance": 50, "so_what_clarity": 50}, "executive"
        )
        executive_score = round(executive_score, 2)
        failures.extend(score_failures)
        if executive_score < 90:
            failures.append("executive score below 90")
        if require_list(reviews["executive"], "critical_questions"):
            failures.append("executive has unanswered critical questions")
        for name in (
            "can_explain_capability_value",
            "can_explain_trust_limit",
            "can_identify_decision_owner",
            "can_identify_next_action",
        ):
            if reviews["executive"].get(name) is not True:
                failures.append(f"executive hard check {name} must be true")

    result = {
        "gate": "point",
        "round": reviews["fact"].get("round"),
        "passed": not failures,
        "point_score": total,
        "synthesis_score": synthesis_score,
        "prose_score": prose_score,
        "executive_score": executive_score,
        "artifact_sha256": artifact_hash,
        "model_sha256": model_hash,
        "failures": failures,
    }
    write_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 2


def command_freeze(args: argparse.Namespace) -> int:
    markdown = Path(args.markdown).resolve()
    model = Path(args.model).resolve()
    gate = read_json(Path(args.gate))
    if gate.get("passed") is not True:
        raise SystemExit("cannot freeze a failed Point gate")
    if gate.get("artifact_sha256") != sha256(markdown) or gate.get("model_sha256") != sha256(model):
        raise SystemExit("gate hashes do not match the artifacts")
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    out_markdown = output / "point.md"
    out_model = output / "point.yaml"
    shutil.copyfile(markdown, out_markdown)
    shutil.copyfile(model, out_model)
    (output / "point.sha256").write_text(
        f"{sha256(out_markdown)}  point.md\n{sha256(out_model)}  point.yaml\n",
        encoding="utf-8",
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
    init.set_defaults(func=command_init)

    gate = commands.add_parser("point-gate")
    for name in ("draft", "model", "fact", "domain", "reader", "writer", "prose", "output", "query", "prior", "baseline", "synthesis"):
        gate.add_argument(f"--{name}", required=True)
    gate.add_argument("--source-model", dest="source_model", required=True)
    gate.add_argument("--executive")
    gate.set_defaults(func=command_point_gate)

    freeze = commands.add_parser("freeze")
    freeze.add_argument("--markdown", required=True)
    freeze.add_argument("--model", required=True)
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
