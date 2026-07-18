# Intel RATS paired To Deck run

This run projects one frozen Point into two independent PowerPoint deliverables:

- `final/summary/intel-tdx-attestation-summary.pptx` — two-slide decision and sequence summary.
- `final/structural/intel-tdx-attestation-structural.pptx` — a complete, navigable structural deck.

Both outputs use the copied `input/to-site.input.json` semantic package (`point_sha256` `59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891`). The structural coverage map is exhaustive for its claims, sources, model nodes/edges/boundaries, proof limits, and Point-declared deployment obligations.

## Rebuild

```bash
npm ci
npm run build
python3 validate-paired.py
```

Render each deck with `skills/communication/to-deck/scripts/render_deck.py`; use the generated manifests only. The final package contains both decks, their render trails, coverage map, crosswalk, source inputs, and package gate evidence.
