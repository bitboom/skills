# Intel RATS full-Point prose v2 paired deck

This immutable round uses the canonical passed Point package directly, rather than the earlier selective `to-site.input.json` projection.

- Canonical Point hash: recorded in `input/point.sha256`
- Summary: 2 slides, with deliberate omissions recorded in `final/summary-structural-crosswalk.json`
- Structural: 15 slides, covering all canonical Point claims, nodes, edges, boundaries, context dependencies, proof/non-proof entries, implications, caveats, exclusions, and source IDs
- Prose contract: `final/prose-trace.json` maps every Point claim to a visible Korean sentence

## Rebuild

```bash
npm ci
npm run build
npm run validate
```

Render both decks using `skills/communication/to-deck/scripts/render_deck.py`. The package gate must be run only against the generated render manifests.
