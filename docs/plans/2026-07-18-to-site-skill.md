# To Site Skill Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Turn a passed Point package into a concise, evidence-preserving static narrative site without weakening claims, qualifiers, proof limits, or source provenance.

**Architecture:** `to-site` consumes a frozen Point run read-only, validates a framework-independent semantic projection, and builds a portable Astro Core site. A pinned Archify renderer may produce a focused diagram prototype; a pinned Anthropic `frontend-design` reference governs the subject-specific visual-direction pass. Neither external skill can create claims or replace semantic, accessibility, or browser gates.

**Tech Stack:** Astro Core, plain CSS, Content Collections schema validation, Playwright (verification only); optional Archify SVG; Starlight only for a genuine documentation corpus.

---

## Scope and non-goals

**Required surfaces:** `/` (decision-first thesis), `/mechanism/` (one focused architecture/workflow/sequence visual), `/evidence/` (claims, source refs, proof limits, caveats). Generate `/glossary/` only when Point supplies one.

**Do not add:** a CMS, backend, database, remote search, React/Vue/Svelte, Tailwind/shadcn, automatic source research, new material claims, or an Archify HTML embed. Do not migrate an existing site framework without explicit direction.

## Pinned external references

| Source | Pin | Adopt | Explicitly do not adopt |
|---|---|---|---|
| Archify `tt-a1i/archify` | `ed0efcc763d358b78df845182b5ed24a9d165a1c` | typed architecture/workflow/sequence/data-flow/lifecycle IR; schema/layout checks; SVG prototype/export | grammar selection, evidence semantics, self-contained HTML toolbar, raster final output |
| Anthropic `frontend-design` | `fa0fa64bdc967915dc8399e803be67759e1e62b8` | subject/audience/page-job framing, meaningful structure, restrained signature, focus/reduced-motion, screenshot self-critique | generic visual defaults, invented copy/claims, evidence/provenance gates |

External revisions are recorded in every site run. A newer upstream version is not silently used; update the pin and rerun the visual review deliberately.

## Task 1: Define immutable input and visual-direction artifacts

**Files:**
- Create: `skills/communication/to-site/SKILL.md`
- Create: `skills/communication/to-site/references/run-contract.md`
- Create: `skills/communication/to-site/references/site-rubric.md`
- Create: `skills/communication/to-site/references/research-basis.md`
- Test: `skills/communication/to-site/tests/test_pipeline.py`

**Contract:** accept only a passed Point final package and validate its manifest/hash before projection. Preserve claim ID, source ID, text, qualifier, proof limit, evidence status, source title, canonical URL, locator, quote/selector when available, source hash, model node/edge/boundary, and explicit unknown state.

Create `01-visual-direction.yaml` only after the semantic projection passes:

```yaml
subject: "..."
audience: "..."
page_job: "one reader action or understanding outcome"
layout_thesis: "..."
palette: [{name: "...", hex: "#..."}]
type_roles: [{role: display|body|utility, family: "..."}]
signature_element: "one subject-grounded, meaning-bearing visual treatment"
structural_semantics: "how labels/dividers/numbering encode real content"
responsive_policy: "..."
motion_policy: "none or a named, reduced-motion-safe purpose"
rejected_generic_defaults: ["..."]
frontend_design_revision: "fa0fa64bdc967915dc8399e803be67759e1e62b8"
```

**Acceptance:** reject a visual direction whose page job is missing, whose structure is decorative-only, whose signature obscures evidence, or whose palette alone encodes semantic states.

## Task 2: Implement Point projection and optional Archify handoff

**Files:**
- Create: `skills/communication/to-site/scripts/pipeline.py`
- Create: `skills/communication/to-site/tests/fixtures/passed-point/`
- Test: `skills/communication/to-site/tests/test_pipeline.py`

**Generated projection:**

```text
generated/claims.generated.json
generated/sources.generated.json
generated/models.generated.json
generated/semantic-map.json
```

**Fail-closed tests:** missing final Point gate, manifest/hash mismatch, duplicate IDs, missing source ref, missing qualifier/proof limit, local path in a public source, or a site-only claim presented as source-confirmed.

