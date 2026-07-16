# Baseline and synthesis

## Fixed independent prompt

Save and send this prompt before the model sees the source:

> You know only the domain topic, not the repository or document. For a novice developer and a technical executive, identify the minimum complete mental model: what problem exists, what the technology is, actors and end-to-end mechanism, what it proves and does not prove, decisions enabled, operational value, trust assumptions, common misconceptions, and the five questions a good explanation must answer. Return candidate coverage, not factual authority.

Add the canonical topic, audiences, language, and requested scope. Do not add project conclusions.

## Domain baseline JSON

Required fields: topic, project_context_seen=false, audience_questions, problem, one_line, actors, flow, proves, does_not_prove, critical_essentials, common_misconceptions, decision_value, glossary, and source_ids. Every critical_essentials item has a stable id, novice_value, executive_value, and authoritative source_ids.

## Source model JSON

Required fields: source_identity, baseline_context_seen=false, declared_purpose, taught_concepts, flow, project_insights, omissions, conflicts, and source_ids. Every project_insights item has a stable id and explains why this source is useful beyond a generic domain summary.

## Synthesis map JSON

Record hashes for the prior, baseline, source model, final text, and final model. Include one row per baseline essential and selected source insight:

    concept_id, concept, relationship, selection, selected_from,
    audience_value, source_ids, reason, final_ids, resolution

Allowed relationship values are aligned, missing, conflict, and source_addition. Allowed selections are must, should, and exclude. A conflict requires a resolution. A must item requires final_ids.

Allowed selected_from values are baseline, source, and both.

Also record scores, content_balance, hard_checks, critical_issues, and issues using the run contract.

Record a blind comparison with baseline_strengths_adopted and source_strengths_adopted. The final must be at least as complete as the authoritative domain baseline and at least as faithful to the project as the source model; it must improve on either candidate by joining domain explanation to source-specific value.

## Synthesis rules

- Treat the model prior as a question generator, never a source.
- Close every causal dependency. If a verifier compares an expected value, model how it receives or retains that value. If a decision maker consumes a result across a trust boundary, model how that result is authenticated and bound.
- Cover every baseline critical essential or fail. Do not silently compress it away.
- Use at least two source-specific insights and state why the project is useful beyond a generic explanation.
- For a teaching_vehicle, name the domain in the title and first line; introduce the project after the domain mechanism is clear.
- Keep corrections and readiness judgments after the explanation and at no more than 20% of the content.
- Prefer causal explanation over term lists: problem → evidence → verification → result → policy decision → action.
- Reject details that are accurate but irrelevant to the approved audience or communication job; record the reason.
