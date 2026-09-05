# MetroPT_Reliability_Agent — repository instructions

A diagnostic and reliability agent for the Metro do Porto APU (MetroPT-3 dataset).
A method artefact, published under MIT. **Everything in this repository is written in
English**: code, documentation and commit messages.

## Scope

- The data is **CC BY 4.0** and is **not redistributed here**. Credit Davari, Veloso,
  Ribeiro and Gama, and the DOI, on any figure or text derived from it. See
  ATTRIBUTION.md.
- The raw CSV lives in `data/raw/`, which is git-ignored. Only derived artefacts small
  enough to be diffable are tracked, such as `data/events.csv`.
- This repository has its own git and its own venv. Nothing here depends on a local
  checkout of another project.

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

The five pre-code checks are closed and layer 5 is built. `docs/` carries the design,
the source audit, the exposure and cycle analyses, and the life table. Still open: the
MCP server, the historian database, and the document base in `kb/`.
