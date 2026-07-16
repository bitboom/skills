# Visual component selection

## Contents

1. Artifact flow
2. Visual-job map
3. Individual component scoring
4. Hard failures
5. Ensemble selection
6. Independent A/B and selection audit
7. Final traceability
8. Security-flow separation checklist

## Artifact flow

Create the fixed rubric, then the open catalog. Each blind architect independently produces its own jobs, score matrix, ensemble, and storyboard. Run `component-gate` before slide construction.

```text
Point + baseline + constraints
        ↓
rubric → open catalog
        ↓                         ↓
jobs A → scores A → ensemble A → storyboard A
jobs B → scores B → ensemble B → storyboard B
        ↓                         ↓
      anonymized component-selection audit
        ↓
      existing storyboard Selection Reviewer
        ↓
      build → cold reads → render QA → slide gate
```

Pre-candidate artifacts use a deterministic branch seed rather than a future candidate-output hash. The seed hashes branch, Point, model, baseline, constraints, and rubric. Downstream artifacts also hash every causally prior file. The audit contains the actual A/B candidate hashes. This avoids circular self-hashes while preserving stale-artifact rejection.

## Visual-job map

Extract jobs from Point Claims, model nodes/edges/boundaries, and the blind visual baseline. Use these standard jobs, with `custom-...` extensions allowed: definition, mechanism, actor relationship, causal path, sequence, trust boundary, artifact movement, decision or branching, state transition, comparison, proof, non-proof, limitation, action, and project lens.

Every job requires all fields below:

```json
{
  "id": "VJ-004",
  "visual_job": "artifact-movement",
  "claim_ids": ["C-004"],
  "model_ids": ["E-013", "E-015"],
  "baseline_ids": ["VB-004", "VB-005"],
  "criticality": "critical",
  "intended_audiences": ["novice_developer", "technical_executive"],
  "expected_cold_read_answer": "Evidence is evaluated before a signed Result reaches the release owner.",
  "distinction_ids": ["D-EVIDENCE-RESULT-ACTION"]
}
```

Each branch also records critical relationship IDs, critical boundary IDs, explicit two-sided distinctions, required distinction IDs, and at least two applicable dominant families. A shared preprocessor must not choose the visual grammar.

Also record `required_causal_path` as exactly four ordered stages—`evidence`, `evaluation`, `authenticated_result`, and `policy_action`—with Claim, model, and baseline IDs for each stage. The ensemble and final visual-object map must cover every one of those IDs; labels alone do not close the path.

## Individual component scoring

Normalize each anchored 1–5 score to 100 with these weights:

| Criterion | Weight |
|---|---:|
| semantic coverage | 25 |
| structural fidelity | 20 |
| causal, directional and boundary expressiveness | 15 |
| novice-developer comprehension | 10 |
| technical-executive usefulness | 10 |
| density and legibility fit | 10 |
| visual hierarchy | 5 |
| editability and accessibility | 5 |

Every criterion stores `score` and an evidence-based `justification`. Every component also stores covered baseline, Point, and model IDs; uncovered IDs; visual-job IDs; preserved distinctions; risks; hard failures; assumptions; normalized score; and eligibility. Bare numeric self-scores fail.

### Individual anchors

| Criterion | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| semantic coverage | misses the governing claim | covers isolated terms | covers the main claim but loses required meaning | covers all assigned critical meaning with minor secondary gaps | covers assigned meaning completely and precisely |
| structural fidelity | contradicts the model | collapses important structure | approximate topology with recoverable omissions | preserves actors, artifacts, and major relations | preserves every assigned node, relation, state, and boundary |
| causal/directional/boundary expressiveness | no causal reading | ambiguous path or ownership | partial direction and boundary cues | clear path, direction, and material boundaries | closed path with explicit branching, provenance, and boundaries |
| novice comprehension | likely mis-teach | requires expert inference | gist recoverable but reconstruction fragile | novice can reconstruct assigned meaning | novice can accurately teach it back quickly |
| executive usefulness | no decision value | value or owner unclear | capability visible but action weak | capability, limit, owner, and action are clear | decision consequence and next action are immediate |
| density/legibility fit | unreadable at required size | severe overload | feasible only with risky compression | readable at font floors with manageable density | comfortably readable with reserve space |
| visual hierarchy | no dominant message | competing focal points | hierarchy present but weak | clear dominant argument and supporting order | immediate, stable hierarchy at full and thumbnail size |
| editability/accessibility | rasterized or color-only | difficult to edit and narrate | partly editable with metadata gaps | editable, labeled, non-color-redundant | fully editable with logical order and complete semantic descriptions |

Scores 1–5 must use the criterion-specific anchors in the immutable rubric artifact. Dominant eligibility requires at least 80. Supporting eligibility requires at least 70.

## Hard failures

