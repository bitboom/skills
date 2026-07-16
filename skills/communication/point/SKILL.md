---
name: point
description: Turn a technical repository, document, or source set into a domain-first, evidence-backed teaching brief by independently generating the ideal domain explanation, mapping what the source teaches, comparing both, and synthesizing the strongest content for novice developers and technical executives. Use for technical summaries, project explainers, explain-then-assess briefs, and verified semantic input for To Deck.
---

# Point

Teach the subject the source exists to explain. For educational projects, make the domain—not the repository—the headline.

## Start the run

1. Read references/run-contract.md, references/baseline-and-synthesis.md, references/roles-and-rubrics.md, and references/korean-technical-prose.md when the deliverable is Korean.
2. Create an immutable run with scripts/pipeline.py init.
3. Resolve canonical_topic and project_role: primary_subject, teaching_vehicle, implementation, or case_study.
4. Use domain_through_project by default when a repository is documentation, a visual explainer, tutorial, or educational project. Target roughly 60% domain core, 25% project lens, and 15% caveat; never let assessment lead.

## Build two blind candidates

Keep these lanes isolated. Record the exact prompts, inputs seen, model identity when known, and hashes.

1. **Model-Prior Agent:** use the strongest current reasoning model available. Give it only the canonical topic and audiences, never the project. Save the exact prompt in 01-domain-query.md and candidate coverage in 02-model-prior.json. This is a coverage hypothesis, never evidence.
2. **Domain Baseline Agent:** still blind to the project, verify and correct the prior with primary or authoritative sources. Save the minimum complete teaching model in 03-domain-baseline.json and its fact review.
3. **Source Mapper:** read only the repository or source set, not the prior or baseline. Extract declared purpose, taught concepts, flow, unique teaching value, omissions, and conflicts into 04-source-model.json.

## Compare before writing

1. **Coverage Synthesizer:** see both candidates for the first time. Classify every baseline essential and source insight as aligned, missing, conflict, or source addition; select must, should, or exclude with reasons.
2. Save the comparison and adoption decisions in rounds/vNN-synthesis-map.json.
3. Draft domain first: one-line domain definition; problem; actors and five-to-seven-step mechanism; what it proves and does not prove; source-specific teaching value; developer implications; executive implications; concise caveats.
4. Give claims C-NNN IDs and model nodes, edges, and boundaries stable IDs. Do not design slides.
5. Lock the semantic draft before prose work. The prose pass may rearrange sentences, split or merge paragraphs, define a term locally, and remove repetition, but it must preserve every claim ID, citation, qualifier, actor, boundary, condition, and proof limit.

## Run independent reviews

Give each reviewer the brief, current artifacts, source ledger, and only its rubric. Hide author self-scores and other reviewers' scores.

1. **Evidence Auditor:** verify every critical claim and model relationship. The model prior cannot be cited.
2. **Domain Reviewer:** check the problem, threat/trust model, actors, mechanism, proof limits, policy decision, and operational meaning. For protocols and security flows, require explicit adversary capabilities and trust assumptions; do not combine components whose compromise has different authenticity or availability effects. Reject expected context that does not reach both producer and checker, and reject a decision-bearing result that crosses a trust boundary without authentication, audience/request binding, and enough Evidence/policy identity to justify the action.
3. **Novice Developer:** cold-read and teach back the problem, flow, proof, non-proof, and why the project helps.
4. **Technical Executive:** state capability, value, trust limitation, decision owner, and next action.
5. **Technical Writer:** check logic, ambiguity, terminology, and compression without deleting the teaching model.
6. **Language Prose Reviewer:** review the locked draft in the deliverable language. Check reader fit, term onboarding, causal cohesion, and concision without loss. For Korean, reject literal translation, stacked noun phrases that hide the actor or action, unexplained English terms, and a paragraph that answers more than one reader question. Save `vNN-prose-review.json` with the exact artifact/model hashes and the hard checks in `references/korean-technical-prose.md`.
7. After any rewrite, rerun evidence review and the prose review on the exact artifacts.

Run scripts/pipeline.py point-gate. On failure, create the next round and repeat comparison, synthesis, and all reviews. Never overwrite a round or lower thresholds. Stop after four failures.

## Freeze and hand off

When the gate passes, run freeze, write final/final-report.md, then run manifest and package. Deliver Point for approval; invoke To Deck only after approval or an explicit end-to-end request.

Point owns domain completeness, source relevance, and semantic correctness. To Deck owns visual explanation. Return to Point if slide work exposes missing meaning.
