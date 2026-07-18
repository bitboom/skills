# Intel RATS full-Point prose v2 — final review

## Purpose

This round corrects the earlier deck's source drift: the old build read a selective four-claim projection, while this round reads the passed canonical Point directly.

## Canonical input

- Point: `input/point.md`
- Model: `input/point.yaml`
- Gate: `input/point-gate.json` (`round: 4`, `score: 92`, `passed: true`)
- SHA-256: `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`

## Improved To Deck contract exercised

1. A selective projection cannot replace canonical `point.md` as prose source.
2. `prose-trace.json` maps every Point claim to a visible Korean reader sentence.
3. Each security relation retains actor → artifact → check → policy owner → action/failure semantics.
4. A structural build fails if it omits canonical claims, model material, proof/non-proof entries, implications, caveats, exclusions, or source IDs.

## Deliverables

| Product | Output | Scope |
|---|---|---|
| Summary | `summary/intel-tdx-attestation-prose-summary.pptx` | 2-slide release-control story |
| Structural | `structural/intel-tdx-attestation-prose-structural.pptx` | 15-slide complete Point explanation |
| Coverage | `structural-coverage-map.json` | 88 canonical material IDs mapped |
| Prose trace | `prose-trace.json` | 10 Point claims with reader-visible Korean sentences |
| Crosswalk | `summary-structural-crosswalk.json` | shared summary/structural invariants |

## Verification

```text
npm run build: passed
npm run validate: passed
canonical Point hash: matched
summary render: 2 / 2 PNG pages
structural render: 15 / 15 PNG pages
visual QA: full-size inspections of Summary 1–2 and Structural 4, 8, 9, 11, 12, 14, 15
```

The final full-size QA found and corrected one compressed proof-boundary sentence and one overly long pilot release-gate sentence. No clipping, actor-direction contradiction, or Key-release / Result ownership contradiction remained in the inspected final renders.

## Portable review package

- Archive: `final/intel-rats-prose-v2-review-trail.zip`
- SHA-256: delivered separately so the archive does not contain a self-referential hash
- Package-render-manifest gate: passed; delivery report records the generated gate JSON outside the archive

## Caveat

This deck explains the passed Point and retains its stated scope: Intel-rats is a teaching/design-review lens, not a deployable verifier baseline or production approval.
