# Paired deck delivery modes

A passed Point can need two different presentation products. They share the same frozen Point input and cannot introduce divergent claims, but they optimize for different reader tasks.

| Mode | Reader job | Scope | Normal size | Success criterion |
|---|---|---|---:|---|
| `summary` | understand the Point result and decision model quickly | only the designated must-see result, causal path, proof limit, and action | 1–2 slides | a cold reader reconstructs the core mechanism and policy consequence |
| `structural` | inspect, teach, and navigate all material Point meaning | every material claim, model node/edge/boundary, qualifier, proof/non-proof, decision condition, and cited source reference | as many slides as semantic clusters require | coverage matrix has no unmapped material ID and a reader can trace each path in PPT |
| `paired` | deliver both products together | both contracts below | both outputs | summary is concise; structural deck is complete; crosswalk proves consistency |

Do not make a `summary` deck by shrinking the structural deck. Do not make a `structural` deck by exporting Point prose as slide bullets.

## Summary: one or two slides

The summary deck is a separate visual argument, not a table of contents.

1. Freeze `summary_must_see_ids` from the Point/visual baseline. It includes the domain thesis, main causal path, accountable decision owner, proof limit, and the next action or terminal outcome. Record any material Point IDs deliberately omitted from the summary and why.
2. **One slide:** use one dominant decision/mechanism diagram; the title states the domain result, and a compact proof/non-proof or allow/deny surface states the decision boundary.
3. **Two slides:** slide 1 teaches the result/decision model; slide 2 teaches the minimum mechanism or sequence required to keep the result honest. Do not repeat slide 1 as decorated cards.
4. Make source/project detail supportive only. The summary must keep its headline, causal diagram, proof limit, and decision readable at thumbnail size.
5. Review against `summary_must_see_ids`, not the full Point inventory. A cold reader must answer: what is evaluated, who decides, what result crosses which boundary, what action follows, and what remains unproven.

## Structural: complete Point deck

The structural deck is a navigable visual projection of Point. It must represent all material input in editable PowerPoint objects; a website, notes file, or speaker memory cannot be the only location of required meaning.

### Required inventory and coverage map

Before storyboarding, create `structural-coverage-map.json` from the frozen Point package. It must enumerate every material:

- Claim ID and claim text;
- model node, edge, boundary, state, and decision-condition ID;
- source reference and locator used by the claim;
- qualifier, assumption, threat/trust statement, proof, non-proof, caveat, failure state, developer implication, and executive implication.

Each row maps to at least one slide number and editable object ID, with `coverage_role` of `primary`, `supporting`, `source-footer`, or `appendix`. Every `primary` relationship must be readable in the slide body; sources may be compressed to an appendix only if their linked claim has an on-slide source marker. The gate fails on unmapped material IDs, a source without a consuming claim, or an object that merges a required distinction.

### Structural information architecture

Choose slide boundaries from semantic clusters, not a pre-fixed slide count. A normal technical Point deck uses only the applicable modules below, in the order the reader needs to build the model:

1. domain result, problem, and outcome;
2. terminology and actor/trust boundary map;
3. primary end-to-end causal model;
4. focused protocol/sequence or artifact lineage;
5. evaluation, authenticated Result, and policy/branching decision;
6. proof, non-proof, assumptions, caveats, and failure paths;
7. developer/operational implications;
8. executive decision, ownership, and next action;
9. source and model appendix with claim/source cross-references.

A slide may cover several tightly related IDs, but must preserve actor, artifact, direction, boundary, condition, and outcome distinctions. Prefer a visual model plus a concise reading layer over long prose. Reuse a consistent actor/color/shape legend across slides without relying on color alone.

### Structural review

In addition to normal rendered-slide QA:

- run the full coverage matrix twice: before build from storyboard objects, and after build from inspected PPT object IDs;
- ask a technical reader to locate an arbitrary claim, source, and model edge from the coverage map and reconstruct its local causal path from slides alone;
- test every slide at full size and thumbnail; appendices may be dense but remain legible at the declared full-size font floor;
- verify source-marker, footer, and appendix locators resolve to the same Point source reference;
- reject a deck that is complete only by repeating the same generic cards or by hiding critical proof limits in notes.

## Paired delivery controls

`paired` runs write separate `summary/` and `structural/` PPTX, render manifests, visual models, review files, and reports. A `summary-structural-crosswalk.json` records the shared Point hash; summary must-see IDs; their structural slide/object locations; intentionally summary-only framing; and any exclusions. It fails when the two decks disagree about an actor, artifact, direction, proof/non-proof, decision owner, or release/failure outcome.

Package both decks, both render trails, `structural-coverage-map.json`, and the crosswalk in one review trail. The final report states which product is appropriate for an executive briefing, a technical training session, and detailed design/evidence review.