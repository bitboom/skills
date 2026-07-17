import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import yaml


SKILL = Path(__file__).resolve().parents[1]
PIPELINE_PATH = SKILL / "scripts" / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("to_deck_pipeline", PIPELINE_PATH)
PIPELINE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(PIPELINE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class IntelRatsFixture:
    def __init__(self, root):
        self.root = Path(root)
        self.paths = {}
        self._make_point_and_baseline()
        self._make_rubric_and_catalog()
        self._make_branch("A")
        self._make_branch("B")
        self._make_audit()
        self._make_point_package()

    def put(self, name, value, suffix="json"):
        path = self.root / f"{name}.{suffix}"
        if suffix == "json":
            save_json(path, value)
        else:
            path.write_text(value, encoding="utf-8")
        self.paths[name.replace("-", "_")] = path
        return path

    def _make_point_and_baseline(self):
        self.put("point", "# Intel TDX Remote Attestation\nEvidence is evaluated before release.\n", "md")
        claims = [{"id": f"C-{index:03d}", "concept": f"concept {index}"} for index in range(1, 10)]
        model = {
            "nodes": [
                {"id": "N-RP"}, {"id": "N-VERIFIER"}, {"id": "N-TD"},
                {"id": "N-QGS"}, {"id": "N-TDQE"}, {"id": "N-PCS"}, {"id": "N-PCCS"},
            ],
            "edges": [
                {"id": "E-REQUEST"}, {"id": "E-EVIDENCE"}, {"id": "E-QGS-TDQE"},
                {"id": "E-QUOTE"}, {"id": "E-RESULT"}, {"id": "E-ACTION"},
                {"id": "E-PCS-PCCS"},
            ],
            "boundaries": [
                {"id": "B-QGS-TDQE"}, {"id": "B-PCS-PCCS"},
                {"id": "B-APPRAISAL"}, {"id": "B-RESULT-USE"},
            ],
        }
        point_model = {
            "canonical_topic": "Intel TDX Remote Attestation",
            "domain_core": claims[:8],
            "project_lens": claims[8:],
            "model": model,
            "source_map": {row["id"]: ["S-001"] for row in claims},
        }
        point_model_path = self.root / "point.yaml"
        point_model_path.write_text(yaml.safe_dump(point_model, sort_keys=False), encoding="utf-8")
        self.paths["point_model"] = point_model_path
        baseline = {
            "must_see": [
                {"id": f"VB-{index:03d}", "point_ids": [f"C-{index:03d}"]}
                for index in range(1, 10)
            ],
            "semantic_required_ids": ["VB-002", "VB-003", "VB-004", "VB-005", "VB-006"],
            "gist_required_ids": ["VB-001", "VB-004", "VB-006"],
            "reconstruction_required_ids": [
                "VB-002", "VB-003", "VB-004", "VB-005", "VB-006", "VB-007", "VB-008"
            ],
            "executive_required_ids": ["VB-001", "VB-004", "VB-007", "VB-009"],
            "headline_required_ids": ["VB-001", "VB-006"],
            "thumbnail_mechanism_required_ids": ["VB-004", "VB-005", "VB-006"],
            "security_boundary_required": True,
            "security_boundary_model_ids": {
                "role": ["N-PCCS"],
                "artifact": ["E-PCS-PCCS"],
                "checker": ["N-VERIFIER"],
                "decision": ["N-RP"],
                "failure": ["E-ACTION"],
            },
        }
        self.put("visual-baseline", baseline)
        self.put("constraints", {
            "slide_size": "16:9",
            "minimum_body_font_pt": 16,
            "minimum_midlevel_font_pt": 24,
            "minimum_title_font_pt": 35,
        })

    def _base_hashes(self):
        return {
            "point_sha256": digest(self.paths["point"]),
            "point_model_sha256": digest(self.paths["point_model"]),
            "visual_baseline_sha256": digest(self.paths["visual_baseline"]),
            "constraints_sha256": digest(self.paths["constraints"]),
            "component_rubric_sha256": digest(self.paths["component_rubric"]),
            "component_catalog_sha256": digest(self.paths["component_catalog"]),
        }

    def _make_rubric_and_catalog(self):
        base = {
            "point_sha256": digest(self.paths["point"]),
            "point_model_sha256": digest(self.paths["point_model"]),
            "visual_baseline_sha256": digest(self.paths["visual_baseline"]),
            "constraints_sha256": digest(self.paths["constraints"]),
        }
        all_criteria = set(PIPELINE.INDIVIDUAL_COMPONENT_WEIGHTS) | set(PIPELINE.ENSEMBLE_WEIGHTS)
        rubric = {
            **base,
            "round": 1,
            "rubric_source_sha256": digest(SKILL / "references" / "component-selection.md"),
            "individual_weights": PIPELINE.INDIVIDUAL_COMPONENT_WEIGHTS,
            "ensemble_weights": PIPELINE.ENSEMBLE_WEIGHTS,
            "thresholds": {
                "dominant_component_minimum": 80,
                "supporting_component_minimum": 70,
                "ensemble_minimum": 90,
                "maximum_non_diagram_support_blocks": 3,
                "final_slide_gate_minimum": 90,
                "final_criterion_minimum": 4,
            },
            "hard_failure_codes": sorted(PIPELINE.REQUIRED_COMPONENT_HARD_FAILURES),
            "anchors": {
                name: {str(score): f"{name} anchored level {score}" for score in range(1, 6)}
                for name in sorted(all_criteria)
            },
        }
        self.put("component-rubric", rubric)
        rubric_hash = digest(self.paths["component_rubric"])
        seed_hashes = {
            **base,
            "component_rubric_sha256": rubric_hash,
            "component_catalog_sha256": "not-used-by-seed",
        }
        catalog = {
            **base,
            "round": 1,
            "component_rubric_sha256": rubric_hash,
            "catalog_source_sha256": digest(SKILL / "references" / "component-catalog.md"),
            "open_catalog": True,
            "candidate_seed_sha256": {
                branch: PIPELINE.component_candidate_seed(branch, seed_hashes)
                for branch in ("A", "B")
            },
            "dominant_families": [
                {"id": family, "role": "dominant", "meaning_bearing": True,
                 "visual_jobs": ["mechanism", "causal-path"]}
                for family in sorted(PIPELINE.DEFAULT_DOMINANT_FAMILIES)
            ],
            "supporting_families": [
                {"id": family, "role": "supporting", "meaning_bearing": True,
                 "visual_jobs": ["definition", "limitation", "action"]}
                for family in sorted(PIPELINE.DEFAULT_SUPPORTING_FAMILIES)
            ],
            "non_semantic_exclusions": sorted(PIPELINE.NON_SEMANTIC_FAMILIES),
        }
        self.put("component-catalog", catalog)

    def _jobs(self, branch):
        distinctions = [
            {"id": "D-QGS-TDQE", "left_ids": ["N-QGS"], "right_ids": ["N-TDQE"],
             "baseline_ids": ["VB-003"], "critical": True},
            {"id": "D-PCS-PCCS", "left_ids": ["N-PCS"], "right_ids": ["N-PCCS"],
             "baseline_ids": ["VB-005"], "critical": True},
            {"id": "D-OWNERS", "left_ids": ["N-VERIFIER"], "right_ids": ["N-RP"],
             "baseline_ids": ["VB-004"], "critical": True},
            {"id": "D-EVIDENCE-RESULT", "left_ids": ["E-QUOTE"], "right_ids": ["E-RESULT"],
             "baseline_ids": ["VB-004"], "critical": True},
            {"id": "D-RESULT-ACTION", "left_ids": ["E-RESULT"], "right_ids": ["E-ACTION"],
             "baseline_ids": ["VB-004", "VB-006"], "critical": True},
            {"id": "D-PROOF-NONPROOF", "left_ids": ["C-007"], "right_ids": ["C-008"],
             "baseline_ids": ["VB-007", "VB-008"], "critical": True},
            {"id": "D-OUTCOMES", "left_ids": ["C-006"], "right_ids": ["C-009"],
             "baseline_ids": ["VB-006", "VB-009"], "critical": True},
        ]
        rows = [
            (1, "definition", ["N-RP"], []),
            (2, "mechanism", ["N-TD", "E-REQUEST", "E-EVIDENCE"], []),
            (3, "trust-boundary", ["N-QGS", "N-TDQE", "E-QGS-TDQE", "B-QGS-TDQE"], ["D-QGS-TDQE"]),
            (4, "artifact-movement", ["N-VERIFIER", "N-RP", "E-QUOTE", "E-RESULT"],
             ["D-OWNERS", "D-EVIDENCE-RESULT"]),
            (5, "trust-boundary", ["N-PCS", "N-PCCS", "B-PCS-PCCS", "E-PCS-PCCS"], ["D-PCS-PCCS"]),
            (6, "decision-or-branching", ["E-ACTION", "B-APPRAISAL"], ["D-RESULT-ACTION", "D-OUTCOMES"]),
            (7, "proof", ["N-VERIFIER"], ["D-PROOF-NONPROOF"]),
            (8, "non-proof", ["B-RESULT-USE"], ["D-PROOF-NONPROOF"]),
            (9, "action", ["N-RP"], ["D-OUTCOMES"]),
        ]
        jobs = []
        for index, job_type, model_ids, distinction_ids in rows:
            jobs.append({
                "id": f"VJ-{branch}-{index:03d}",
                "visual_job": job_type,
                "claim_ids": [f"C-{index:03d}"],
                "model_ids": model_ids,
                "baseline_ids": [f"VB-{index:03d}"],
                "criticality": "supporting" if index == 9 else "critical",
                "intended_audiences": ["novice_developer", "technical_executive"],
                "expected_cold_read_answer": f"recover meaning {index}",
                "distinction_ids": distinction_ids,
            })
        return {
            **self._base_hashes(),
            "round": 1,
            "candidate_seed_sha256": self.catalog()["candidate_seed_sha256"][branch],
            "branch": branch,
            "visual_jobs": jobs,
            "critical_relationship_ids": [
                "E-REQUEST", "E-EVIDENCE", "E-QGS-TDQE", "E-QUOTE",
                "E-RESULT", "E-ACTION", "E-PCS-PCCS",
            ],
            "critical_boundary_ids": ["B-QGS-TDQE", "B-PCS-PCCS", "B-APPRAISAL", "B-RESULT-USE"],
            "distinctions": distinctions,
            "required_distinction_ids": [row["id"] for row in distinctions],
            "applicable_dominant_families": (
                ["causal-pipeline", "evidence-and-verification-chain"]
                if branch == "A" else
                ["trust-boundary-and-data-flow-diagram", "sequence-or-handshake-diagram"]
            ),
            "required_causal_path": [
                {"stage": "evidence", "claim_ids": ["C-002"],
                 "model_ids": ["E-EVIDENCE"], "baseline_ids": ["VB-002"]},
                {"stage": "evaluation", "claim_ids": ["C-004"],
                 "model_ids": ["N-VERIFIER"], "baseline_ids": ["VB-004"]},
                {"stage": "authenticated_result", "claim_ids": ["C-004"],
                 "model_ids": ["E-RESULT"], "baseline_ids": ["VB-004"]},
                {"stage": "policy_action", "claim_ids": ["C-006"],
                 "model_ids": ["E-ACTION"], "baseline_ids": ["VB-006"]},
            ],
        }

    def _criteria(self, weights, score):
        return {
            name: {"score": score, "justification": f"evidence for {name} at {score}"}
            for name in weights
        }

    def _component(self, component_id, role, family, jobs, baselines, points, models, distinctions, score):
        threshold = 80 if role == "dominant" else 70
        normalized = round(sum(score / 5 * weight for weight in PIPELINE.INDIVIDUAL_COMPONENT_WEIGHTS.values()), 2)
        return {
            "component_id": component_id,
            "role": role,
            "family": family,
            "visual_job_ids": jobs,
            "criteria": self._criteria(PIPELINE.INDIVIDUAL_COMPONENT_WEIGHTS, score),
            "normalized_score": normalized,
            "covered_baseline_ids": baselines,
            "covered_point_ids": points,
            "covered_model_ids": models,
            "uncovered_ids": {"baseline_ids": [], "point_ids": [], "model_ids": []},
            "preserved_distinction_ids": distinctions,
            "risks": ["density must be checked after rendering"],
            "hard_failures": [],
            "assumptions": ["editable native shapes are available"],
            "eligible": normalized >= threshold,
        }

    def _make_branch(self, branch):
        jobs = self._jobs(branch)
        jobs_path = self.put(f"visual-jobs-{branch.lower()}", jobs)
        if branch == "A":
            dominant_family, alternate_family = "causal-pipeline", "evidence-and-verification-chain"
            signature = {
                "dominant_family": dominant_family,
                "composition_pattern": "left-to-right pipeline with collateral rail",
                "primary_encoding": "directed artifact flow",
                "path_topology": "linear path with terminal branch",
            }
        else:
            dominant_family, alternate_family = "trust-boundary-and-data-flow-diagram", "sequence-or-handshake-diagram"
            signature = {
                "dominant_family": dominant_family,
                "composition_pattern": "nested trust zones with decision spine",
                "primary_encoding": "boundary-contained actors and messages",
                "path_topology": "dual lane convergence",
            }
        prefix = branch
        dominant_jobs = [f"VJ-{branch}-{index:03d}" for index in range(1, 7)]
        critical_models = [
            "N-RP", "N-VERIFIER", "N-TD", "N-QGS", "N-TDQE", "N-PCS", "N-PCCS",
            "E-REQUEST", "E-EVIDENCE", "E-QGS-TDQE", "E-QUOTE", "E-RESULT", "E-ACTION", "E-PCS-PCCS",
            "B-QGS-TDQE", "B-PCS-PCCS", "B-APPRAISAL", "B-RESULT-USE",
        ]
        components = [
            self._component(
                f"{prefix}-DOM", "dominant", dominant_family, dominant_jobs,
                [f"VB-{index:03d}" for index in range(1, 7)],
                [f"C-{index:03d}" for index in range(1, 7)], critical_models,
                ["D-QGS-TDQE", "D-PCS-PCCS", "D-OWNERS", "D-EVIDENCE-RESULT", "D-RESULT-ACTION"], 5,
            ),
            self._component(
                f"{prefix}-ALT", "dominant", alternate_family, dominant_jobs,
                [f"VB-{index:03d}" for index in range(1, 7)],
                [f"C-{index:03d}" for index in range(1, 7)], critical_models,
                ["D-QGS-TDQE", "D-PCS-PCCS", "D-OWNERS", "D-EVIDENCE-RESULT", "D-RESULT-ACTION"], 3,
            ),
            self._component(
                f"{prefix}-PROOF", "supporting", "proof-and-non-proof", [f"VJ-{branch}-007"],
                ["VB-007"], ["C-007"], ["N-VERIFIER"], ["D-PROOF-NONPROOF"], 5,
            ),
            self._component(
                f"{prefix}-LIMIT", "supporting", "limitations-and-risks", [f"VJ-{branch}-008"],
                ["VB-008"], ["C-008"], ["B-RESULT-USE"], ["D-PROOF-NONPROOF"], 5,
            ),
            self._component(
                f"{prefix}-ACTION", "supporting", "decision-and-next-action", [f"VJ-{branch}-009"],
                ["VB-009"], ["C-009"], ["N-RP"], ["D-OUTCOMES"], 5,
            ),
        ]
        scores = {
            **self._base_hashes(),
            "round": 1,
            "candidate_seed_sha256": self.catalog()["candidate_seed_sha256"][branch],
            "visual_jobs_sha256": digest(jobs_path),
            "branch": branch,
            "other_candidate_seen": False,
            "other_scores_seen": False,
            "other_visual_grammar_seen": False,
            "considered_dominant_families": jobs["applicable_dominant_families"],
            "components": components,
        }
        score_path = self.put(f"component-score-{branch.lower()}", scores)
        selected_ids = [f"{prefix}-DOM", f"{prefix}-PROOF", f"{prefix}-LIMIT", f"{prefix}-ACTION"]
        coverage = {
            "baseline_ids": [f"VB-{index:03d}" for index in range(1, 10)],
            "point_ids": [f"C-{index:03d}" for index in range(1, 10)],
            "model_ids": critical_models,
        }
        ensemble = {
            **self._base_hashes(),
            "round": 1,
            "candidate_seed_sha256": self.catalog()["candidate_seed_sha256"][branch],
            "visual_jobs_sha256": digest(jobs_path),
            "component_score_sha256": digest(score_path),
            "branch": branch,
            "other_candidate_seen": False,
            "other_scores_seen": False,
            "other_visual_grammar_seen": False,
            "dominant_component_id": f"{prefix}-DOM",
            "supporting_component_ids": [f"{prefix}-PROOF", f"{prefix}-LIMIT", f"{prefix}-ACTION"],
            "selected_component_ids": selected_ids,
            "support_contributions": [
                {"component_id": f"{prefix}-PROOF", "incremental_baseline_ids": ["VB-007"],
                 "incremental_value": "critical_coverage", "justification": "adds proof boundary"},
                {"component_id": f"{prefix}-LIMIT", "incremental_baseline_ids": ["VB-008"],
                 "incremental_value": "critical_coverage", "justification": "adds non-proof boundary"},
                {"component_id": f"{prefix}-ACTION", "incremental_baseline_ids": ["VB-009"],
                 "incremental_value": "meaningful_new_baseline", "justification": "adds owner and action"},
            ],
            "coverage": coverage,
            "preserved_distinction_ids": [
                "D-QGS-TDQE", "D-PCS-PCCS", "D-OWNERS", "D-EVIDENCE-RESULT", "D-RESULT-ACTION",
                "D-PROOF-NONPROOF", "D-OUTCOMES",
            ],
            "criteria": self._criteria(PIPELINE.ENSEMBLE_WEIGHTS, 5),
            "redundancy_penalty": 0,
            "ensemble_score": 100.0,
            "hard_failures": [],
            "unnecessary_component_ids": [],
            "dominant_visual_argument": "Evidence is evaluated before a separate release decision.",
            "custom_fallback_reason": "not required",
        }
        ensemble_path = self.put(f"component-ensemble-{branch.lower()}", ensemble)
        component_for_baseline = {
            **{f"VB-{index:03d}": f"{prefix}-DOM" for index in range(1, 7)},
            "VB-007": f"{prefix}-PROOF",
            "VB-008": f"{prefix}-LIMIT",
            "VB-009": f"{prefix}-ACTION",
        }
        object_map = []
        object_index = 0
        for job in jobs["visual_jobs"]:
            for model_id in job["model_ids"]:
                object_index += 1
                baseline_id = job["baseline_ids"][0]
                object_map.append({
                    "planned_object_id": f"{branch}-OBJ-{object_index:03d}",
                    "baseline_ids": [baseline_id],
                    "point_ids": job["claim_ids"],
                    "model_ids": [model_id],
                    "component_id": component_for_baseline[baseline_id],
                })
        candidate = {
            **self._base_hashes(),
            "round": 1,
            "candidate_seed_sha256": self.catalog()["candidate_seed_sha256"][branch],
            "visual_jobs_sha256": digest(jobs_path),
            "component_score_sha256": digest(score_path),
            "component_ensemble_sha256": digest(ensemble_path),
            "candidate_id": branch,
            "visual_grammar": signature["composition_pattern"],
            "narrative_job": "show Evidence-to-action closure",
            "headline": "Quote verification is not secret release",
            "dominant_component_id": f"{prefix}-DOM",
            "selected_component_ids": selected_ids,
            "visual_grammar_signature": signature,
            "object_map": object_map,
            "reading_order": ["headline", "dominant mechanism", "proof limits", "action"],
            "support_blocks": ["proof", "limitations", "next action"],
            "omissions": ["byte-level protocol profile"],
            "density_risks": ["actor labels require render QA"],
            "accessibility_risks": ["reading order must be checked"],
        }
        self.put(f"candidate-{branch.lower()}", candidate)

    def _make_audit(self):
        base = self._base_hashes()
        recomputed = {}
        for branch in ("A", "B"):
            scores = self.load(f"component_score_{branch.lower()}")
            ensemble = self.load(f"component_ensemble_{branch.lower()}")
            recomputed[branch] = {
                "components": {row["component_id"]: row["normalized_score"] for row in scores["components"]},
                "ensemble": ensemble["ensemble_score"],
            }
        audit = {
            **base,
            "round": 1,
            "visual_jobs_a_sha256": digest(self.paths["visual_jobs_a"]),
            "visual_jobs_b_sha256": digest(self.paths["visual_jobs_b"]),
            "component_score_a_sha256": digest(self.paths["component_score_a"]),
            "component_score_b_sha256": digest(self.paths["component_score_b"]),
            "component_ensemble_a_sha256": digest(self.paths["component_ensemble_a"]),
            "component_ensemble_b_sha256": digest(self.paths["component_ensemble_b"]),
            "candidate_a_sha256": digest(self.paths["candidate_a"]),
            "candidate_b_sha256": digest(self.paths["candidate_b"]),
            "candidate_names_hidden": True,
            "author_information_hidden": True,
            "author_aggregate_scores_hidden": True,
            "score_evidence_verified": True,
            "semantic_fidelity_rechecked": True,
            "redundancy_rechecked": True,
            "hard_failures": [],
            "critical_issues": [],
            "recomputed_scores": recomputed,
            "verified_baseline_ids": [f"VB-{index:03d}" for index in range(1, 10)],
            "selected_candidate": "A",
            "selection_reason": "A provides the clearest causal closure with minimum support.",
        }
        self.put("component-selection-audit", audit)

    def _make_point_package(self):
        hash_file = self.root / "point.sha256"
        hash_file.write_text(
            f"{digest(self.paths['point'])}  point.md\n{digest(self.paths['point_model'])}  point.yaml\n",
            encoding="utf-8",
        )
        self.paths["point_hash_file"] = hash_file
        point_gate = {
            "passed": True,
            "artifact_sha256": digest(self.paths["point"]),
            "model_sha256": digest(self.paths["point_model"]),
        }
        self.put("point-gate", point_gate)

    def catalog(self):
        return self.load("component_catalog")

    def load(self, key):
        return json.loads(self.paths[key].read_text(encoding="utf-8"))

    def save(self, key, value):
        save_json(self.paths[key], value)

    def component_args(self):
        args = []
        for name in PIPELINE.COMPONENT_BUNDLE_PATHS:
            args += [f"--{name}", str(self.paths[name.replace("-", "_")])]
        args += [
            "--point-hash-file", str(self.paths["point_hash_file"]),
            "--point-gate", str(self.paths["point_gate"]),
            "--round", "1",
            "--output", str(self.root / "component-gate.json"),
        ]
        self.paths["component_gate"] = self.root / "component-gate.json"
        return args

    def run_component_gate(self):
        return subprocess.run(
            [sys.executable, str(PIPELINE_PATH), "component-gate", *self.component_args()],
            check=False, capture_output=True, text=True,
        )

    def context(self, branch="A"):
        point_model = yaml.safe_load(self.paths["point_model"].read_text(encoding="utf-8"))
        claims, nodes, edges, boundaries = PIPELINE.point_id_sets(point_model)
        baseline = self.load("visual_baseline")
        must_ids = {row["id"] for row in baseline["must_see"]}
        required_sets = {name: set(baseline[name]) for name in PIPELINE.REQUIRED_BASELINE_SETS}
        required_sets["complete_must_see_coverage"] = must_ids
        _, families = PIPELINE.validate_component_catalog(self.catalog())
        jobs_value = self.load(f"visual_jobs_{branch.lower()}")
        _, jobs = PIPELINE.validate_visual_jobs(
            jobs_value, "jobs", claims, nodes, edges, boundaries, must_ids, required_sets, families,
        )
        scores_value = self.load(f"component_score_{branch.lower()}")
        _, components = PIPELINE.validate_component_scores(
            scores_value, "scores", jobs, families, claims, nodes | edges | boundaries,
            must_ids, True,
        )
        return required_sets, jobs, components

    def make_slide_gate_fixture(self):
        component_result = self.run_component_gate()
        if component_result.returncode != 0:
            raise AssertionError(component_result.stdout + component_result.stderr)
        self.put("visual-query", "Define the minimum visual understanding.\n", "md")
        brief_path = self.root / "brief.yaml"
        brief_path.write_text(
            "slide_count: 1\nprior_deck: null\nuser_rejected_dimensions: []\n",
            encoding="utf-8",
        )
        self.paths["brief"] = brief_path
        deck = self.root / "deck.pptx"
        with zipfile.ZipFile(deck, "w") as archive:
            archive.writestr("ppt/slides/slide1.xml", "<slide/>")
        self.paths["deck"] = deck
        render_dir = self.root / "render"
        render_dir.mkdir()
        render = render_dir / "slide-1.png"
        render.write_bytes(
            b"\x89PNG\r\n\x1a\n" + b"\0" * 8 + (1600).to_bytes(4, "big") + (900).to_bytes(4, "big")
        )
        self.paths["render"] = render
        self.put("render-manifest", {
            "schema_version": 2,
            "renderer": "test renderer",
            "renderer_version": "1",
            "command": "test",
            "generated_at": "2026-07-17T00:00:00Z",
            "toolchain": {
                "renderer": "test renderer",
                "renderer_version": "1",
                "command": "test",
                "environment": "test environment",
            },
            "producer": {"kind": "manual", "command": "test"},
            "slide_count": 1,
            "slides": [{"path": "render/slide-1.png", "width": 1600, "height": 900,
                        "sha256": digest(render)}],
        })
        ensemble = self.load("component_ensemble_a")
        score_rows = self.load("component_score_a")["components"]
        component_for_point = {
            point_id: row["component_id"]
            for row in score_rows for point_id in row["covered_point_ids"]
            if row["component_id"] in ensemble["selected_component_ids"]
        }
        component_for_model = {
            model_id: row["component_id"]
            for row in score_rows for model_id in row["covered_model_ids"]
            if row["component_id"] in ensemble["selected_component_ids"]
        }
        visual_objects = [
            {"id": "node-main", "kind": "node", "component_ids": ["A-DOM"],
             "baseline_ids": ["VB-001"], "point_ids": ["C-001"],
             "model_ids": ["N-TD"], "artifact_object_ids": ["sh/node"]},
            {"id": "edge-one", "kind": "connector", "component_ids": ["A-DOM"],
             "baseline_ids": ["VB-002"], "point_ids": ["C-002"],
             "model_ids": ["E-EVIDENCE"], "artifact_object_ids": ["sh/edge-1"]},
            {"id": "edge-two", "kind": "connector", "component_ids": ["A-DOM"],
             "baseline_ids": ["VB-004"], "point_ids": ["C-004"],
             "model_ids": ["E-RESULT"], "artifact_object_ids": ["sh/edge-2"]},
            {"id": "edge-three", "kind": "connector", "component_ids": ["A-ACTION"],
             "baseline_ids": ["VB-009"], "point_ids": ["C-009"],
             "model_ids": ["E-ACTION"], "artifact_object_ids": ["sh/edge-3"]},
            {"id": "boundary-main", "kind": "boundary", "component_ids": ["A-DOM"],
             "baseline_ids": ["VB-003"], "point_ids": ["C-003"],
             "model_ids": ["B-QGS-TDQE"], "artifact_object_ids": ["sh/boundary"]},
        ]
        records = [
            {"kind": "slide", "slide": 1},
            {"kind": "shape", "id": "sh/node", "slide": 1, "bbox": [50, 130, 500, 400]},
            {"kind": "shape", "id": "sh/edge-1", "slide": 1, "bbox": [550, 250, 200, 10]},
            {"kind": "shape", "id": "sh/edge-2", "slide": 1, "bbox": [750, 250, 200, 10]},
            {"kind": "shape", "id": "sh/edge-3", "slide": 1, "bbox": [950, 250, 150, 10]},
            {"kind": "shape", "id": "sh/boundary", "slide": 1, "bbox": [40, 120, 1100, 500]},
        ]
        mapped_points = {item for row in visual_objects for item in row["point_ids"]}
        mapped_models = {item for row in visual_objects for item in row["model_ids"]}
        for index, point_id in enumerate(sorted(set(ensemble["coverage"]["point_ids"]) - mapped_points), 1):
            suffix = point_id.split("-")[-1]
            artifact_id = f"sh/point-{index}"
            visual_objects.append({
                "id": f"point-{index}", "kind": "semantic-label",
                "component_ids": [component_for_point[point_id]],
                "baseline_ids": [f"VB-{suffix}"], "point_ids": [point_id],
                "model_ids": [], "artifact_object_ids": [artifact_id],
            })
            records.append({"kind": "shape", "id": artifact_id, "slide": 1,
                            "bbox": [80 + index * 20, 500, 16, 16]})
        for index, model_id in enumerate(sorted(set(ensemble["coverage"]["model_ids"]) - mapped_models), 1):
            artifact_id = f"sh/model-{index}"
            visual_objects.append({
                "id": f"model-{index}", "kind": "semantic-label",
                "component_ids": [component_for_model[model_id]],
                "baseline_ids": [], "point_ids": [], "model_ids": [model_id],
                "artifact_object_ids": [artifact_id],
            })
            records.append({"kind": "shape", "id": artifact_id, "slide": 1,
                            "bbox": [80 + index * 20, 520, 16, 16]})
        inspect = self.root / "deck.inspect.ndjson"
        inspect.write_text("\n".join(json.dumps(row) for row in records) + "\n", encoding="utf-8")
        self.paths["deck_inspect"] = inspect
        model_object_ids = {
            model_id: row["id"]
            for row in visual_objects
            for model_id in row["model_ids"]
        }
        visual_model = {
            "objects": visual_objects,
            "critical_artifact_traces": [{
                "id": "TRACE-EVIDENCE-RESULT",
                "producer_object_ids": ["node-main"],
                "checker_object_ids": [model_object_ids["N-VERIFIER"]],
                "consumer_object_ids": [model_object_ids["N-RP"]],
                "connector_object_ids": ["edge-one", "edge-two"],
                "connector_paths": [
                    {"connector_object_id": "edge-one", "from_object_id": "node-main", "to_object_id": model_object_ids["N-VERIFIER"]},
                    {"connector_object_id": "edge-two", "from_object_id": model_object_ids["N-VERIFIER"], "to_object_id": model_object_ids["N-RP"]},
                ],
                "visible_direction": "left-to-right",
            }],
            "security_boundary_trace": {
                "role_object_ids": [model_object_ids["N-PCCS"]],
                "artifact_object_ids": [model_object_ids["E-PCS-PCCS"]],
                "checker_object_ids": [model_object_ids["N-VERIFIER"]],
                "decision_object_ids": [model_object_ids["N-RP"]],
                "failure_object_ids": [model_object_ids["E-ACTION"]],
                "connector_object_ids": ["edge-one", "edge-two", "edge-three"],
                "connector_paths": [
                    {"connector_object_id": "edge-one", "from_object_id": model_object_ids["N-PCCS"], "to_object_id": model_object_ids["N-VERIFIER"]},
                    {"connector_object_id": "edge-two", "from_object_id": model_object_ids["N-VERIFIER"], "to_object_id": model_object_ids["N-RP"]},
                    {"connector_object_id": "edge-three", "from_object_id": model_object_ids["N-RP"], "to_object_id": model_object_ids["E-ACTION"]},
                ],
                "visible_direction": "left-to-right",
            },
        }
        self.put("visual-model", visual_model)
        self._make_selection_and_reviews()

    def _make_selection_and_reviews(self):
        def path_hash(key):
            return digest(self.paths[key])

        selection = {
            "round": 1,
            "point_sha256": path_hash("point"),
            "visual_query_sha256": path_hash("visual_query"),
            "visual_baseline_sha256": path_hash("visual_baseline"),
            "brief_sha256": path_hash("brief"),
            "constraints_sha256": path_hash("constraints"),
            "component_rubric_sha256": path_hash("component_rubric"),
            "component_catalog_sha256": path_hash("component_catalog"),
            "visual_jobs_a_sha256": path_hash("visual_jobs_a"),
            "visual_jobs_b_sha256": path_hash("visual_jobs_b"),
            "component_score_a_sha256": path_hash("component_score_a"),
            "component_score_b_sha256": path_hash("component_score_b"),
            "component_ensemble_a_sha256": path_hash("component_ensemble_a"),
            "component_ensemble_b_sha256": path_hash("component_ensemble_b"),
            "candidate_a_sha256": path_hash("candidate_a"),
            "candidate_b_sha256": path_hash("candidate_b"),
            "component_selection_audit_sha256": path_hash("component_selection_audit"),
            "component_gate_sha256": path_hash("component_gate"),
            "visual_model_sha256": path_hash("visual_model"),
            "selected_candidate": "A",
            "selected_component_ids": ["A-DOM", "A-PROOF", "A-LIMIT", "A-ACTION"],
            "must_see_total": 9,
            "must_see_mapped": 9,
            "coverage_rows": [{"id": f"VB-{index:03d}", "status": "mapped"} for index in range(1, 10)],
            "candidate_a_strengths": ["closed causal path"],
            "candidate_b_strengths": ["strong boundary view"],
            "hard_checks": {
                "candidate_a_blind": True,
                "candidate_b_blind": True,
                "candidate_visual_grammars_distinct": True,
                "prior_deck_hidden": True,
                "selection_reasoned": True,
                "dominant_diagram_selected": True,
                "project_lens_secondary": True,
                "no_new_claims": True,
                "visual_component_selection_completed": True,
                "selection_audit_blind": True,
                "ensemble_threshold_met": True,
                "component_redundancy_zero": True,
                "component_hard_failures_zero": True,
            },
            "scores": {"visual_baseline_coverage": 5, "candidate_comparison_quality": 5},
            "critical_issues": [],
        }
        self.put("selection", selection)
        common = {
            "round": 1,
            "point_sha256": path_hash("point"),
            "point_model_sha256": path_hash("point_model"),
            "brief_sha256": path_hash("brief"),
            "deck_sha256": path_hash("deck"),
            "render_manifest_sha256": path_hash("render_manifest"),
            "deck_inspect_sha256": path_hash("deck_inspect"),
            "visual_model_sha256": path_hash("visual_model"),
            "component_selection_audit_sha256": path_hash("component_selection_audit"),
            "component_gate_sha256": path_hash("component_gate"),
            "author_id": "author",
            "author_model": "author-model",
            "author_provider": "author-provider",
            "review_prompt_sha256": "b" * 64,
            "critical_issues": [],
            "issues": [],
        }
        semantic = {
            **common, "reviewer_id": "semantic", "reviewer_model": "model",
            "structural_elements": 7, "relationships": 7, "diagram_required": True,
            "dominant_visual_present": True, "semantic_visual_share": 0.76,
            "nodes_total": 1, "nodes_checked": 1, "edges_total": 3, "edges_checked": 3,
            "boundaries_total": 1, "boundaries_checked": 1, "diagram_direction_errors": 0,
            "visual_grammar_matches_job": True, "trust_roles_not_collapsed": True,
            "project_assessment_secondary": True,
            "verified_semantic_ids": [f"VB-{index:03d}" for index in range(1, 10)],
            "scores": {"point_coverage": 5, "causal_structure_visibility": 5, "diagram_accuracy": 5},
        }
        reader = {
            **common, "reviewer_id": "reader", "reviewer_model": "model",
            "allowed_inputs": ["rendered_slides"], "point_context_seen": False,
            "storyboard_context_seen": False, "prior_scores_seen": False,
            "gist_exposure_seconds": 8, "reconstruction_exposure_seconds": 25,
            "raw_gist_answers": {"answer": "evidence before action"},
            "raw_reconstruction_answers": {"answer": "request to Evidence to Result to action"},
            "gist_recovered_ids": ["VB-001", "VB-004", "VB-006"],
            "reconstruction_recovered_ids": [
                "VB-002", "VB-003", "VB-004", "VB-005", "VB-006", "VB-007", "VB-008"
            ],
            "teach_back_match": True, "critical_questions": [],
            "scores": {"novice_comprehension": 5},
        }
        executive = {
            **common, "reviewer_id": "executive", "reviewer_model": "model",
            "allowed_inputs": ["rendered_slides"], "point_context_seen": False,
            "storyboard_context_seen": False, "prior_scores_seen": False,
            "raw_answers": {"answer": "capability, limit, owner, action"},
            "executive_recovered_ids": ["VB-001", "VB-004", "VB-007", "VB-009"],
            "critical_questions": [], "scores": {"executive_takeaway": 5},
        }
        writer = {
            **common, "reviewer_id": "writer", "reviewer_model": "model",
            "headline_domain_first": True, "headline_is_assertion": True,
            "meta_evaluation_language_absent": True, "labels_plain_language": True,
            "compression_preserves_model": True, "headline_recovered_ids": ["VB-001", "VB-006"],
            "unexplained_critical_terms": 0, "scores": {"headline_clarity": 5},
        }
        visual = {
            **common, "reviewer_id": "visual", "reviewer_model": "model",
            "reviewer_provider": "independent-provider", "reviewer_role": "model",
            "reviewer_independence_basis": "different-provider", "review_pass": 2,
            "full_size_render_inspected": True, "thumbnail_render_inspected": True,
            "structural_test_passed": True, "slide_count_match": True,
            "thumbnail_raw_gist": "evidence is evaluated before a release decision",
            "thumbnail_raw_mechanism_answers": {"answer": "Verifier evaluates evidence before RP acts"},
            "thumbnail_mechanism_recovered_ids": ["VB-004", "VB-005", "VB-006"],
            "rendered_slide_sha256s": [digest(self.paths["render"])],
            "bug_hunt_checks": {
                "overlap": True, "clipping": True, "label_clearance": True,
                "footer_collision": True, "contrast": True, "text_wrapping": True,
                "placeholder_content": True, "reading_order": True,
            },
            "non_diagram_support_blocks": 3,
            "density_telemetry": {
                "visible_word_count": 100, "perceptual_group_count": 8, "min_font_pt": 16,
                "direct_label_rate": 1.0, "edge_crossings": 0, "whitespace_ratio": 0.5,
            },
            "hard_checks": {name: 0 for name in PIPELINE.RENDER_HARD_CHECKS},
            "scores": {"hierarchy": 5, "render_qa": 5},
        }
        for key, value in (("semantic", semantic), ("reader", reader), ("executive", executive),
                           ("writer", writer), ("visual", visual)):
            self.put(key, value)

    def slide_args(self):
        names = (
            "point", "point-model", "point-hash-file", "point-gate", "deck",
            "render-manifest", "deck-inspect", "visual-query", "visual-baseline",
            "brief", "constraints", "component-rubric", "component-catalog",
            "visual-jobs-a", "visual-jobs-b", "component-score-a", "component-score-b",
            "component-ensemble-a", "component-ensemble-b", "candidate-a", "candidate-b",
            "component-selection-audit", "component-gate", "visual-model", "selection",
            "semantic", "reader", "executive", "writer", "visual",
        )
        args = []
        for name in names:
            args += [f"--{name}", str(self.paths[name.replace("-", "_")])]
        args += ["--output", str(self.root / "slide-gate.json")]
        self.paths["slide_gate"] = self.root / "slide-gate.json"
        return args

    def run_slide_gate(self):
        return subprocess.run(
            [sys.executable, str(PIPELINE_PATH), "slide-gate", *self.slide_args()],
            check=False, capture_output=True, text=True,
        )

    def refresh_render_manifest_hashes(self):
        value = digest(self.paths["render_manifest"])
        for key in ("semantic", "reader", "executive", "writer", "visual"):
            review = self.load(key)
            review["render_manifest_sha256"] = value
            self.save(key, review)

    def refresh_visual_model_hashes(self):
        value = digest(self.paths["visual_model"])
        selection = self.load("selection")
        selection["visual_model_sha256"] = value
        self.save("selection", selection)
        for key in ("semantic", "reader", "executive", "writer", "visual"):
            review = self.load(key)
            review["visual_model_sha256"] = value
            self.save(key, review)


class VisualComponentSelectionTest(unittest.TestCase):
    def test_valid_intel_rats_component_bundle(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            result = fixture.run_component_gate()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            gate = json.loads((fixture.root / "component-gate.json").read_text())
            self.assertTrue(gate["passed"])
            self.assertEqual(gate["selected_ensemble_score"], 100.0)

    def test_structural_generic_card_grid_cannot_be_eligible(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            required, jobs, components = fixture.context("A")
            scores = fixture.load("component_score_a")
            card = copy.deepcopy(scores["components"][0])
            card["component_id"] = "A-CARDS"
            card["family"] = "generic-card-grid"
            card["catalog_extension"] = {"definition": "generic cards", "job_fit": "lists facts"}
            card["eligible"] = True
            card["hard_failures"] = []
            scores["components"] = [card, *scores["components"][1:]]
            claims, nodes, edges, boundaries = PIPELINE.point_id_sets(
                yaml.safe_load(fixture.paths["point_model"].read_text())
            )
            failures, _ = PIPELINE.validate_component_scores(
                scores, "cards", jobs, PIPELINE.validate_component_catalog(fixture.catalog())[1],
                claims, nodes | edges | boundaries,
                {f"VB-{index:03d}" for index in range(1, 10)}, True,
            )
            self.assertTrue(any("generic card grid" in item for item in failures))
            self.assertTrue(any("eligibility" in item for item in failures))

    def test_collapsed_actor_or_boundary_fails_ensemble(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            required, jobs, components = fixture.context("A")
            ensemble = fixture.load("component_ensemble_a")
            ensemble["preserved_distinction_ids"].remove("D-QGS-TDQE")
            failures, _ = PIPELINE.validate_component_ensemble(
                ensemble, "collapsed", components, jobs, required,
            )
            self.assertTrue(any("required distinction" in item for item in failures))

    def test_selecting_every_high_component_fails_overload_and_redundancy(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            required, jobs, components = fixture.context("A")
            extra = copy.deepcopy(components["A-PROOF"])
            extra["component_id"] = "A-EXTRA"
            components["A-EXTRA"] = extra
            ensemble = fixture.load("component_ensemble_a")
            ensemble["supporting_component_ids"].append("A-EXTRA")
            ensemble["selected_component_ids"].append("A-EXTRA")
            ensemble["support_contributions"].append({
                "component_id": "A-EXTRA", "incremental_baseline_ids": [],
                "incremental_value": "meaningful_new_baseline", "justification": "duplicate",
            })
            ensemble["redundancy_penalty"] = 5
            ensemble["ensemble_score"] = 95
            failures, _ = PIPELINE.validate_component_ensemble(
                ensemble, "overloaded", components, jobs, required,
            )
            self.assertTrue(any("more than three" in item or "overloads" in item for item in failures))
            self.assertTrue(any("adds no" in item for item in failures))

    def test_support_without_new_must_see_id_is_excluded(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            required, jobs, components = fixture.context("A")
            components["A-PROOF"]["covered_baseline_set"] = {"VB-001"}
            ensemble = fixture.load("component_ensemble_a")
            ensemble["support_contributions"][0]["incremental_baseline_ids"] = []
            failures, _ = PIPELINE.validate_component_ensemble(
                ensemble, "no-increment", components, jobs, required,
            )
            self.assertTrue(any("adds no" in item for item in failures))

    def test_custom_domain_diagram_is_required_when_standard_types_fail(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            required, jobs, components = fixture.context("A")
            for component in components.values():
                if component["role"] == "dominant":
                    component["eligible_value"] = False
                    component["calculated_score"] = 60
            custom = copy.deepcopy(components["A-DOM"])
            custom["component_id"] = "A-CUSTOM"
            custom["family"] = "custom-domain-diagram"
            custom["eligible_value"] = True
            custom["calculated_score"] = 100
            components["A-CUSTOM"] = custom
            ensemble = fixture.load("component_ensemble_a")
            ensemble["dominant_component_id"] = "A-CUSTOM"
            ensemble["selected_component_ids"][0] = "A-CUSTOM"
            ensemble["custom_fallback_reason"] = "All applicable standard families lost a required trust distinction."
            failures, summary = PIPELINE.validate_component_ensemble(
                ensemble, "fallback", components, jobs, required,
            )
            self.assertFalse(any("fall back" in item or "custom fallback" in item for item in failures), failures)
            self.assertEqual(summary["dominant_component_id"], "A-CUSTOM")

    def test_same_visual_grammar_fails_component_gate(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            candidate_a = fixture.load("candidate_a")
            candidate_b = fixture.load("candidate_b")
            candidate_b["visual_grammar_signature"] = candidate_a["visual_grammar_signature"]
            fixture.save("candidate_b", candidate_b)
            audit = fixture.load("component_selection_audit")
            audit["candidate_b_sha256"] = digest(fixture.paths["candidate_b"])
            fixture.save("component_selection_audit", audit)
            result = fixture.run_component_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads((fixture.root / "component-gate.json").read_text())
            self.assertTrue(any("same visual grammar" in item for item in gate["failures"]))

    def test_component_artifacts_cannot_mix_immutable_rounds(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            candidate_b = fixture.load("candidate_b")
            candidate_b["round"] = 2
            fixture.save("candidate_b", candidate_b)
            audit = fixture.load("component_selection_audit")
            audit["candidate_b_sha256"] = digest(fixture.paths["candidate_b"])
            fixture.save("component_selection_audit", audit)
            result = fixture.run_component_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads((fixture.root / "component-gate.json").read_text())
            self.assertTrue(any("immutable round" in item for item in gate["failures"]))


class SlideGateRegressionTest(unittest.TestCase):
    def test_existing_gates_and_freeze_still_pass(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertEqual(gate["slide_score"], 100.0)
            final = fixture.root / "final"
            freeze = subprocess.run([
                sys.executable, str(PIPELINE_PATH), "freeze", "--deck", str(fixture.paths["deck"]),
                "--gate", str(fixture.paths["slide_gate"]), "--output-dir", str(final),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(freeze.returncode, 0, freeze.stdout + freeze.stderr)
            self.assertTrue((final / "final-deck.pptx").is_file())

    def test_required_ids_reach_final_visual_object_map(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            for item in visual_model["objects"]:
                if "C-009" in item["point_ids"]:
                    item["point_ids"].remove("C-009")
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("misses Point IDs selected" in item for item in gate["failures"]))

    def test_final_artifact_cannot_merge_result_and_release_action(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            for item in visual_model["objects"]:
                if "E-RESULT" in item["model_ids"]:
                    item["model_ids"].append("E-ACTION")
                    break
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("collapses required distinction D-RESULT-ACTION" in item
                                for item in gate["failures"]))

    def test_slide_gate_rejects_absolute_render_manifest_paths(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            manifest = fixture.load("render_manifest")
            manifest["slides"][0]["path"] = str(fixture.paths["render"].resolve())
            fixture.save("render_manifest", manifest)
            fixture.refresh_render_manifest_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("absolute" in item for item in gate["failures"]))

    def test_slide_gate_rejects_script_producer_outside_manifest_directory(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            manifest = fixture.load("render_manifest")
            manifest["producer"] = {
                "kind": "script",
                "command": "python build.py",
                "source_path": "../build.py",
                "source_sha256": "0" * 64,
            }
            fixture.save("render_manifest", manifest)
            fixture.refresh_render_manifest_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("producer source path must stay" in item for item in gate["failures"]))

    def test_slide_gate_requires_thumbnail_mechanism_evidence(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual = fixture.load("visual")
            visual.pop("thumbnail_raw_mechanism_answers")
            visual.pop("thumbnail_mechanism_recovered_ids")
            fixture.save("visual", visual)
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("thumbnail mechanism" in item for item in gate["failures"]))

    def test_slide_gate_requires_complete_security_boundary_trace(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            visual_model["security_boundary_trace"].pop("failure_object_ids")
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("security boundary trace" in item for item in gate["failures"]))

    def test_slide_gate_rejects_collapsed_or_directionless_critical_artifact_trace(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            trace = visual_model["critical_artifact_traces"][0]
            trace["checker_object_ids"] = list(trace["producer_object_ids"])
            trace["visible_direction"] = "not-a-direction"
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("critical artifact trace" in item for item in gate["failures"]))

    def test_slide_gate_rejects_collapsed_security_boundary_roles(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            trace = visual_model["security_boundary_trace"]
            trace["decision_object_ids"] = list(trace["checker_object_ids"])
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("security boundary trace" in item for item in gate["failures"]))

    def test_slide_gate_requires_connected_critical_artifact_trace(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            visual_model["critical_artifact_traces"][0]["connector_paths"] = []
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("connector_paths" in item for item in gate["failures"]))

    def test_slide_gate_requires_complete_critical_artifact_trace(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            visual_model = fixture.load("visual_model")
            visual_model["critical_artifact_traces"][0]["connector_object_ids"] = []
            fixture.save("visual_model", visual_model)
            fixture.refresh_visual_model_hashes()
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("critical artifact trace" in item for item in gate["failures"]))

    def test_legacy_thresholds_and_render_hard_checks_are_unchanged(self):
        with tempfile.TemporaryDirectory() as value:
            fixture = IntelRatsFixture(value)
            fixture.make_slide_gate_fixture()
            writer = fixture.load("writer")
            writer["scores"]["headline_clarity"] = 3
            fixture.save("writer", writer)
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("below 4/5" in item for item in gate["failures"]))

            writer["scores"]["headline_clarity"] = 5
            fixture.save("writer", writer)
            for key in ("selection", "semantic", "reader", "executive", "writer", "visual"):
                review = fixture.load(key)
                for criterion in review["scores"]:
                    review["scores"][criterion] = 4
                fixture.save(key, review)
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("slide score below 90" in item for item in gate["failures"]))

            visual = fixture.load("visual")
            visual["hard_checks"]["overflow"] = 1
            fixture.save("visual", visual)
            result = fixture.run_slide_gate()
            self.assertEqual(result.returncode, 2)
            gate = json.loads(fixture.paths["slide_gate"].read_text())
            self.assertTrue(any("overflow must be zero" in item for item in gate["failures"]))


if __name__ == "__main__":
    unittest.main()