Any listed failure makes that component ineligible regardless of score:

- `semantic-distortion`
- `collapsed-distinct-roles-or-boundaries`
- `causal-or-message-direction-missing`
- `evidence-result-action-path-broken`
- `proof-non-proof-confused`
- `source-project-dominates-domain`
- `decorative-card-listing`
- `unreadable-at-required-size`
- `color-only-encoding`
- `new-material-claim`

The catalog remains open, so additional failure codes may use a `custom-` prefix. Custom codes never replace the required list.

## Ensemble selection

Select exactly one eligible dominant component and no more than three eligible supports. Evaluate the combination again:

| Criterion | Weight |
|---|---:|
| complete must-see coverage | 30 |
| causal closure and structural correctness | 20 |
| complementarity and incremental value | 15 |
| low redundancy | 10 |
| cognitive load and readability | 10 |
| one coherent dominant visual argument | 10 |
| accessibility and editability | 5 |

### Ensemble anchors

| Criterion | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| complete coverage | most must-see meaning missing | several required sets missing | headline/gist present but reconstruction incomplete | every required set mapped with a minor noncritical gap | all must-see and required sets mapped exactly |
| causal closure | path is broken | major actor or boundary collapse | endpoints visible but middle logic weak | closed path with all critical relations and boundaries | fully closed mechanism with explicit alternate outcomes |
| complementarity | supports repeat the dominant | little incremental value | one useful addition amid repetition | every support adds new baseline meaning | minimum supports add distinct critical meaning only |
| low redundancy | pervasive duplication | multiple restatements | noticeable overlap | small justified overlap | no unnecessary repetition |
| cognitive load | unusable overload | exceeds space or font constraints | readable only with effort | readable within constraints | effortless scan plus reliable reconstruction |
| coherent argument | unrelated components | multiple competing stories | common topic but weak integration | one dominant story with ordered support | every support sharpens one visual argument |
| accessibility/editability | inaccessible and flattened | major edit/order gaps | partly editable | editable with complete labels and order | fully editable, narratable, and redundantly encoded |

Require every ensemble criterion at least 4/5 and the final score at least 90. Subtract five points per duplicate baseline assignment, capped at twenty. Each support must declare the exact baseline IDs it newly adds and classify the value as `critical_coverage` or `meaningful_new_baseline`. Empty incremental coverage fails.

Require semantic, gist, reconstruction, executive, and headline ID sets at 100%; zero missing critical relationships, boundaries, or distinctions; zero hard failures; zero unnecessary components; and one coherent dominant visual argument.

Do not select all high-scoring components. If no applicable standard dominant component is eligible, select an eligible `custom-domain-diagram` and record why the standard options failed.

## Independent A/B and selection audit

- A and B see identical Point, baseline, constraints, catalog, and rubric.
- They do not see the other branch's jobs, scores, ensemble, or grammar.
- Their dominant family must differ, or at least two material grammar dimensions must differ: composition pattern, primary encoding, and path topology.
- The audit reviewer sees anonymized candidates and evidence, not names, authors, or author aggregate scores.
- The reviewer recomputes every component and ensemble score, verifies actual ID coverage, rechecks redundancy and semantic fidelity, and then selects A, B, or synthesis.
- A synthesis records one dominant component, at most three incrementally useful supports, adopted and rejected components, and a reasoned `component_decisions` row for every adoption or rejection. Recompute its anchored ensemble score and redundancy penalty exactly as for A/B; require complete ID coverage, score at least 90, zero hard failures, and zero unnecessary components.

The existing Selection Reviewer then verifies that the final selection agrees with this audit and records the selected component IDs in `vNN-selection.json`.

## Final traceability

Each meaning-bearing `vNN-visual-model.json` object maps:

```json
{
  "id": "node-verifier",
  "kind": "node",
  "component_ids": ["A-DOMINANT"],
  "baseline_ids": ["VB-004"],
  "point_ids": ["C-002", "C-004"],
  "model_ids": ["N-003", "E-015", "B-004"],
  "artifact_object_ids": ["sh/verifier"]
}
```

The final visual-object map must contain every baseline, Point, model, and component ID selected by the ensemble. Every meaning-bearing object points to an inspected artifact object. Aggregate semantic IDs by artifact object and fail if one actual shape contains both sides of a required distinction. Page numbers, decoration, icons, and backgrounds contain no semantic mappings.

## Security-flow separation checklist

When present in Point, preserve these as explicit distinctions and test them in the component audit:

- QGS daemon versus TDQE;
- PCS authority versus PCCS cache/transport;
- Verifier owner versus Relying Party or release-policy owner;
- Evidence versus authenticated Result versus final release decision;
- proof versus non-proof;
- allow, deny, replay, expiry, and invalid outcomes.

Fail any component or ensemble that merges identities with different authenticity, availability, policy, or action semantics.
