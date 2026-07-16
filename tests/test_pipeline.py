import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


POINT = Path("/root/.codex/skills/remote-skills/skill-6a58b466be148191b7d19dfb66387db5/scripts/pipeline.py")
DECK = Path("/root/.codex/skills/remote-skills/skill-6a58a9ef7c8081919e19102e69057435/scripts/pipeline.py")


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
                "--writer", str(root / "writer.json"), "--output", str(root / "gate.json"),
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
                "--synthesis", str(root / "synthesis.json"), "--output", str(root / "gate.json"),
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
                "--synthesis", str(root / "synthesis.json"), "--output", str(root / "gate.json"),
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
                "--synthesis", str(root / "synthesis.json"), "--output", str(root / "gate.json"),
            ], check=False)
            self.assertEqual(result.returncode, 2)


class DeckPipelineTest(unittest.TestCase):
    def test_requires_meaning_bearing_diagram(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            point = root / "point.md"
            point.write_text("approved", encoding="utf-8")
            common = {
                "round": 1, "point_sha256": digest(point),
                "critical_issues": [], "issues": [],
            }
            diagram = common | {
                "scores": {"point_coverage": 5, "structural_visibility": 5, "diagram_accuracy": 5},
                "structural_elements": 4, "relationships": 3, "diagram_required": True,
                "dominant_visual_present": False, "semantic_visual_share": 0.2,
                "nodes_total": 4, "nodes_checked": 4, "edges_total": 3, "edges_checked": 3,
                "boundaries_total": 1, "boundaries_checked": 1, "diagram_direction_errors": 0,
            }
            reader = common | {
                "scores": {"reader_comprehension": 5}, "teach_back_match": True,
                "headline_paraphrase_match": True, "identified_input": True,
                "identified_decision_maker": True, "identified_action": True,
                "identified_outcome": True, "critical_questions": [],
            }
            executive = common | {
                "scores": {"first_glance_takeaway": 5}, "so_what_clear": True,
                "decision_clear": True, "risk_or_constraint_clear": True,
                "next_action_clear": True, "critical_questions": [],
            }
            visual = common | {
                "scores": {"hierarchy": 5, "traceability_qa": 5},
                "hard_checks": {name: 0 for name in (
                    "semantic_drift", "overflow", "unintended_overlap", "clipping",
                    "broken_or_unreadable_text", "diagram_direction_errors",
                    "missing_material_sources",
                )},
            }
            for name, review in (("diagram", diagram), ("reader", reader),
                                 ("executive", executive), ("visual", visual)):
                save(root / f"{name}.json", review)
            command = [
                sys.executable, str(DECK), "slide-gate", "--point", str(point),
                "--diagram", str(root / "diagram.json"), "--reader", str(root / "reader.json"),
                "--executive", str(root / "executive.json"), "--visual", str(root / "visual.json"),
                "--output", str(root / "gate.json"),
            ]
            failed = subprocess.run(command, check=False)
            self.assertEqual(failed.returncode, 2)
            diagram["dominant_visual_present"] = True
            diagram["semantic_visual_share"] = 0.6
            save(root / "diagram.json", diagram)
            passed = subprocess.run(command, check=False)
            self.assertEqual(passed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
