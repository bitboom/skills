import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]
POINT = REPOSITORY / "skills" / "communication" / "point" / "scripts" / "pipeline.py"
DECK = REPOSITORY / "skills" / "communication" / "to-deck" / "scripts" / "pipeline.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


class PointPipelineTest(unittest.TestCase):
    def make_run(self, root, teach_back=True):
        draft = root / "point.md"
        model = root / "point.yaml"
        draft.write_text("# Point\nA mechanism produces a decision.\n", encoding="utf-8")
        model.write_text("model:\n  nodes: [A, B]\n  edges: [A-B]\n", encoding="utf-8")
        common = {
            "round": 1,
            "artifact_sha256": digest(draft),
            "model_sha256": digest(model),
            "critical_issues": [],
            "issues": [],
        }
        query = root / "query.md"
        query.write_text("Explain the domain without project context.\n", encoding="utf-8")
        prior = {
            "project_context_seen": False,
            "is_evidence": False,
            "status": "coverage_hypothesis",
            "model_identity": "test-reasoning-model",
            "domain_query_sha256": digest(query),
            "candidate_topics": ["mechanism"],
        }
        baseline = {
            "project_context_seen": False,
            "critical_essentials": [
                {"id": "B-001", "text": "problem", "source_ids": ["S-001"]},
                {"id": "B-002", "text": "proof limit", "source_ids": ["S-001"]},
            ],
            "source_ids": ["S-001"],
        }
        source_model = {
            "baseline_context_seen": False,
            "project_insights": [
                {"id": "P-001", "text": "role map"},
                {"id": "P-002", "text": "flow comparison"},
            ],
        }
        save(root / "prior.json", prior)
        save(root / "baseline.json", baseline)
        save(root / "source-model.json", source_model)
        synthesis = {
            "round": 1,
            "domain_query_sha256": digest(query),
            "prior_sha256": digest(root / "prior.json"),
            "baseline_sha256": digest(root / "baseline.json"),
            "source_model_sha256": digest(root / "source-model.json"),
            "artifact_sha256": digest(draft),
            "model_sha256": digest(model),
            "scores": {
                "domain_baseline_coverage": 5,
                "project_relevance": 5,
                "synthesis_gain": 5,
            },
            "hard_checks": {
                "prior_used_as_evidence": False,
                "prior_project_context_seen": False,
                "baseline_project_context_seen": False,
                "source_baseline_context_seen": False,
                "authoritative_baseline": True,
                "domain_first": True,
                "project_value_statement_present": True,
                "blind_comparison_completed": True,
                "final_domain_coverage_not_below_baseline": True,
                "final_project_fidelity_not_below_source": True,
                "unresolved_critical_domain_gaps": 0,
            },
            "baseline_strengths_adopted": ["problem framing"],
            "source_strengths_adopted": ["role map", "flow comparison"],
            "content_balance": {"domain_core_share": 0.6, "project_lens_share": 0.25, "assessment_share": 0.15},
            "coverage_rows": [
                {"concept_id": "B-001", "relationship": "aligned", "selection": "must", "selected_from": "both", "final_ids": ["C-001"]},
                {"concept_id": "B-002", "relationship": "missing", "selection": "must", "selected_from": "baseline", "final_ids": ["C-002"]},
                {"concept_id": "P-001", "relationship": "source_addition", "selection": "should", "selected_from": "source", "final_ids": ["C-003"]},
                {"concept_id": "P-002", "relationship": "source_addition", "selection": "should", "selected_from": "source", "final_ids": ["C-004"]},
            ],
            "critical_issues": [],
            "issues": [],
        }
        save(root / "synthesis.json", synthesis)
        reviews = {
            "fact": common | {
                "claims_total": 3, "claims_checked": 3,
                "model_elements_total": 3, "model_elements_checked": 3,
                "time_sensitive_total": 0, "time_sensitive_checked": 0,
                "critical_unsupported": 0, "critical_conflicts": 0,
                "critical_authoritative_source_gaps": 0,
            },
            "domain": common | {
                "scores": {"conceptual_coverage": 5, "structural_completeness": 5},
                "hard_checks": {
                    "what_how_why_action_complete": True,
                    "essentials_defined": True,
                    "exclusions_defined": True,
                    "structural_topic": True,
                    "model_nodes": 2,
                    "model_edges": 1,
                    "trust_boundaries_required": False,
                    "model_boundaries": 0,
                    "problem_threat_model_flow_proof_limits_policy_complete": True,
                    "context_dependencies_required": True,
                    "context_dependencies_closed": True,
                    "cross_boundary_result_auth_required": True,
                    "cross_boundary_results_authenticated": True,
                    "threat_model_required": True,
                    "threat_assumptions_explicit": True,
                    "trust_semantics_required": True,
                    "trust_semantics_not_collapsed": True,
                    "result_identity_required": True,
                    "decision_result_identifies_evidence_and_policy": True,
                },
            },
            "reader": common | {
                "scores": {
                    "audience_comprehension": 5,
                    "mental_model_clarity": 5,
                    "one_line_clarity": 5,
                },
                "teach_back_match": teach_back,
                "can_explain_problem": True,
                "can_explain_flow": True,
                "can_explain_proves_and_limits": True,
                "can_explain_project_value": True,
                "critical_questions": [],
            },
            "writer": common | {
                "scores": {
                    "logical_coherence": 5,
                    "unambiguity": 5,
                    "compression_without_loss": 5,
                },
            },
            "prose": common | {
                "language": "ko-KR",
                "scores": {
                    "reader_fit": 5,
                    "terminology_onboarding": 5,
                    "causal_cohesion": 5,
                    "concision_without_loss": 5,
                },
                "hard_checks": {
                    "claim_ids_preserved": True,
                    "citations_and_qualifiers_preserved": True,
                    "critical_terms_defined_or_known": True,
                    "actors_and_actions_explicit": True,
                    "paragraphs_answer_one_reader_question": True,
                    "language_is_natural_for_audience": True,
                    "unresolved_literal_translation_count": 0,
                },
            },
            "executive": common | {
                "scores": {"decision_relevance": 5, "so_what_clarity": 5},
                "can_explain_capability_value": True,
                "can_explain_trust_limit": True,
                "can_identify_decision_owner": True,
                "can_identify_next_action": True,
                "critical_questions": [],
            },
        }
        for name, value in reviews.items():
            save(root / f"{name}.json", value)
        return draft, model

    def test_point_gate_pass_and_freeze(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root)
            gate = root / "gate.json"
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate",
                "--draft", str(draft), "--model", str(model),
                "--fact", str(root / "fact.json"), "--domain", str(root / "domain.json"),
                "--reader", str(root / "reader.json"), "--writer", str(root / "writer.json"),
                "--prose", str(root / "prose.json"),
                "--query", str(root / "query.md"),
                "--prior", str(root / "prior.json"), "--baseline", str(root / "baseline.json"),
                "--source-model", str(root / "source-model.json"), "--synthesis", str(root / "synthesis.json"),
                "--executive", str(root / "executive.json"), "--output", str(gate),
            ], check=False)
            self.assertEqual(result.returncode, 0)
            frozen = root / "final"
            subprocess.run([
                sys.executable, str(POINT), "freeze", "--markdown", str(draft),
                "--model", str(model), "--gate", str(gate), "--output-dir", str(frozen),
            ], check=True)
            self.assertTrue((frozen / "point.sha256").is_file())

    def test_point_gate_rejects_failed_teachback(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root, teach_back=False)
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate", "--draft", str(draft),
                "--model", str(model), "--fact", str(root / "fact.json"),
                "--domain", str(root / "domain.json"), "--reader", str(root / "reader.json"),
                "--query", str(root / "query.md"),
                "--prior", str(root / "prior.json"), "--baseline", str(root / "baseline.json"),
                "--source-model", str(root / "source-model.json"), "--synthesis", str(root / "synthesis.json"),
                "--writer", str(root / "writer.json"), "--prose", str(root / "prose.json"),
                "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)

    def test_point_gate_rejects_failed_prose_review(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root)
            prose = json.loads((root / "prose.json").read_text())
            prose["hard_checks"]["language_is_natural_for_audience"] = False
            save(root / "prose.json", prose)
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate", "--draft", str(draft),
                "--model", str(model), "--fact", str(root / "fact.json"),
                "--domain", str(root / "domain.json"), "--reader", str(root / "reader.json"),
                "--query", str(root / "query.md"),
                "--prior", str(root / "prior.json"), "--baseline", str(root / "baseline.json"),
                "--source-model", str(root / "source-model.json"), "--synthesis", str(root / "synthesis.json"),
                "--writer", str(root / "writer.json"), "--prose", str(root / "prose.json"),
                "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)

    def test_point_gate_rejects_missing_baseline_and_project_value(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root)
            synthesis = json.loads((root / "synthesis.json").read_text())
            synthesis["coverage_rows"] = synthesis["coverage_rows"][:1]
            synthesis["hard_checks"]["project_value_statement_present"] = False
            save(root / "synthesis.json", synthesis)
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate", "--draft", str(draft),
                "--model", str(model), "--fact", str(root / "fact.json"),
                "--domain", str(root / "domain.json"), "--reader", str(root / "reader.json"),
                "--query", str(root / "query.md"),
                "--writer", str(root / "writer.json"), "--prior", str(root / "prior.json"),
                "--baseline", str(root / "baseline.json"), "--source-model", str(root / "source-model.json"),
                "--synthesis", str(root / "synthesis.json"), "--prose", str(root / "prose.json"),
                "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)

    def test_point_gate_rejects_stale_independent_query(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root)
            (root / "query.md").write_text("A different independent prompt.\n", encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate", "--draft", str(draft),
                "--model", str(model), "--fact", str(root / "fact.json"),
                "--domain", str(root / "domain.json"), "--reader", str(root / "reader.json"),
                "--writer", str(root / "writer.json"), "--query", str(root / "query.md"),
                "--prior", str(root / "prior.json"), "--baseline", str(root / "baseline.json"),
                "--source-model", str(root / "source-model.json"),
                "--synthesis", str(root / "synthesis.json"), "--prose", str(root / "prose.json"),
                "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)

    def test_point_gate_rejects_open_context_dependency(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            draft, model = self.make_run(root)
            domain = json.loads((root / "domain.json").read_text())
            domain["hard_checks"]["context_dependencies_closed"] = False
            save(root / "domain.json", domain)
            result = subprocess.run([
                sys.executable, str(POINT), "point-gate", "--draft", str(draft),
                "--model", str(model), "--fact", str(root / "fact.json"),
                "--domain", str(root / "domain.json"), "--reader", str(root / "reader.json"),
                "--writer", str(root / "writer.json"), "--query", str(root / "query.md"),
                "--prior", str(root / "prior.json"), "--baseline", str(root / "baseline.json"),
                "--source-model", str(root / "source-model.json"),
                "--synthesis", str(root / "synthesis.json"), "--prose", str(root / "prose.json"),
                "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)


@unittest.skip("Superseded by skills/communication/to-deck/tests/test_component_selection.py")
class DeckPipelineTest(unittest.TestCase):
    HARD_CHECKS = (
        "semantic_drift", "overflow", "unintended_overlap", "clipping",
        "broken_or_unreadable_text", "diagram_direction_errors",
        "missing_material_sources", "title_wrap", "body_below_16pt",
        "midlevel_below_24pt", "slide_title_below_35pt", "unsupported_glyphs",
        "critical_contrast_failure", "font_substitution", "color_only_encoding",
        "missing_alt_text", "invalid_reading_order",
    )

    def make_run(self, root):
        point = root / "point.md"
        model = root / "point.yaml"
        point.write_text("approved", encoding="utf-8")
        model.write_text(
            "model:\n"
            "  nodes: [{id: N1}, {id: N2}, {id: N3}]\n"
            "  edges: [{id: E1}, {id: E2}]\n"
            "  boundaries: [{id: B1}]\n",
            encoding="utf-8",
        )
        point_hash = root / "point.sha256"
        point_hash.write_text(
            f"{digest(point)}  point.md\n{digest(model)}  point.yaml\n", encoding="utf-8"
        )
        save(root / "point-gate.json", {
            "passed": True, "artifact_sha256": digest(point), "model_sha256": digest(model),
        })
        brief = root / "brief.yaml"
        brief.write_text(
            "slide_count: 1\nprior_deck: \nuser_rejected_dimensions: []\n", encoding="utf-8"
        )
        deck = root / "deck.pptx"
        with zipfile.ZipFile(deck, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr("ppt/slides/slide1.xml", "<p:sld/>")
        render = root / "slide-1.png"
        render.write_bytes(b"render")
        render_manifest = root / "render-manifest.json"
        save(render_manifest, {
            "renderer": "test", "renderer_version": "1", "command": "render test",
            "generated_at": "2026-07-16T00:00:00Z", "slide_count": 1,
            "slides": [{"path": str(render), "sha256": digest(render), "width": 1280, "height": 720}],
        })
        inspect = root / "deck.inspect.ndjson"
        records = [
            {"kind": "slide", "id": "sl/1", "slide": 1},
            {"kind": "shape", "id": "sh/n1", "slide": 1, "bbox": [80, 160, 220, 160]},
            {"kind": "shape", "id": "sh/n2", "slide": 1, "bbox": [430, 160, 220, 160]},
            {"kind": "shape", "id": "sh/n3", "slide": 1, "bbox": [780, 160, 220, 160]},
            {"kind": "shape", "id": "sh/e1", "slide": 1, "bbox": [300, 220, 130, 10]},
            {"kind": "shape", "id": "sh/e2", "slide": 1, "bbox": [650, 220, 130, 10]},
            {"kind": "shape", "id": "sh/b1", "slide": 1, "bbox": [40, 100, 1100, 400]},
        ]
        inspect.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")
        query = root / "query.md"
        query.write_text("visual baseline", encoding="utf-8")
        baseline = root / "visual-baseline.json"
        must = [{"id": f"VB-{number:03d}"} for number in range(1, 6)]
        save(baseline, {
            "must_see": must,
            "semantic_required_ids": ["VB-002", "VB-003", "VB-004"],
            "gist_required_ids": ["VB-001"],
            "reconstruction_required_ids": ["VB-002", "VB-003", "VB-004"],
            "executive_required_ids": ["VB-001", "VB-005"],
            "headline_required_ids": ["VB-001"],
        })
        constraints = root / "constraints.json"
        candidate_a = root / "candidate-a.json"
        candidate_b = root / "candidate-b.json"
        save(constraints, {"slide_count": 1})
        save(candidate_a, {"candidate_id": "A", "visual_grammar": "flow"})
        save(candidate_b, {"candidate_id": "B", "visual_grammar": "architecture"})
        visual_model = root / "visual-model.json"
        save(visual_model, {"objects": [
            {"id": "O1", "kind": "node", "artifact_object_ids": ["sh/n1"], "baseline_ids": ["VB-001"]},
            {"id": "O2", "kind": "node", "artifact_object_ids": ["sh/n2"], "baseline_ids": ["VB-002"]},
            {"id": "O3", "kind": "node", "artifact_object_ids": ["sh/n3"], "baseline_ids": ["VB-003"]},
            {"id": "O4", "kind": "connector", "artifact_object_ids": ["sh/e1"], "baseline_ids": ["VB-004"]},
            {"id": "O5", "kind": "connector", "artifact_object_ids": ["sh/e2"], "baseline_ids": []},
            {"id": "O6", "kind": "boundary", "artifact_object_ids": ["sh/b1"], "baseline_ids": ["VB-005"]},
        ]})
        selection = {
            "round": 1, "point_sha256": digest(point),
            "visual_query_sha256": digest(query), "visual_baseline_sha256": digest(baseline),
            "brief_sha256": digest(brief), "constraints_sha256": digest(constraints),
            "candidate_a_sha256": digest(candidate_a), "candidate_b_sha256": digest(candidate_b),
            "visual_model_sha256": digest(visual_model),
            "scores": {"visual_baseline_coverage": 5, "candidate_comparison_quality": 5},
            "hard_checks": {
                "candidate_a_blind": True, "candidate_b_blind": True,
                "candidate_visual_grammars_distinct": True, "prior_deck_hidden": True,
                "selection_reasoned": True, "dominant_diagram_selected": True,
                "project_lens_secondary": True, "no_new_claims": True,
            },
            "selected_candidate": "synthesis", "must_see_total": 5, "must_see_mapped": 5,
            "coverage_rows": must, "candidate_a_strengths": ["flow"],
            "candidate_b_strengths": ["boundary"], "critical_issues": [], "issues": [],
        }
        save(root / "selection.json", selection)
        common = {
            "round": 1, "point_sha256": digest(point), "point_model_sha256": digest(model),
            "brief_sha256": digest(brief), "deck_sha256": digest(deck),
            "render_manifest_sha256": digest(render_manifest), "deck_inspect_sha256": digest(inspect),
            "visual_model_sha256": digest(visual_model), "author_id": "builder",
            "author_model": "test-model", "review_prompt_sha256": "a" * 64,
            "critical_issues": [], "issues": [],
        }
        semantic = common | {
            "reviewer_id": "semantic", "reviewer_model": "test-model",
            "scores": {"point_coverage": 5, "causal_structure_visibility": 5, "diagram_accuracy": 5},
            "structural_elements": 3, "relationships": 2, "diagram_required": True,
            "dominant_visual_present": True, "semantic_visual_share": 0.614,
            "nodes_total": 3, "nodes_checked": 3, "edges_total": 2, "edges_checked": 2,
            "boundaries_total": 1, "boundaries_checked": 1, "diagram_direction_errors": 0,
            "visual_grammar_matches_job": True, "trust_roles_not_collapsed": True,
            "project_assessment_secondary": True,
            "verified_semantic_ids": ["VB-002", "VB-003", "VB-004"],
        }
        reader = common | {
            "reviewer_id": "reader", "reviewer_model": "test-model",
            "scores": {"novice_comprehension": 5}, "allowed_inputs": ["rendered_slides"],
            "point_context_seen": False, "storyboard_context_seen": False, "prior_scores_seen": False,
            "gist_exposure_seconds": 8, "reconstruction_exposure_seconds": 25,
            "raw_gist_answers": {"gist": "decision"},
            "raw_reconstruction_answers": {"model": "flow and boundary"},
            "gist_recovered_ids": ["VB-001"],
            "reconstruction_recovered_ids": ["VB-002", "VB-003", "VB-004"],
            "teach_back_match": True, "critical_questions": [],
        }
        executive = common | {
            "reviewer_id": "executive", "reviewer_model": "test-model",
            "scores": {"executive_takeaway": 5}, "allowed_inputs": ["rendered_slides"],
            "point_context_seen": False, "storyboard_context_seen": False, "prior_scores_seen": False,
            "raw_answers": {"decision": "value and owner"},
            "executive_recovered_ids": ["VB-001", "VB-005"], "critical_questions": [],
        }
        writer = common | {
            "reviewer_id": "writer", "reviewer_model": "test-model",
            "scores": {"headline_clarity": 5}, "headline_domain_first": True,
            "headline_is_assertion": True, "meta_evaluation_language_absent": True,
            "labels_plain_language": True, "compression_preserves_model": True,
            "headline_recovered_ids": ["VB-001"], "unexplained_critical_terms": 0,
        }
        visual = common | {
            "reviewer_id": "visual", "reviewer_model": "test-model",
            "scores": {"hierarchy": 5, "render_qa": 5},
            "full_size_render_inspected": True, "thumbnail_render_inspected": True,
            "structural_test_passed": True, "slide_count_match": True,
            "non_diagram_support_blocks": 2,
            "density_telemetry": {
                "visible_word_count": 80, "perceptual_group_count": 6, "min_font_pt": 18,
                "direct_label_rate": 1.0, "edge_crossings": 0, "whitespace_ratio": 0.3,
            },
            "hard_checks": {name: 0 for name in self.HARD_CHECKS},
        }
        for name, review in (("semantic", semantic), ("reader", reader),
                             ("executive", executive), ("writer", writer), ("visual", visual)):
            save(root / f"{name}.json", review)
        return {
            "point": point, "point-model": model, "point-hash-file": point_hash,
            "point-gate": root / "point-gate.json", "brief": brief, "deck": deck,
            "render-manifest": render_manifest, "deck-inspect": inspect,
            "visual-query": query, "visual-baseline": baseline, "constraints": constraints,
            "candidate-a": candidate_a, "candidate-b": candidate_b, "visual-model": visual_model,
            "selection": root / "selection.json", "semantic": root / "semantic.json",
            "reader": root / "reader.json", "executive": root / "executive.json",
            "writer": root / "writer.json", "visual": root / "visual.json",
            "output": root / "gate.json",
        }

    def command(self, paths):
        command = [sys.executable, str(DECK), "slide-gate"]
        for name, path in paths.items():
            command.extend([f"--{name}", str(path)])
        return command

    def test_artifact_bound_gate_passes_complete_fixture(self):
        with tempfile.TemporaryDirectory() as value:
            paths = self.make_run(Path(value))
            result = subprocess.run(self.command(paths), check=False)
            self.assertEqual(result.returncode, 0)

    def test_rejects_missing_real_connectors_even_with_perfect_scores(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            paths = self.make_run(root)
            model = json.loads(paths["visual-model"].read_text())
            model["objects"] = [item for item in model["objects"] if item["kind"] != "connector"]
            save(paths["visual-model"], model)
            result = subprocess.run(self.command(paths), check=False)
            self.assertEqual(result.returncode, 2)

    def test_rejects_failed_blind_reader_reconstruction(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            paths = self.make_run(root)
            reader = json.loads(paths["reader"].read_text())
            reader["reconstruction_recovered_ids"] = ["VB-002"]
            save(paths["reader"], reader)
            result = subprocess.run(self.command(paths), check=False)
            self.assertEqual(result.returncode, 2)

    def test_rejects_stale_deck_reviews(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            paths = self.make_run(root)
            with zipfile.ZipFile(paths["deck"], "a") as archive:
                archive.writestr("changed.txt", "changed")
            result = subprocess.run(self.command(paths), check=False)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
