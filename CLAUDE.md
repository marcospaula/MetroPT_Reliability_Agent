# MetroPT_Reliability_Agent — repository instructions

A diagnostic and reliability agent for the Metro do Porto APU (MetroPT-3 dataset).
A method artefact, and a candidate for public release. **Everything in this repository
is written in English**: code, documentation and commit messages.

## Scope and safety

- The data is **CC BY 4.0**: redistribution with attribution is allowed. Credit Davari,
  Veloso, Ribeiro and Gama, and the DOI, on any figure or post derived from it.
- None of the data belongs to Marcos and none of it is personal. The investment
  cockpit's discretion rule does not apply here.
- **Commit and push only when he asks.** No remote while this is a sketch.
- Isolated repository, its own git and venv. Do not mix it with
  `industrial-ai-troubleshooting-agent`, which is a third-party clone with read-only
  permission.

## Method rules

- **Recompute, do not re-read.** Every number taken from a dataset description, a paper
  or a web search is an assumption until checked against the CSV. The "7 analogue,
  8 digital" split and the failure count both entered here by description, not by
  reading the file.
- **Verify by the defect, not by the fix.** When checking a finding, try to reproduce
  the failure it claims, rather than confirming that the correction runs.
- **An event is not an anomaly.** The boiler repository calls a KPI band excursion an
  anomaly. Here, a failure event is what the operator's report says it is. Do not let
  the two contaminate each other: a detected anomaly never enters the life table.
- **Censoring is data, not a defect.** The window ends with the compressor still
  running. Every life estimate must carry the suspension explicitly.
- **Report ranges, never a single point.** With few events, the interval is the answer.
  Publish the sensitivity; never elect a true value.
- **An error that favours the conclusion is the most dangerous one.** If a number makes
  the thesis look good, recheck it first.

## State

Skeleton only. `docs/design-sketch-2026-09-05.md` holds the design and the checks that
must pass before any code is written.
