# Superseded Intel-rats deck pilot

The original To Deck pilot is preserved as a regression case, not an accepted output.

Its content gate passed 97/100 and slide gate passed 96/100 under the first rubric, yet the user rejected the deck because it read like an audit report, omitted the core mechanism, lacked a meaning-bearing diagram, and used an unclear headline.

## Root cause

- The brief changed “what should I know?” into “may I trust this as an implementation baseline?”
- The frozen content became a corrections report, so slide production could not restore the missing mental model.
- Writing criteria measured accuracy, logic, ambiguity, and concision but not conceptual coverage or reader teach-back.
- A deck with no diagram could still receive a perfect diagram score.
- Rendering QA was allowed to pass an artifact whose information architecture had failed.

## Corrective action

- Split semantic work into `point` and visual work into `to-deck`.
- Make Point generate and verify an ideal, project-blind domain explanation before it reads the source, then compare that baseline with a baseline-blind source map.
- Require independent general-engineer and conditional technical-executive readers.
- Require What/How/Why/Action, nodes, edges, trust boundaries, and a context-free one-line Point.
- Make a meaning-bearing diagram mandatory for structural topics.
- Add baseline regression checks for mental-model reconstruction, scanability, and information coverage.
- Bind every review to the exact Point, PPTX, render, inspection, and visual-model hashes; derive diagram requirements from Point rather than reviewer-entered counts.
- Generate two blind storyboards, compare them before build, and preserve raw short-gist and longer-reconstruction answers from independent readers.

The accepted Point result is in [`point-result.md`](point-result.md). The replacement deck and its immutable review evidence are now recorded in [`to-deck-result.md`](to-deck-result.md).
