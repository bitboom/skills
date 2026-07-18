# Intel RATS full-Point prose v3 — review trail

## Canonical source

- `input/point.md` and `input/point.yaml`
- passed Point gate: round 4, score 92
- SHA-256: `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`

## Why v3 exists

The first independent full-Point review found semantic loss despite clean rendering: Quote producer/transport ambiguity, a retained-context direction error, incomplete trust and profile qualifiers, and compressed proof/pilot/source language. v3 makes those facts reader-visible and adds PPTX-text regression checks.

## Contract and deliverables

- To Deck contract now requires canonical ownership, retained internal state, Summary term onboarding, reader-visible source markers, and a canonical-model review.
- Summary: `summary/intel-tdx-attestation-prose-summary.pptx` (2 slides).
- Structural: `structural/intel-tdx-attestation-prose-structural.pptx` (16 slides).
- `prose-trace.json`: 10 Point claims mapped to visible Korean sentences.
- `structural-coverage-map.json`: 88 / 88 canonical material IDs.
- `summary-structural-crosswalk.json`: shared invariants.

## Current verification evidence

```text
To Deck tests: 24 / 24 passed
npm run build: passed
npm run validate: passed
semantic gate: 2 summary + 16 structural PPTX slides; no ownership/state/source failures
renders: 2 / 2 summary and 16 / 16 structural PNG pages
full-size visual QA: Summary 1–2; Structural 2, 4–9, 11–12, 14–16
```

The visual QA specifically checked the TDQE/QGS and PCS/PCCS distinctions, Verifier-owned retained context, signed Result vs release, visible ALLOW/NO KEY branches, proof limits, Intel-rats caveat, pilot gates, and source-map appendix.

## Independent acceptance

A read-only fresh-eyes reviewer compared canonical `point.md`/`point.yaml` to the actual PPTX text and all 18 rendered PNGs. **PASS**: the reviewer confirmed all ten required categories—ownership/transport, retained state, closed release/failure path, K/D/E profile, trust/DoS, proof limits, Intel-rats/RFC caveat, SGX-vs-TDX boundary, pilot ownership/gates, and Korean/source-marker legibility. No files were changed by the reviewer.

## Scope caveat

Intel-rats remains a teaching and design-review lens. It is not a deployable verifier baseline or proof of production approval.
