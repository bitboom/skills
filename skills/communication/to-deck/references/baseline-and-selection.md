# Baseline and selection

## Fixed visual-baseline prompt

Send this before the agent sees a template, prior deck, or design candidate:

> Given only the approved Point, audience, venue, language, and slide count, define the minimum complete visual understanding. State the context-free takeaway; Point/model IDs that must be seen; the causal path from input through evaluation and decision to outcome; trust boundaries; what is proved and not proved; the decision or next action; the source project's proper role; likely misconceptions; and cold-read questions with expected answers. Describe meaning, not styling.

Save the prompt, inputs seen, model identity when known, and SHA-256. The visual baseline is a completeness contract, not a slide design.

The JSON contains `must_see` objects with stable IDs plus five ID sets derived from them: `semantic_required_ids`, `gist_required_ids`, `reconstruction_required_ids`, `executive_required_ids`, and `headline_required_ids`. This makes cold-read checks specific to a flow, architecture, comparison, decision, or timeline instead of forcing one universal template.

## Candidate contract

Each storyboard records:

    candidate_id, visual_grammar, narrative_job, headline,
    dominant_visual, object_map, reading_order, support_blocks,
    omissions, density_risks, accessibility_risks

`object_map` maps every must-see baseline ID to a planned object and Point/model IDs. Candidates must differ in visual grammar, not merely color or spacing. They are blind to one another and to prior decks.

## Selection map

Record exact hashes for the query, baseline, constraints, candidates, Point, deck, and render manifest. Include:

- selected_candidate: A, B, or synthesis;
- one coverage row per must-see baseline item;
- strengths and rejected elements from each candidate;
- synthesis instructions when selected;
- content hierarchy and project-lens share;
- hard checks, critical issues, and scored justification.

The selection fails if either candidate was not independent, the candidates use the same visual grammar, a must-see item lacks a selected visual object, the source project displaces the domain, or the chosen diagram is only decorative.

## One-slide information floor

Do not optimize for the fewest words. A one-slide technical explainer must still expose:

- subject, mechanism, and outcome in the headline;
- input/Evidence, evaluator, authenticated result, final decision owner, and allow/deny outcome;
- material actor or trust boundaries from Point;
- one proof and one non-proof;
- the decision or next action;
- the source project's role when Point marks it material.

Encode the mechanism in the diagram. Supporting prose adds limits and decisions; it does not restate the diagram. Use no more than three non-diagram support blocks.
