---
name: to-deck
description: Turn an approved Point into a domain-first, diagram-led presentation by establishing a deck-blind visual baseline, independently scoring meaning-bearing visual components, comparing two distinct storyboards, selecting or synthesizing the stronger visual argument, and testing rendered slides with novice developers and technical executives. Use after Point when a verified technical brief must become a presentation without semantic loss.
---

# To Deck

Make the approved meaning visible. The deck must teach the subject, not narrate the review process or make the source project the hero.

## Start from Point

1. Read references/run-contract.md, references/baseline-and-selection.md, references/component-catalog.md, references/component-selection.md, and references/rubrics.md.
2. Require a passed Point markdown, model, and hashes. Return to Point for missing or disputed meaning; To Deck does not research new claims.
3. Run `scripts/pipeline.py init` and resolve audience, venue, slide count, language, template, accessibility, and prior-deck constraints. Record the production command, source script, and lockfile when the deck is programmatically generated.
4. For a teaching vehicle, keep the domain as title and dominant visual. Limit project assessment to a small supporting lens.

## Establish the visual baseline

Keep the first pass blind to prior decks and templates.

1. **Visual Baseline Architect:** see only Point, audience, venue, and slide count. Save the exact prompt and hash. Define the context-free takeaway, must-see Point/model IDs, causal path, proof/non-proof, decision, project role, exclusions, and cold-read answers. Do not choose styling.
2. **Constraint Mapper:** record template, aspect ratio, font floors, venue, source-footer needs, and known accessibility or brand constraints. A prior deck is recorded but remains hidden until the blind gate finishes.
3. Freeze the open visual-component catalog and anchored scoring rubric for the run. Page numbers, decoration, and backgrounds are never semantic components.
4. **Storyboard A and B:** two independent architects see the same Point, baseline, constraints, catalog, and rubric but not each other. Each independently extracts visual jobs, scores multiple component candidates with evidence, selects one dominant component plus the minimum useful supports, and then creates a storyboard. Their dominant component or visual grammar must materially differ.
5. Run `scripts/pipeline.py component-gate`. Reject stale hashes, unsupported IDs, self-scoring without reasons, collapsed roles or boundaries, broken causal paths, redundant supports, ensembles below 90, and candidates below their component thresholds.
6. **Selection Reviewer:** compare anonymized candidates. Hide names, authors, and author aggregate scores; expose rubric evidence so the reviewer can recompute scores, coverage, redundancy, and semantic fidelity. Select A, B, or an explicit synthesis and record adopted and rejected components.

## Build one visual argument

1. Make one meaning-bearing diagram the dominant composition when the Point is structural. A diagram is not a row of generic cards: it must expose actors, artifact movement, decision gates, direction, and relevant trust boundaries.
2. For a one-slide explainer, preserve this hierarchy: domain takeaway; dominant causal diagram; proof limit and decision/action; small source-project lens only when Point requires it.
3. Use a renderer-backed technical-diagram prototype only after a visual grammar is selected. Archify may implement an architecture, workflow, sequence, data-flow, or lifecycle candidate from a pinned revision, but it never chooses the grammar or substitutes for Point/visual-model/reader gates. Record its typed IR, version/revision, validation/check output, and rendered SVG hash; treat self-contained HTML or raster export as review material, not the final PowerPoint component. Recreate every meaning-bearing final object as editable PowerPoint content and map it to selected IDs. See `references/component-selection.md`.
4. Use the Presentations skill. Keep important objects editable and map them to selected component IDs, visual-baseline IDs, Point Claim IDs, and model IDs. Add no new material claims.
5. Render every slide with `scripts/render_deck.py` at full size and thumbnail size. The helper clears stale render outputs, requires the PPTX/PNG page counts to agree, produces PDF, PNG, extracted text, and a schema-v2 relative-path manifest with renderer and producer provenance. A script-produced deck must include its source hash and includes a lockfile hash when a lockfile governs the build; a manual deck must say so explicitly.
6. Never hand-write a render manifest. Gate the generated manifest, then package and run `scripts/pipeline.py verify-package --archive <zip> --deck <package-relative-deck> --render-manifest <package-relative-manifest> --output <json>`; it clean-extracts the ZIP and revalidates portable render paths and declared producer assets.
7. For a web-adjacent design direction, borrow Anthropic `frontend-design` only as a pinned visual-critique reference: subject/audience/page job, semantic structure, restrained signature, responsive/focus/reduced-motion checks, and screenshot self-critique. It cannot add a claim, relax the evidence model, or replace deck-specific readability, accessibility, and cold-read gates.

## Run isolated reviews

Every review must reference the exact Point, deck, and render-manifest hashes. Reviewers see only their rubric and no peer scores.

1. **Semantic Diagram Reviewer:** verify Point coverage, causal closure, actor separation, direction, boundaries, and proof limits from the rendered slide.
2. **Novice Developer:** see rendered slides only. After 5–10 seconds, hide them and record gist verbatim; after 20–30 seconds, hide them again and record the model reconstruction verbatim. A separate matcher maps answers to baseline IDs.
3. **Technical Executive:** see rendered slides only and state the baseline-defined capability, value, trust limitation, accountable owner, and next action in raw answers.
4. **Technical Writer:** reject meta-evaluation headlines, unexplained critical terms, vague labels, and compression that removes the mental model.
5. **Render QA:** inspect every slide individually for hierarchy, font floors, title wrapping, contrast, overlap, clipping, glyphs, sources, and reading order. Record the exact rendered-slide hashes, raw thumbnail gist plus required mechanism answers, all bug-hunt checks, review pass number, and reviewer provenance. A new deck needs a render → fix → verify cycle (`review_pass >= 2`); a reviewer sharing the author’s model/provider must explicitly document a separate session.
6. Run `scripts/pipeline.py slide-gate`. Component scores are only pre-build evidence; they never replace these cold-read and rendered-slide gates. On failure, create the next immutable round and repeat component selection, candidate comparison, and all reviews. Never lower thresholds; stop after four failed rounds.

After a blind gate passes, compare with any prior deck. Require improvement on every recorded user-rejected dimension and no accuracy, readability, or scanability regression.

## Freeze and deliver

Run freeze, write final/final-report.md, then manifest and package. Deliver the PPTX, report, and review trail. If slide work exposes missing meaning, return to Point.
