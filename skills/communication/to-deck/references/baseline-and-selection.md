# Baseline and selection

## Fixed visual-baseline prompt

Send this before the agent sees a template, prior deck, or design candidate:

> Given only the approved Point, audience, venue, language, and slide count, define the minimum complete visual understanding. State the context-free takeaway; Point/model IDs that must be seen; the causal path from input through evaluation and decision to outcome; trust boundaries; what is proved and not proved; the decision or next action; the source project's proper role; likely misconceptions; and cold-read questions with expected answers. Describe meaning, not styling.

Save the prompt, inputs seen, model identity when known, and SHA-256. The visual baseline is a completeness contract, not a slide design.

The JSON contains `must_see` objects with stable IDs plus six ID sets derived from them: `semantic_required_ids`, `gist_required_ids`, `reconstruction_required_ids`, `executive_required_ids`, `headline_required_ids`, and `thumbnail_mechanism_required_ids`. The thumbnail set is the minimum mechanism a reviewer must recover from the reduced render, not merely a promise that the thumbnail was inspected. For a material security boundary, set `security_boundary_required: true` and declare `security_boundary_model_ids` for `role`, `artifact`, `checker`, `decision`, and `failure`. This makes cold-read and boundary checks specific to a flow, architecture, comparison, decision, or timeline instead of forcing one universal template.

## Independent visual-job maps

Give both architects the same Point, baseline, constraints, open component catalog, and anchored rubric. Hide the other branch's visual jobs, component scores, ensemble, and visual grammar. Each branch maps every job to Claim IDs, model node/edge/boundary IDs, must-see IDs, criticality, intended audience, and an expected cold-read answer. Record critical relationships, critical trust boundaries, and explicit distinctions that cannot be merged.

Do not let a shared preprocessor choose the dominant diagram. A and B may identify different applicable component families as long as each considers at least two and preserves all required IDs and distinctions.

## Candidate contract

After component scoring and ensemble validation, each storyboard records:

    candidate_id, visual_grammar, narrative_job, headline,
    dominant_component_id, selected_component_ids,
    visual_grammar_signature, object_map, reading_order,
    support_blocks, omissions, density_risks, accessibility_risks

`object_map` maps every must-see baseline ID to a planned object, selected component, Point Claim IDs, and model IDs. Candidates must differ in dominant family or in at least two material grammar dimensions; color or spacing changes do not count. They are blind to one another and to prior decks.

## Selection map

Record exact hashes for the query, baseline, constraints, rubric, catalog, both visual-job maps, both score matrices, both ensembles, both candidates, component-selection audit, component gate, Point, deck, and render manifest. Include:

- selected_candidate: A, B, or synthesis;
- one coverage row per must-see baseline item;
- strengths and rejected elements from each candidate;
- synthesis instructions when selected;
- selected component IDs and the independently recomputed ensemble score;
- content hierarchy and project-lens share;
- hard checks, critical issues, and scored justification.

The selection fails if either candidate was not independent, the candidates use the same visual grammar, the component audit was not blind, a score lacks evidence, the ensemble contains redundant support, a must-see item lacks a selected visual object, a critical relationship or boundary is lost, the source project displaces the domain, or the chosen diagram is only decorative.

## One-slide information floor

Do not optimize for the fewest words. A one-slide technical explainer must still expose:

- subject, mechanism, and outcome in the headline;
- input/Evidence, evaluator, authenticated result, final decision owner, and allow/deny outcome;
- material actor or trust boundaries from Point; when a security boundary is material, the role, crossing artifact, checker, separate decision owner, and failure outcome must be connected in the visual-object map;
- one proof and one non-proof;
- the decision or next action;
- the source project's role when Point marks it material.

Encode the mechanism in the diagram. Supporting prose adds limits and decisions; it does not restate the diagram. Use no more than three non-diagram support blocks.
