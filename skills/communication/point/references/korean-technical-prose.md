# Korean technical prose pass

Use this pass after the semantic Point draft is locked and before the final Point gate. Its job is not to make a security or protocol document informal. Its job is to reduce reader effort while preserving the exact claim, evidence, condition, boundary, and proof-limit model.

## Input and output

Inputs:

- locked Point markdown and model
- claim IDs, citation ledger, source qualifiers, and language brief
- target reader's prior knowledge and decision

Output: `rounds/vNN-prose-review.json`. It must bind to the exact `point.md` and `point.yaml` hashes.

```json
{
  "round": 1,
  "artifact_sha256": "<point.md sha256>",
  "model_sha256": "<point.yaml sha256>",
  "language": "ko-KR",
  "scores": {
    "reader_fit": 5,
    "terminology_onboarding": 5,
    "causal_cohesion": 5,
    "concision_without_loss": 5
  },
  "hard_checks": {
    "claim_ids_preserved": true,
    "citations_and_qualifiers_preserved": true,
    "critical_terms_defined_or_known": true,
    "actors_and_actions_explicit": true,
    "paragraphs_answer_one_reader_question": true,
    "language_is_natural_for_audience": true,
    "unresolved_literal_translation_count": 0
  },
  "critical_issues": [],
  "issues": []
}
```

## Procedure

1. **Build a reader map.** Record what the target reader already knows, the decision they must make, and the five questions the text must answer. Do not simplify a specialist term that the reader already needs; define it at first use instead.
2. **Make the causal chain visible.** Prefer actor → artifact → check → policy → action. State which component acts and what it consumes. Do not hide a trust or decision boundary in a noun phrase.
3. **Introduce terms locally.** At first use, write a short Korean explanation and the stable English term or abbreviation when it is needed later. Use one term consistently after that. A gloss must not substitute for the normative definition in a cited source.
4. **Reduce sentence load.** Keep one main action or claim per sentence. Split only when the sentence carries independent actions, conditions, or proof limits. Keep a causal pair together when splitting would hide the dependency.
5. **Give each paragraph one reader job.** A paragraph may answer what the component does, what it proves, what it does not prove, or what decision follows. Use a table only for a stable comparison and a list only for items that are genuinely parallel.
6. **Remove repetition, not constraints.** Delete duplicated introductions, vague signposting, and prose that restates a heading. Retain source qualifiers, conditions, exceptions, cardinality, policy/version identity, and every claim ID.
7. **Read for Korean naturalness.** Reject literal translation, stacked modifiers that conceal the subject or verb, unexplained English, and generic abstract nouns when a concrete actor or artifact is available. Do not add conversational voice, opinions, or unsupported analogies.
8. **Run the semantic diff.** Check that the claim-ID set, citation set, model nodes/edges/boundaries, and stated proof limits match the locked draft. If a natural rewrite needs new factual content, return it to the evidence author rather than guessing.

## Scoring rubric

| Criterion | 5 | 4 | Fail |
|---|---|---|---|
| Reader fit | A target reader can state the problem, flow, proof limit, and decision without translation work. | One minor clarification is needed. | The reader must infer a key role, action, or purpose. |
| Terminology onboarding | Every critical term is defined or explicitly treated as known; usage is stable. | One noncritical term is late or slightly inconsistent. | A critical term is unexplained or changes meaning. |
| Causal cohesion | Actors, artifacts, checks, policies, and actions are explicit in the required order. | One noncritical transition is implicit. | A trust, evidence, or decision dependency is hidden. |
| Concision without loss | Repetition and avoidable density are removed without deleting conditions or limits. | A small amount of removable wording remains. | Compression weakens a claim, omits a qualifier, or makes the model vague. |

## Korean checks

- Prefer an explicit agent and verb: `Verifier가 Quote를 검증한다` over an agentless passive construction when the actor matters.
- Introduce a term once: `증거(Evidence)` or `증거 평가자(Verifier)`, then keep that spelling.
- Replace vague abstractions with the object or action that carries the meaning. `신뢰 경계가 유지된다` is weaker than the checks that prevent an untrusted path from authorizing release.
- Preserve deliberate technical precision. `단일 사용 상태 전이`, `정책 버전`, `proof of possession` and similar terms should be explained, not erased.
- Do not mechanically shorten every sentence. A sentence that states a necessary condition and its consequence may remain long when splitting obscures the relation.

## Evidence basis

- Google Technical Writing One: audience, clear sentences, short sentences, lists/tables, paragraphs, and document design. https://developers.google.com/tech-writing/one
- Microsoft Writing Style Guide: simple, straightforward, scannable technical communication. https://learn.microsoft.com/en-us/style-guide/welcome/
- Hotaling (2020), concise scientific writing requires a dedicated revision pass. https://doi.org/10.1002/lol2.10165
- Kendeou and van den Broek (2007), prior knowledge and text structure affect comprehension of scientific texts. https://doi.org/10.3758/BF03193491
- Reynolds and Thompson (2011), structured scientific peer review improved student thesis writing. https://doi.org/10.1187/cbe.10-10-0127
- Paper Plain (2022), local definitions, plain-language summaries, and question-guided navigation made research papers easier to read without a comprehension loss in its study. https://arxiv.org/abs/2203.00130

These sources motivate the workflow. They do not justify removing evidence, conditions, or technical qualifiers from a security or protocol document.
