# Gates

## Visual component gate

Before storyboard selection, require both blind architects to pass the artifact-bound component gate described in `component-selection.md`.

- Every visual job links valid Claim, model, and baseline IDs and states criticality, audience, expected cold-read answer, and required distinctions.
- Every component criterion uses an anchored 1–5 score with a non-empty justification. Recompute the weighted score; reject declared totals that differ.
- Dominant components require at least 80/100. Supporting components require at least 70/100 and must add a previously uncovered must-see ID.
- Any semantic distortion, collapsed role or boundary, broken causal direction, broken Evidence→evaluation→authenticated Result→policy action path, proof/non-proof confusion, project-first framing, decorative card listing, unreadable composition, color-only encoding, or new material claim makes the component ineligible regardless of score.
- Each ensemble contains exactly one dominant component and at most three supports. Apply five redundancy points for every duplicate baseline assignment, capped at twenty. Require every ensemble criterion at least 4/5, total at least 90/100, all five baseline-required sets fully covered, zero missing critical relationships/boundaries/distinctions, zero hard failures, and zero unnecessary components.
- If all applicable standard dominant candidates are ineligible, require an eligible `custom-domain-diagram` and record the fallback reason.
- Require A/B visual grammars to differ materially. The anonymized Selection Reviewer independently recomputes component and ensemble scores before selecting A, B, or an explicit synthesis.

Component scores are pre-build evidence only. They never replace the following slide gate.

## Slide gate

## Hard gates

- Visual query, baseline, candidates, selection, reviews, deck, and render manifest have matching hashes.
- Two independent, materially different storyboards were compared; every visual-baseline must-see item maps to the selected design.
- A structural Point has one dominant meaning-bearing diagram occupying at least 55% of the core content region.
- The diagram exposes the causal path from input/Evidence through evaluation and authenticated Result to final policy action. Distinct trust roles are not collapsed.
- Required nodes, edges, boundaries, direction, proof, non-proof, decision owner, and allow/deny outcome are visible and checked.
- A novice developer recovers every baseline gist ID after a 5–10 second exposure and every reconstruction ID after a 20–30 second exposure. Raw answers precede matching.
- A technical executive recovers every baseline executive ID from raw answers.
- The headline is domain-first, plain-language, assertion-led, and recovers every baseline headline ID. Review-process or audit language is absent from audience-facing copy.
- No unexplained critical term remains; no more than three non-diagram support blocks are used.
- Full-size and thumbnail renders were inspected; raw thumbnail gist and mechanism answers recover the declared thumbnail baseline IDs; rendered-slide hashes match the manifest; all bug-hunt checks completed; visual QA includes a render → fix → verify cycle; every render hard check is zero.
- Render manifest is schema v2: all slide paths are relative, symlink-confined to the manifest directory after clean extraction, match image hashes and PNG dimensions, and declare renderer/toolchain plus manual-or-script producer provenance. A declared script source or lockfile must be included and hash-valid; schema-v1 trails are rebuilt rather than grandfathered.
- The visual model contains a distinct, direction-declared producer → checker → consumer trace with declared connector paths. For a required security boundary it also maps every expected role → artifact → checker → separate decision → failure model ID and connects role → checker → decision → failure through declared connector paths.
- A prior-deck comparison, when required, occurs only after blind review and improves every recorded user-rejected dimension without accuracy, readability, or scanability regression.

## Scored gate

Score every criterion from 1 to 5. Any score below 4 fails; weighted total must be at least 90.

| Review | Criterion | Weight |
|---|---|---:|
| Selection | visual_baseline_coverage | 10 |
| Selection | candidate_comparison_quality | 5 |
| Semantic | point_coverage | 15 |
| Semantic | causal_structure_visibility | 15 |
| Semantic | diagram_accuracy | 10 |
| Reader | novice_comprehension | 15 |
| Executive | executive_takeaway | 10 |
| Writer | headline_clarity | 10 |
| Visual QA | hierarchy | 5 |
| Visual QA | render_qa | 5 |

Render hard checks are semantic_drift, overflow, unintended_overlap, clipping, broken_or_unreadable_text, diagram_direction_errors, missing_material_sources, title_wrap, body_below_16pt, midlevel_below_24pt, slide_title_below_35pt, unsupported_glyphs, critical_contrast_failure, font_substitution, color_only_encoding, missing_alt_text, and invalid_reading_order. Each must equal zero.
