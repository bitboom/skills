# To Site run contract

Never mutate the Point input. A site run uses a versioned projection and produces portable static output.

```text
<run>/
├── input/{point.yaml,point.sha256,sources.json,to-site.input.json}
├── 01-visual-direction.yaml
├── generated/{claims.generated.json,sources.generated.json,models.generated.json,semantic-map.json,site-content.json}
├── site/                         # framework source
├── dist/                         # deployable output
├── verification/
│   ├── projection-gate.json
│   ├── site-gate.json
│   └── screenshots/{desktop.png,mobile.png}
├── site-manifest.json
└── review-trail.zip
```

## Input projection

`to-site.input.v1` must include a Point SHA-256, title, thesis, claims, sources, models, and `does_not_prove`.

- A claim has stable ID, text, qualifier, proof limit, evidence status, and one or more source refs.
- A source has a stable ID, title, public canonical `http(s)` URL, and useful locator.
- Every model node, edge, and boundary has stable ID and source refs.
- Unknown/undocumented conditions remain explicit instead of becoming empty UI.

Run `scripts/pipeline.py validate --input <input> --output <report>` and `project` before site generation. Both return exit 2 on semantic failure.

## Diagram contract

Select a diagram only when spatial placement lowers inference cost. If optional Archify is used, pin `tt-a1i/archify` revision, preserve IR/validation/SVG hashes, map every node/edge/boundary to model/source IDs, and render a site-native accessible equivalent. Do not publish the Archify HTML toolbar/export UI.

## Verification contract

`dist/` contains `index.html`, `mechanism/index.html`, and `evidence/index.html`. Each selected semantic ID appears in public DOM hooks (`data-claim-id`, `data-source-id`) without exposing local source paths.

Run `scripts/validate_site.py --dist <dist> --semantic-map <map> --output <report>`. It checks required pages, DOM semantic coverage, private-path leakage, and internal links. Screenshot `desktop.png` and `mobile.png` are mandatory; inspect overflow, clipped text, diagram labels, focus, contrast, non-color distinctions, and reduced-motion behavior.
