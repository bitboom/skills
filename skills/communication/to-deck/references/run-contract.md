# Run contract

Never overwrite a round. Use two-digit versions beginning with v01.

    <run>/
    ├── 00-deck-brief.yaml
    ├── 00-brief-decision.md
    ├── input/{point.md,point.yaml,point.sha256,point-gate.json}
    ├── 01-visual-query.md
    ├── 02-visual-baseline.json
    ├── 03-constraint-map.json
    ├── 04-component-rubric.json
    ├── 05-visual-component-catalog.json
    ├── slides/
    │   ├── v01-visual-jobs-a.json
    │   ├── v01-visual-jobs-b.json
    │   ├── v01-component-score-a.json
    │   ├── v01-component-score-b.json
    │   ├── v01-component-ensemble-a.json
    │   ├── v01-component-ensemble-b.json
    │   ├── v01-candidate-a.json
    │   ├── v01-candidate-b.json
    │   ├── v01-component-selection-audit.json
    │   ├── v01-component-gate.json
    │   ├── v01-selection.json
    │   ├── v01-storyboard.md
    │   ├── v01-visual-model.json
    │   ├── v01-deck.pptx
    │   ├── v01-deck.inspect.ndjson
    │   ├── v01-render/
    │   ├── v01-render-manifest.json
    │   ├── v01-semantic-review.json
    │   ├── v01-reader-review.json
    │   ├── v01-executive-review.json
    │   ├── v01-writer-review.json
    │   ├── v01-visual-review.json
    │   ├── v01-regression-review.json
    │   ├── v01-gate.json
    │   └── v01-decision.md
    ├── final/{final-deck.pptx,final-deck.sha256,final-report.md}
    ├── manifest.json
    └── review-trail.zip

Every post-build review contains round, Point, brief, deck, render, inspection, visual-model, component-selection-audit, and component-gate hashes; reviewer ID/model; author model; review-prompt hash; allowed inputs; critical issues; issues; scores; and justification. The gate rejects stale files and duplicate cold-reader identities.

Selection also records query, baseline, constraint, and candidate hashes; blind-candidate and coverage hard checks; selected candidate; must-see totals; and coverage rows.

## Visual component selection

The rubric and catalog are immutable run inputs. The rubric records Point, Point-model, baseline, and constraint hashes plus its source hash. It cannot contain its own file hash. The catalog adds the rubric hash and deterministic A/B candidate-seed hashes. Candidate seeds hash the branch label, Point, model, baseline, constraints, and rubric; they do not encode a visual grammar.

Each A/B jobs, score, ensemble, and candidate artifact records Point, model, baseline, constraints, rubric, catalog, candidate-seed, and every causally prior branch-artifact hash. This prevents self-hash and future-output cycles. The selection audit records both actual candidate hashes and all branch artifacts. `component-gate` rejects stale or missing artifacts before slide construction; `slide-gate` revalidates the bundle and the passed component-gate hash.

Every `vNN` component artifact contains the same positive integer `round`; its filename version, component-gate round, selection round, and all post-build review rounds must agree. A failed round is never overwritten. The next attempt copies the frozen run inputs and writes a complete new `vNN` artifact chain.

Each visual job links Claim IDs, model node/edge/boundary IDs, must-see IDs, criticality, audience, cold-read answer, and preserved distinctions. Each component score contains anchored criterion scores with justifications, covered and uncovered IDs, risks, hard failures, and assumptions. Each ensemble records one dominant component, at most three supports, incremental baseline value for every support, exact coverage, preserved distinctions, redundancy penalty, and the recomputed score.

The final visual model maps every meaning-bearing object to component IDs, baseline IDs, Point IDs, model IDs, and inspected artifact-object IDs. Decoration, page numbers, and backgrounds carry no semantic coverage. All required baseline sets and every Point/model ID selected by the ensemble must survive into the final visual-object map.

Semantic review records structural totals and checked totals, dominant-visual share, causal-path checks, actor separation, proof/non-proof visibility, project hierarchy, and diagram direction errors.

Reader review stores raw five-to-ten-second gist and twenty-to-thirty-second reconstruction before `gist_recovered_ids` and `reconstruction_recovered_ids`. Executive review does the same with `executive_recovered_ids`. Writer review records `headline_recovered_ids`. Visual review records full-size/thumbnail inspection, exact rendered-slide hashes, a raw thumbnail gist and mechanism answer, `thumbnail_mechanism_recovered_ids`, complete bug-hunt checks, reviewer/provider provenance, `review_pass >= 2`, support-block count, structural-test status, density telemetry, and all render hard checks.

## Portable rendering and visual traces

`scripts/render_deck.py` creates the required schema-v2 render manifest. `slides[*].path` is relative to the manifest directory, cannot be absolute or escape it, must resolve inside it after symlink resolution, and is hash- and PNG-dimension-verified by `slide-gate`. The helper clears stale `slide-*.png`, PDF, text, and manifest outputs before rendering; it requires contiguous numeric PNG filenames and PPTX/PNG page-count agreement. The manifest records renderer/rasterizer/extractor versions, the environment, a producer command, and whether production was `manual` or `script`. A script producer additionally records its source and, when one governs the build, a lockfile inside the manifest directory plus hashes; a missing or stale declared source/lockfile fails the gate. Schema-v1 manifests are intentionally unsupported: regenerate the complete immutable review round with `render_deck.py`.

The final visual model contains at least one `critical_artifact_traces` record with distinct producer, checker, consumer, and connector object IDs, a valid visible direction, and `connector_paths` entries (`connector_object_id`, `from_object_id`, `to_object_id`) that connect producer → checker → consumer. If `security_boundary_required` is true in the baseline, the baseline declares every required role/artifact/checker/decision/failure model ID and the visual model maps all of them to a `security_boundary_trace`; its connector paths must connect role → checker → distinct decision → failure. This prevents a cache, verifier, decision owner, or failure path from being present only as unconnected prose.

Before `package`, run `pipeline.py verify-package --archive <zip> --deck <package-relative-deck> --render-manifest <package-relative-manifest> --output <json>`. It rejects encrypted, duplicate, symlink, traversal, oversized, and high-compression ZIP members before bounded clean extraction, then revalidates the manifest, slide hashes/dimensions, and declared producer assets. A packaged review trail is not reproducible until that check passes.

Regression review is required when 00-deck-brief.yaml names a prior deck. It records blind_review_completed_before_comparison, user_rejected_dimensions, improvements, no_regression, and regressions.

Gate JSON is generated by pipeline.py and never hand-edited.
