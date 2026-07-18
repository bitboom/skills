# Intel RATS full-Point prose v3 paired deck

This round reads the passed canonical Point directly, not the earlier selective projection.

- Point hash: `input/point.sha256`
- Summary: 2 slides
- Structural: 16 slides; all canonical claims, nodes, edges, boundaries, state, proof limits, caveats, implications, exclusions, and source markers are mapped
- `final/prose-trace.json`: 10 reader-visible Korean claim sentences
- `final/structural-coverage-map.json`: 88 canonical material IDs
- `validate-prose-v2.py`: extracts actual PPTX slide text and fails on ownership, retained-state, summary-term, failure-branch, pilot-gate, and source-marker regressions

## Rebuild

```bash
npm ci
npm run build
npm run validate
```

Render using `skills/communication/to-deck/scripts/render_deck.py`. Run package verification against the generated render manifests only.
