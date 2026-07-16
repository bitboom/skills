# Roles and rubrics

## Role isolation

| Role | Sees | Must not see |
|---|---|---|
| Model-Prior Agent | Topic, audiences, scope | Source or project |
| Domain Baseline Agent | Prior, authoritative sources | Source or project |
| Source Mapper | Source or project | Prior and baseline |
| Coverage Synthesizer | Both blind candidates | Other scores |
| Reviewers | Current final artifacts and assigned evidence | Author self-score and peer scores |
| Language Prose Reviewer | Locked draft, model, citation ledger, language brief | Author self-score and peer scores |

Use the strongest current reasoning model available for the prior. Record the model when known. Its output is still only a coverage hypothesis.

## Hard gates

- Every critical claim, node, edge, and boundary is checked against authoritative evidence.
- Every context dependency has a modeled source and consumer. For security or protocol topics, a reviewer must reject freshness, identity, or binding claims when the expected context reaches only one side of the comparison.
- Every decision-bearing result that crosses a trust boundary is authenticated and bound to its intended audience, request, subject, and validity window when the domain requires it. Do not hide these links as implied out-of-band behavior.
- Security topics state attacker capabilities, trusted roots and policy components, authenticity guarantees, and availability limits. Components with different trust semantics remain separate nodes or have an explicit internal boundary.
- When an action depends on a decision result, the result identifies its verdict, relevant policy/version, Evidence or subject, and any approved key or channel binding needed by the consumer. Treat domain-specific fields as an explicit profile, not a universal standard unless a source says so.
- Every baseline critical essential is present in the final; at least two source-specific insights are used.
- The final explains the problem, actors, evidence-to-decision flow, proof, non-proof, policy/action, and why the source adds value.
- Domain core occupies at least half; assessment does not exceed one fifth or lead the narrative.
- A novice developer can explain the central concept without the project name and can teach back Quote/evidence as input rather than authorization.
- A technical executive can state capability, value, principal trust limitation, accountable decision, and next action.
- The one-line Point names the domain, mechanism, and outcome without relying on unexplained project jargon.
- Terms are interpretable, essentials and exclusions are explicit, and fact corrections do not displace teaching.
- The prose review preserves every claim ID, citation, qualifier, actor, boundary, and proof limit. It improves reader fit by making terms local, actions explicit, causal links visible, and each paragraph answer one reader question.

## Point score

Score each criterion from 1 to 5. Every score must be at least 4 and the weighted total at least 90.

| Review | Criterion | Weight |
|---|---|---:|
| Domain | conceptual_coverage | 20 |
| Domain | structural_completeness | 15 |
| Reader | audience_comprehension | 15 |
| Reader | mental_model_clarity | 15 |
| Reader | one_line_clarity | 10 |
| Writer | logical_coherence | 10 |
| Writer | unambiguity | 10 |
| Writer | compression_without_loss | 5 |

## Synthesis score

domain_baseline_coverage weighs 40, project_relevance 30, and synthesis_gain 30. Every score must be at least 4 and the normalized total at least 90.

When executive review is required, decision_relevance and so_what_clarity must each be at least 4, normalized total at least 90, and critical questions empty.

## Prose score

Score reader_fit, terminology_onboarding, causal_cohesion, and concision_without_loss from 1 to 5. Every score must be at least 4 and the normalized total at least 90. The prose reviewer is not an evidence authority: it must flag, not repair from memory, a claim whose natural rewrite would need new factual content.

## Cold-read questions

The novice answers: What problem exists? Who creates and checks what? What happens next? What does the evidence prove and not prove? Why is this project useful?

The executive answers: What capability does this enable? What decision follows? What is the trust limit or failure risk? Who owns the policy? What should happen next?

When a prior output exists, compare blind: final novice clarity and executive usefulness must not be below the domain baseline, and final project fidelity must not be below the source model.
