---
name: to-deck
description: Turn an approved Point into a domain-first, diagram-led presentation by establishing a deck-blind visual baseline, comparing two independent storyboards, selecting or synthesizing the stronger visual argument, and testing the rendered slides with novice developers and technical executives. Use after Point when a verified technical brief must become a presentation without semantic loss.
---

# To Deck

Make the approved meaning visible. The deck must teach the subject, not narrate the review process or make the source project the hero.

## Start from Point

1. Read references/run-contract.md, references/baseline-and-selection.md, and references/rubrics.md.
2. Require a passed Point markdown, model, and hashes. Return to Point for missing or disputed meaning; To Deck does not research new claims.
3. Run scripts/pipeline.py init and resolve audience, venue, slide count, language, template, accessibility, and prior-deck constraints.
4. For a teaching vehicle, keep the domain as title and dominant visual. Limit project assessment to a small supporting lens.

## Establish the visual baseline

Keep the first pass blind to prior decks and templates.

1. **Visual Baseline Architect:** see only Point, audience, venue, and slide count. Save the exact prompt and hash. Define the context-free takeaway, must-see Point/model IDs, causal path, proof/non-proof, decision, project role, exclusions, and cold-read answers. Do not choose styling.
2. **Constraint Mapper:** record template, aspect ratio, font floors, venue, source-footer needs, and known accessibility or brand constraints. A prior deck is recorded but remains hidden until the blind gate finishes.
3. **Storyboard A and B:** two independent architects see the same Point, baseline, and constraints but not each other. They must use materially different visual grammars and each map every baseline item to a planned visual object.
4. **Selection Reviewer:** compare anonymized candidates without author or score context. Select A, B, or a specified synthesis; record coverage, trade-offs, rejected elements, and the chosen visual-object map.

## Build one visual argument

1. Make one meaning-bearing diagram the dominant composition when the Point is structural. A diagram is not a row of generic cards: it must expose actors, artifact movement, decision gates, direction, and relevant trust boundaries.
2. For a one-slide explainer, preserve this hierarchy: domain takeaway; dominant causal diagram; proof limit and decision/action; small source-project lens only when Point requires it.
3. Use the Presentations skill. Keep important objects editable and map them to Point/model IDs. Add no new material claims.
4. Render every slide at full size and thumbnail size; run structural checks before review.

## Run isolated reviews

Every review must reference the exact Point, deck, and render-manifest hashes. Reviewers see only their rubric and no peer scores.

1. **Semantic Diagram Reviewer:** verify Point coverage, causal closure, actor separation, direction, boundaries, and proof limits from the rendered slide.
2. **Novice Developer:** see rendered slides only. After 5–10 seconds, hide them and record gist verbatim; after 20–30 seconds, hide them again and record the model reconstruction verbatim. A separate matcher maps answers to baseline IDs.
3. **Technical Executive:** see rendered slides only and state the baseline-defined capability, value, trust limitation, accountable owner, and next action in raw answers.
4. **Technical Writer:** reject meta-evaluation headlines, unexplained critical terms, vague labels, and compression that removes the mental model.
5. **Render QA:** inspect every slide individually for hierarchy, font floors, title wrapping, contrast, overlap, clipping, glyphs, sources, and reading order. Clean rendering cannot compensate for missing meaning.
6. Run scripts/pipeline.py slide-gate. On failure, create the next immutable round and repeat candidate comparison and all reviews. Never lower thresholds; stop after four failed rounds.

After a blind gate passes, compare with any prior deck. Require improvement on every recorded user-rejected dimension and no accuracy, readability, or scanability regression.

## Freeze and deliver

Run freeze, write final/final-report.md, then manifest and package. Deliver the PPTX, report, and review trail. If slide work exposes missing meaning, return to Point.
