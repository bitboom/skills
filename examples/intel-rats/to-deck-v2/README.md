# Intel RATS — To Deck final v2

**Source of truth:** the passed Intel RATS Point package, hash `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`.

## Deliverable

- `final/intel-tdx-attestation-v2.pptx` — two editable native PowerPoint slides.
  1. Evidence → Verifier → signed Result → RP/KMS release-policy decision.
  2. RP/KMS, Verifier, TD, QGS, and TDQE sequence; QGS is transport and TDQE signs Quote.
- `final/render/slide-*.png` — 180 DPI LibreOffice renders.
- `render-manifest.json` — renderer, source, lockfile, hash, and slide hash provenance.

## Rebuild and verify

```bash
npm ci
npm run build
python3 ../../../skills/communication/to-deck/scripts/render_deck.py \
  --deck final/intel-tdx-attestation-v2.pptx \
  --manifest render-manifest.json \
  --output-dir final/render \
  --text-output final/render-slides.md \
  --dpi 180 --producer-kind script \
  --producer-command 'npm run build' \
  --producer-source build-deck.mjs --producer-lockfile package-lock.json
```

The deck is an educational decision model, not a deployable Quote verifier.
