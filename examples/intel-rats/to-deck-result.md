# Accepted Intel-rats To Deck result

The replacement deck explains Intel TDX remote attestation as a release-control path:

    challenge binding → TD/QGS/TDQE Evidence generation
    → Verifier evaluation and signed Result
    → RP/KMS release policy → allow once or no key

## Visual Component Selection

- Candidate A dominant grammar: causal pipeline
- Candidate B dominant grammar: trust-boundary and data-flow diagram
- Selected ensemble: `A-DOM` + `A-PROOF` + `A-ACTION`
- Component ensemble score: 98/100
- Must-see coverage: 10/10
- Preserved distinctions: QGS/TDQE, PCS/PCCS, Verifier/RP, Evidence/Result, Result/action, proof/non-proof, allow/non-allow

## Final slide gate

- Slide score: 94/100
- Every criterion: at least 4/5
- Semantic visual share: 0.5946 of the core region
- Render hard checks: 17/17 at zero
- Structural PPTX test: passed with no overflow
- Regression: improved every user-rejected dimension with no accuracy, readability, or scanability regression

The slide keeps Intel-rats secondary to the domain explanation. It is presented as a learning and design-review lens, not deployable Quote-verification code.

See [`final-deck.pptx`](final-deck.pptx) and the complete immutable [`review-trail.zip`](review-trail.zip).
