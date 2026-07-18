# To Deck paired summary and structural delivery plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Extend To Deck so one passed Point yields both a 1–2 slide executive-quality summary and a complete, structurally navigable PowerPoint deck without semantic drift.

**Architecture:** Keep Point as one immutable semantic source. Add two independent deck projections: a deliberately selective `summary` visual argument and a complete `structural` slide system. A coverage matrix and crosswalk prevent the concise deck from contradicting the complete deck or the complete deck from omitting Point material.

**Tech Stack:** Existing To Deck `pipeline.py`, `render_deck.py`, PPTX object inspection, JSON provenance, slide rendering, cold-read review artifacts.

---

### Task 1: Define delivery profile at run initialization

**Files:**
- Modify: `skills/communication/to-deck/SKILL.md`
- Modify: `skills/communication/to-deck/references/run-contract.md`
- Create: `skills/communication/to-deck/references/delivery-modes.md`

1. Add `delivery_profile: summary | structural | paired` to the deck brief and default to the user-selected mode.
2. Require `paired` runs to have one Point hash and separate output subtrees for the two decks.
3. Add artifact names for summary/structural PPTX, render manifests, reports, coverage map, and crosswalk.
4. Verify documentation links and run the existing To Deck test suite.

### Task 2: Add summary-deck contract

**Files:**
- Modify: `skills/communication/to-deck/SKILL.md`
- Modify: `skills/communication/to-deck/references/delivery-modes.md`
- Test: `skills/communication/to-deck/tests/test_delivery_modes.py`

1. Add a failing test asserting that summary guidance requires a `summary_must_see_ids` selection, proof limit, decision owner, and one/two-slide cap.
2. Define the 1-slide and 2-slide information architectures.
3. Require a deliberate omissions list instead of claiming full Point coverage.
4. Pass the test and confirm the existing component-selection regression tests still pass.

### Task 3: Add structural coverage artifact and gate

**Files:**
- Modify: `skills/communication/to-deck/scripts/pipeline.py`
- Modify: `skills/communication/to-deck/references/run-contract.md`
- Modify: `skills/communication/to-deck/references/delivery-modes.md`
- Create: `skills/communication/to-deck/tests/test_structural_coverage.py`

1. Write failing fixtures for an unmapped claim, edge, source reference, proof limit, and decision condition.
2. Implement a `structural-coverage` command that reads the frozen Point/model and inspected object map, then fails if any material input lacks a slide/object location.
3. Require coverage roles (`primary`, `supporting`, `source-footer`, `appendix`) and forbid a critical relation from source-footer-only coverage.
4. Run the new tests plus all existing To Deck tests.

### Task 4: Add paired crosswalk gate

**Files:**
- Modify: `skills/communication/to-deck/scripts/pipeline.py`
- Create: `skills/communication/to-deck/tests/test_summary_structural_crosswalk.py`
- Modify: `skills/communication/to-deck/references/delivery-modes.md`

1. Write failing fixtures where the summary and structural deck disagree about decision owner, artifact direction, or proof limit.
2. Implement `summary-structural-crosswalk` validation against the shared Point hash and the two visual models.
3. Require every summary must-see ID to locate its primary structural slide/object.
4. Run the targeted tests and a generated paired fixture through both gates.

### Task 5: Build a complete Intel RATS paired fixture

**Files:**
- Create: `examples/intel-rats/to-deck-paired/`
- Reuse: `examples/intel-rats/point-result.md`

1. Build the existing 2-slide decision/sequence deck as the `summary` deliverable.
2. Build a structural deck that covers every Intel RATS Point claim, actor, trust boundary, message path, proof/non-proof, policy branch, developer implication, executive implication, and source reference.
3. Create `structural-coverage-map.json` and `summary-structural-crosswalk.json` from inspected final PPT object IDs.
4. Render every slide, package both trails, and run the new coverage/crosswalk gates.

### Task 6: Review and freeze paired outputs

**Files:**
- Create: `examples/intel-rats/to-deck-paired/final/`

1. Conduct summary cold-read review for gist, core mechanism, decision owner, and proof limit.
2. Conduct structural navigation review: locate sampled claims, sources, model edges, and failure cases only from the deck.
3. Inspect every render for clipping, contrast, Korean glyphs, source footer legibility, and editable-object coverage.
4. Package the two decks plus the coverage map/crosswalk, run portable package verification, commit, and push.

## Completion criteria

- Summary remains exactly one or two slides and teaches the Point result without false completeness.
- Structural PPTX maps every material Point input to a readable slide/object and source marker.
- The two decks share a frozen Point hash and never contradict each other.
- Both have passing render, reader, coverage, and package evidence.