# Visual component catalog

Use this catalog as a required starting set, not a closed enum. Add a custom family only with a plain definition and an explicit visual-job fit. A component is meaning-bearing only when removing it would remove a Claim, model relationship, boundary, decision, proof limit, or required cold-read answer.

## Dominant components

| Family ID | Best-fit visual jobs |
|---|---|
| `causal-pipeline` | mechanism, causal path, artifact movement, action |
| `sequence-or-handshake-diagram` | sequence, artifact movement, actor relationship |
| `system-architecture` | actor relationship, mechanism, trust boundary |
| `trust-boundary-and-data-flow-diagram` | trust boundary, artifact movement, causal path |
| `decision-tree` | decision or branching, action, limitation |
| `state-machine` | state transition, decision or branching, invalid outcomes |
| `lifecycle-or-timeline` | sequence, lifecycle, expiry, transition |
| `layered-stack` | hierarchy, responsibility, interface boundaries |
| `comparison-matrix` | comparison, proof/non-proof, alternative selection |
| `knowledge-graph-or-topology` | actor relationship, topology, dependency |
| `evidence-and-verification-chain` | Evidence, evaluation, authenticated Result, policy action |
| `custom-domain-diagram` | a domain-specific grammar when applicable standard families all fail |

The dominant component must carry one coherent visual argument. A generic card grid is not a dominant component for a structural Point.

## Supporting components

| Family ID | Incremental job |
|---|---|
| `definition` | define the domain or first-use term |
| `key-characteristics` | expose a small set of distinguishing properties |
| `actor-legend` | decode unfamiliar actors without repeating the diagram |
| `inputs-and-outputs` | expose material artifacts entering or leaving the mechanism |
| `proof-and-non-proof` | separate what Evidence proves from what it does not prove |
| `benefits` | state decision-relevant value not visible in the mechanism |
| `limitations-and-risks` | expose trust, availability, or operational limits |
| `decision-and-next-action` | state the owner, decision, and next action |
| `use-cases` | show where the mechanism applies |
| `source-project-lens` | explain the source project's role without making it the hero |
| `bottom-takeaway` | compress the visible argument into one final consequence |

A support is eligible only when it adds a previously uncovered must-see baseline ID. Restating the dominant diagram is redundancy, not support.

## Never score as semantic components

- page numbers;
- decorative icons;
- simple backgrounds, panels, rules, shadows, or brand ornaments;
- spacing, color palette, or typography by itself.

These may exist in the deck but must not claim baseline, Point, model, or component coverage.

## Custom extension contract

For a family not listed above, record:

```json
{
  "family": "custom-domain-diagram",
  "catalog_extension": {
    "definition": "A domain-specific diagram that keeps two coupled trust paths visible.",
    "job_fit": "Closes Evidence and policy-action paths that no standard family can express legibly."
  }
}
```

Custom does not bypass thresholds, hard failures, accessibility, editability, or cold-read gates.
