# Point prose preservation contract

A structural deck is not a noun-phrase export of Point. It may use diagrams to carry topology, but it must preserve the explanation that lets a reader reconstruct why the topology authorizes an action.

## Canonical input and projection

1. The canonical source is the passed Point package: `point.md`, `point.yaml`, `point.sha256`, and `point-gate.json`. Their hashes must agree.
2. A derivative JSON/YAML projection is allowed only with a projection manifest that records the canonical Point hash and maps every Point claim, node, edge, boundary, context dependency, state, proof/non-proof, caveat, implication, source reference, and qualifier it represents.
3. A projection may accelerate layout but cannot replace `point.md` as the prose source. If it has fewer material IDs than the passed Point package, it is a selective view and must not be used to claim a complete structural deck.
4. If Point markdown, model, and projection disagree about an actor, artifact direction, boundary, or outcome, fail closed and return to Point. Do not silently select the convenient version.
5. The canonical Point model is a typed ledger: node role, edge direction, artifact ownership, state ownership, boundary, proof limit, caveat, and source marker are all semantic facts. A deck must not substitute a more convenient actor, inferred edge, or abbreviated trust claim for them.

## Reading-layer requirements

Every non-appendix structural slide has all of the following.

- **Assertion-led title:** a conclusion with a subject and verb, not an inventory heading.
- **Reader question:** the subtitle answers why the slide exists before it introduces detail.
- **Narrative sentence:** at least one Korean sentence that names the relevant actor, concrete artifact, validation, decision owner, and next action or failure outcome. A diagram label may not satisfy this requirement.
- **Adjacent condition:** the material qualifier, trust assumption, proof limit, or failure condition appears on the same slide as the claim it constrains.
- **Local term onboarding:** at first use, write a short Korean explanation with the stable English term/abbreviation when the reader needs it later.

For a material security boundary, use the sequence:

```text
actor → artifact → check → separate policy owner → action / failure outcome
```

Example:

> Verifier는 Quote와 collateral을 검증해 signed Result를 만든다. RP/KMS는 그 Result의 서명·시간·E/K binding·key possession을 별도로 확인한 뒤, allow일 때만 같은 approved K channel에 secret을 전달한다. replay·expiry·failed PoP는 NO KEY로 끝난다.

## Model-fidelity requirements

- **Ownership is typed:** A rendered claim about creating, signing, issuing, transporting, retaining, consuming, or releasing must name the same owner as the canonical node or typed edge. A convenient simplification such as “TD creates Quote” fails when the model names a different signer.
- **Retained state is not transport:** A retained nonce, expected context, or terminal record must appear as a state owned inside the canonical actor. It must not be drawn or described as a message that leaves that actor.
- **Summary term onboarding:** Before a Summary uses a digest, proof, policy, or state abbreviation to explain a branch, it gives that term a short Korean definition. The Summary route must preserve the canonical producer, signer, transport direction, policy owner, and failure branch.
- **Reader-visible source markers:** The rendered slide must display canonical source markers adjacent to the claim or in a readable footer. If the Point package lacks a bibliographic registry, say that limitation and do not invent citations.

| Allowed label | It must not replace |
|---|---|
| `signed Result` | who signs it, which evidence/policy it identifies, and who consumes it |
| `E-013` | source actor, destination actor, artifact, and why context is retained |
| `K/D/E` | what each digest binds and which comparison protects the release decision |
| `ALLOW` / `NO KEY` | the policy owner and the condition or failure that selects the branch |
| `PCCS cache` | the signature, chain, status, freshness checks and outage/revocation consequence |

## Korean prose checks

- Name the actor with a subject particle when it owns a security-relevant action: `Verifier가`, `RP/KMS가`, `TD가`.
- Keep a condition and its consequence together when separation hides the causal dependency.
- Prefer `RP/KMS가 Result를 확인한 뒤 secret을 공개한다` over `Result-use policy + release`.
- Use English terms only after their Korean role is locally clear; do not stack untranslated noun phrases as the only explanation.
- Avoid a slide whose body can be reconstructed only by already knowing the protocol.

## Required reviews

1. **Prose trace review:** map every full Point claim and its qualifier/proof limit to the slide sentence that carries it. A source-footer, object ID, or diagram label alone is insufficient.
2. **Canonical model fidelity review:** compare every security-relevant rendered statement to canonical node/edge/state ownership and artifact direction. Check that retained state is shown as internal state, failure branches are reader-visible, Summary terms are defined before use, and source markers are readable. Any ownership, direction, or provenance mismatch fails the build.
3. **Projection integrity review:** compare the canonical Point ID inventory with the build input. Fail on omitted material IDs unless the delivery profile is `summary` and the omission is declared.
4. **Regression review:** when a prior deck is structurally correct but prose is hard to understand, require a before/after table for explicit actors, local term definitions, causal sentences, qualifiers, and proof limits.

## Minimum evidence record

Store `prose-trace.json` with:

```json
{
  "canonical_point_sha256": "…",
  "projection_sha256": "…",
  "projection_complete": true,
  "rows": [
    {
      "point_id": "C-004",
      "slide": 8,
      "sentence": "Verifier는 …",
      "qualifier_location": "slide 8 callout",
      "proof_limit_location": "slide 11 comparison"
    }
  ],
  "failures": []
}
```

A structural deck fails if `projection_complete` is false, a material Point ID lacks a reader-visible sentence, or a security-critical relation is present only as a label/legend/footnote.
