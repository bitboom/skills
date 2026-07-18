# Intel RATS — To Site final v1

A static, evidence-preserving reader derived from the passed Intel RATS Point package.

## Public reader

- `/` — the Evidence → Verifier → RP/KMS decision model and explicit proof limits.
- `/mechanism/` — generated signed-Result sequence plus an equivalent ordered text path.
- `/evidence/` — claim, qualifier, proof-limit, and canonical public-source ledger.

## Provenance

- Point package SHA-256: `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`
- Archify renderer: `tt-a1i/archify` at `ed0efcc763d358b78df845182b5ed24a9d165a1c`
- `archify/validation.json` and `archify/check.txt` record the renderer checks.
- `public/archify/intel-tdx-sequence.svg` is a static, site-owned export. The HTML renderer, toolbar, and local state are not embedded.

## Build and verify

```bash
npm ci
python3 ../../../skills/communication/to-site/scripts/pipeline.py validate \
  --input input/to-site.input.json --output verification/projection-gate.json
npm run build
python3 ../../../skills/communication/to-site/scripts/validate_site.py \
  --dist dist --semantic-map generated/semantic-map.json \
  --output verification/site-gate.json
```

Use `qa-screenshots.mjs` with a local static server for desktop and mobile screenshot gates. This is educational material, not a deployable verifier.
