# bitboom/skills

Small, reviewable skills for evidence-first technical communication.

## Skills

| Skill | Purpose |
|---|---|
| [`point`](skills/communication/point/SKILL.md) | Build an authoritative domain explanation and a blind source map, compare them, then synthesize an evidence-backed teaching model that novice developers and technical executives can accurately teach back. |
| [`to-deck`](skills/communication/to-deck/SKILL.md) | Turn an approved Point into a diagram-led, audience-tested presentation with a complete audit trail. |

The skills are deliberately composable:

    domain baseline + source map → Point → approved content model → To Deck → presentation

## Install

After this repository is published:

```bash
npx skills add bitboom/skills --skill point
npx skills add bitboom/skills --skill to-deck
```

The skill is user-invoked because it runs a deliberate, multi-stage review workflow.

## Quality contract

- Point gate: complete claim and model coverage, blind domain/source comparison, successful novice and executive teach-back, weighted score ≥ 90/100, and every criterion ≥ 4/5.
- Slide gate: a mandatory meaning-bearing diagram for structural topics, successful cold read, weighted score ≥ 90/100, and zero semantic or rendering hard-check failures.
- Every revision is immutable and packaged with hashes in a review trail.

## Development

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

The repository is intentionally small: the workflow stays in `SKILL.md`, deterministic checks stay in `scripts/`, and detailed contracts stay in `references/`.