**Archify is opt-in per diagram.** Select its mode from the already-approved visual job:

| Point visual job | Allowed mode |
|---|---|
| component/trust-boundary map | `architecture` |
| policy or approval flow | `workflow` |
| request/return trace | `sequence` |
| artifact lineage/sensitivity | `dataflow` |
| retry/terminal state | `lifecycle` |

Store the input IR, renderer revision, validator output, HTML hash, exported SVG hash, and `node/edge/boundary → Point/model/sourceRef` mapping in the run. Do not invoke Archify automatically. A generic diagram, a dense all-in-one map, or a diagram whose spatial layout does not reduce inference is rejected.

## Task 3: Build the minimal Astro Core reader

**Files:**
- Create: `skills/communication/to-site/templates/astro-core/`
- Create: `skills/communication/to-site/templates/astro-core/src/components/{Claim,SourceRef,Diagram}.astro`
- Create: `skills/communication/to-site/templates/astro-core/src/styles/site.css`
- Test: `skills/communication/to-site/tests/test_validate_site.py`

**Rules:**

1. `/` uses the decision model and preserves the point's `does_not_prove` result in the first reading path.
2. `/mechanism/` contains one diagram type and keeps node/edge explanation adjacent; add a text/table equivalent for every diagram.
3. `/evidence/` renders stable `data-claim-id` and `data-source-id` hooks, evidence status, qualifiers, proof limits, and explicit `Not documented in ingested sources` states.
4. Use the site theme and static SVG/accessible equivalent. Never iframe or ship Archify's self-contained HTML, toolbar, localStorage, or export UI.
5. The frontend-design pass may choose typography, palette, layout, and one restrained signature only after the semantic content is locked. It must preserve keyboard focus, contrast, responsive layout, and `prefers-reduced-motion`.

## Task 4: Add semantic, public-safety, and browser gates

**Files:**
- Create: `skills/communication/to-site/scripts/validate_site.py`
- Create: `skills/communication/to-site/tests/test_validate_site.py`
- Create: `skills/communication/to-site/templates/astro-core/package.json`

`npm run verify` must perform a lockfile install, static build, generic static-server smoke test, semantic map validation, local/private path and secret scan, base-path/deep-link/fragment validation, and Playwright browser QA.

**Semantic gates:** every selected claim is rendered once or explicitly excluded; every source ref resolves; qualifiers/proof limits/evidence status are not weakened or upgraded; unknown is visible; diagram nodes/edges/boundaries have source refs and a text equivalent.

**Visual/accessibility gates:** desktop and mobile full-page screenshots; no overflow, overlap, or clipping; heading/landmark order; descriptive links; keyboard focus; non-color state cues; image/diagram alternative; reduced-motion behavior; zero required console/network failures.

Require screenshot creation everywhere. Require golden pixel comparison only in a pinned identical browser/OS/font CI environment.

## Task 5: Package provenance and verify a vertical slice

**Files:**
- Create: `skills/communication/to-site/references/github-pages-handoff.md`
- Create: `skills/communication/to-site/tests/test_package_contract.py`

Produce:

```text
dist/
verification/report.json
verification/semantic-map.json
verification/screenshots/{desktop.png,mobile.png}
site-manifest.json
review-trail.zip
```

`site-manifest.json` records Point input hash, generated projection hashes, template/generator revision, lockfile hash, external Skill pins used, optional Archify IR/SVG hashes, commands, browser/viewport, and all gate results. `dist/` must work under a generic static HTTP server without Node at runtime.

## Definition of done

- [ ] Point semantics and provenance are preserved without new claims.
- [ ] The first page teaches a decision model; protocol/architecture detail is separate.
- [ ] Archify is used only when a typed diagram meaningfully reduces inference and its output is traceable, static, and accessible.
- [ ] Anthropic frontend-design improves visual direction without turning style into evidence or hiding caveats.
- [ ] Browser, semantic, public-safety, and accessibility gates pass from a clean lockfile build.
- [ ] Desktop/mobile screenshots and a portable review trail exist.
