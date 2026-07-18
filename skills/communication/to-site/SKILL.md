---
name: to-site
description: Turn a passed Point semantic package into a concise, evidence-preserving static narrative site. Use when a verified technical brief needs a public or internal reader surface with claim/source traceability, diagram accessibility, portable build output, and desktop/mobile screenshot evidence.
---

# To Site

Render a Point package as a reader, not a deck copied into the browser. Keep the Point source immutable and fail closed when claim, qualifier, proof limit, model object, or source provenance cannot be preserved.

## Run

1. Read `references/run-contract.md`, `references/site-rubric.md`, and `references/research-basis.md`.
2. Require a passed Point package plus an explicit public source catalog. Never infer canonical source URLs from local file paths.
3. Create a `to-site.input.v1` projection and run `scripts/pipeline.py validate` before design work.
4. Write `01-visual-direction.yaml` after semantic validation: subject, audience, one page job, layout thesis, semantic structure, responsive policy, reduced-motion policy, and one restrained signature. Anthropic `frontend-design` is a pinned visual-direction reference only; it cannot create claims or hide caveats.
5. Default to Astro Core + plain CSS + schema-validated content + browser screenshots. Use Starlight only for a real documentation corpus.
6. Select one focused diagram job. Archify is optional and pinned: retain typed IR, validator output, SVG hash, and model/source mapping. Run `scripts/export_archify_svg.py --html <renderer-output.html> --output <site>/public/archify/<name>.svg` to make a site-owned static SVG. Use an equivalent table/text; never embed the toolbar HTML or treat layout success as semantic proof.
7. Build `dist/`, run `scripts/validate_site.py`, inspect desktop/mobile screenshots, then package the semantic map, report, screenshots, and manifest.

## Non-negotiable gates

- Every selected claim, diagram node, edge, and boundary has public source refs.
- Claims keep qualifiers, evidence strength, proof limits, and explicit unknown states.
- `/` teaches the decision model first; `/mechanism/` carries the protocol detail; `/evidence/` exposes sources and caveats.
- Public output contains no local paths, private excerpts, credentials, or unstated claims.
- Built `dist/` works on a generic static HTTP server; links, deep routes, screenshots, focus, non-color cues, and reduced-motion behavior are checked.

See `references/run-contract.md` for artifacts and `references/site-rubric.md` for screenshot acceptance criteria.
