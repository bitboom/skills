# Intel RATS paired To Deck — final review

## Frozen input

- Structured Point projection: `input/to-site.input.json`
- Point SHA-256: `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`
- Context result: `input/point-result.md`

## Delivered decks

| Product | Purpose | PPTX | Slides |
|---|---|---|---:|
| Summary | fast decision model and actor sequence | `final/summary/intel-tdx-attestation-summary.pptx` | 2 |
| Structural | complete reader-facing Point model, source ledger, and proof boundary | `final/structural/intel-tdx-attestation-structural.pptx` | 11 |

## Completeness and coherence

`validate-paired.py` passed with **28 structural coverage rows**:

- 4 material claims
- 6 model nodes, 4 typed edges, and 2 boundaries
- 4 explicit `does_not_prove` limits
- 6 deployment / result-use obligations
- 2 canonical source records

The two-slide summary maps its 9 must-see IDs into the structural deck through `final/summary-structural-crosswalk.json`. The crosswalk preserves five invariants: QGS versus TDQE, PCS versus PCCS, Verifier versus RP/KMS, Evidence versus Result versus action, and failure → `NO KEY`.

## Render and independent-review remediation

Both PPTX artifacts were rendered through LibreOffice to PDF and 180-DPI PNG:

- Summary: 2 PNG slides
- Structural: 11 PNG slides

A fresh-eyes review of the initial render correctly found presentation and semantic defects. The final render incorporates the following corrections:

1. Replaced unsupported alpha-style badge color that rendered as black in PptxGenJS.
2. Replaced the short Slide-5 `infoCard` boxes whose body text overflowed into the footer with compact callouts.
3. Split PoP challenge/response from the post-ALLOW secret channel in the summary sequence and re-spaced the appraise rows.
4. Unified the detailed Evidence route on Structural Slide 5: `TD → QGS → TDQE → QGS → TD → RP/KMS → Verifier`; `E-013` is the explicit RP/KMS → Verifier arrow.
5. Made Structural Slide 7 show a separate `TD / K endpoint`, bidirectional PoP exchange, and one-way `E-018` secret delivery after the RP/KMS allow decision.
6. Restored the Point’s trust-anchor / organizational-policy and attestation-model / appraisal-policy qualifiers, and stated that K/D/E is a symbolic deployment profile.
7. Added obligation owners, corrected the PCCS outage/collateral-revocation wording, moved the final ledger to an Appendix framing, and added exact model locators.
8. Replaced the summary proof/non-proof panels with short-height-safe callouts so their body text is readable.

The final full-size visual QA passed for Summary Slide 1, Structural Slides 2, 5, 7, 8, and 11: no clipping, glyph failure, footer collision, or unresolved actor/connector defect was found.

## Evidence and caveat

- `final/paired-deck-gate.json` is the machine-readable integrity/completeness result.
- `final/structural-coverage-map.json` is the authoritative Point-ID → slide/object trace; Slide 11 is the human appendix.
- `final/output-sha256.txt` pins the generated decks, manifests, coverage artifacts, and report.
- The deck preserves the Point's proof boundary: a valid Quote or Result does **not** by itself prove code correctness, a container/process identity, future-safe behavior, or availability / all side-channel and supply-chain safety.
