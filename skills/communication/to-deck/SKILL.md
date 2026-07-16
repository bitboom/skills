---
name: to-deck
description: Turn an approved Point content package into an evidence-traceable presentation through information architecture, meaning-bearing diagrams, audience cold reads, rubric gates, rendered-slide review, and a versioned audit trail. Use after Point when a verified technical summary must become a deck.
---

# To Deck

Translate a passed Point into visual understanding. Preserve its meaning while making the mechanism, relationships, and decision visible at first glance.

## Require Point

1. Read references/run-contract.md and references/rubrics.md.
2. Accept final/point.md, final/point.yaml, and point.sha256 from a passed Point run.
3. If Point is missing, incomplete, or semantically disputed, invoke Point first. Do not research or repair claims inside To Deck.
4. Create a new run with scripts/pipeline.py init, which copies and hashes the Point input.
5. Resolve slide count, format, audience, venue, language, visual constraints, and whether an earlier deck is a regression baseline.

## Build the visual argument

For each immutable round:

1. **Information Architect:** map Point's title, one-line point, model, essentials, implications, caveats, and action to a storyboard. Choose the smallest useful visual form: flow, architecture, comparison, timeline, or decision structure.
2. **Slide Designer:** make the meaning-bearing diagram the dominant object when the Point has three or more actors/stages or two or more relationships. Text cards may support the model but cannot replace it.
3. **Presentation Builder:** build the deck using the presentation skill. Map important objects to Point claim or model IDs and add no new material claims.
4. Render every slide at full size and run structural checks before review.

## Run independent reviews

Reviewers receive the Point input, current deck, rendered slides, storyboard, rubric, and source map. Hide author self-scores and prior numeric scores.

1. **Diagram Verifier:** check node, edge, direction, boundary, label, and Point coverage.
2. **Target Reader:** perform a ten-second cold read, paraphrase the headline, and identify input, decision maker, action, and outcome.
3. **Technical Executive:** test first-glance so-what, decision relevance, risk, and next action.
4. **Visual QA:** inspect hierarchy, density, contrast, rendering, sources, and object traceability. Visual QA cannot overrule a failed semantic or reader gate.
5. **Independent Gatekeeper:** run scripts/pipeline.py slide-gate and record accepted, rejected, and deferred findings in slides/vNN-decision.md.

If the gate fails, create the next slide version and repeat all reviews. If a fix needs new meaning, return to Point. Stop after four failed rounds; never lower the threshold.

When a previous artifact exists, review the current deck blind first, then require a baseline comparison. Fail if mental-model reconstruction, scanability, or information coverage regresses.

## Finish with evidence

Only after the Slide Gate passes:

1. Copy the passing deck to final/final-deck.pptx.
2. Write final/final-report.md with scores, input Point hashes, non-blocking caveats, and baseline result.
3. Run manifest and package.
4. Deliver the deck, report, and review trail.

Fresh command output is required before claiming a gate passed, a slide rendered correctly, or the run completed.
