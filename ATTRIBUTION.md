# Attribution

**Licensing in one line:** the code and documentation in this repository are MIT
(see `LICENSE`). That does **not** cover the MetroPT-3 dataset, which is not
redistributed here and carries its own CC BY 4.0 terms.

This repository is analysis built on other people's work. Nothing here would exist
without the data and the papers below, and none of that data is redistributed in this
repository: `data/raw/` is git-ignored and `data/README.md` says how to fetch it from
the original source.

## The dataset

**MetroPT-3**, readings from the Air Production Unit of a Metro do Porto train,
February to September 2020.

> Davari N, Veloso B, Ribeiro RP, Gama J. **MetroPT-3 Dataset**. UCI Machine Learning
> Repository, 2021. DOI: [10.24432/C5VW3R](https://doi.org/10.24432/C5VW3R)

Licence **CC BY 4.0**, which permits redistribution and adaptation with attribution.
Collected by the Laboratory of Artificial Intelligence and Decision Support at
**INESC TEC**, with the **University of Porto**, in a project with the metro operator
of Porto, Portugal. The work was supported by CHIST-ERA grant CHIST-ERA-19-XAI-012 and
project CHIST-ERA/0004/2019 funded by FCT.

The sensor definitions, the operating thresholds and the four failure reports used
throughout this repository all come from `Data Description_Metro.pdf`, which ships
inside the UCI download and is the primary source for this dataset.

## The papers

The paper that introduces the dataset and the analysis it was collected for:

> Davari N, Veloso B, Ribeiro RP, Pereira PM, Gama J. **Predictive maintenance based on
> anomaly detection using deep learning for air production unit in the railway
> industry**. 2021 IEEE 8th International Conference on Data Science and Advanced
> Analytics (DSAA), pp. 1-10, 2021.
> DOI: [10.1109/DSAA53316.2021.9564181](https://doi.org/10.1109/DSAA53316.2021.9564181)

The APU topology in `kg/apu_topology.json` and `docs/apu_schematic.svg` is built from
the equipment and sensor descriptions in these two, which document the sibling 2022
dataset from the same unit:

> Veloso B, Ribeiro RP, Pereira PM, Gama J. **The MetroPT dataset for predictive
> maintenance**. Scientific Data 9, 764, 2022.
> DOI: [10.1038/s41597-022-01877-3](https://doi.org/10.1038/s41597-022-01877-3)

> Veloso B, Gama J, Ribeiro RP, Pereira PM. **A Benchmark dataset for predictive
> maintenance**. arXiv:2207.05466, 2022.
> [arxiv.org/abs/2207.05466](https://arxiv.org/abs/2207.05466)

Where the 2022 description and the MetroPT-3 primary source disagree, this repository
follows the primary source and records the disagreement. They do disagree, on H1: see
`docs/findings-2026-09-05.md`.

## Instrumentation

The sensor hardware is cited by the source papers, not measured here: IFM PT5414
pressure transmitters, LEM AT-B420L AC current transducer, WIKA TC12-M thermocouple.

## The architecture

The four-layer pattern this project follows, a historian, an event log, a topology
graph and a document base, each exposed to an agent through MCP tools, is taken from:

> Scott Duncan. **industrial-ai-troubleshooting-agent**.
> [github.com/ScottDuncanAI/industrial-ai-troubleshooting-agent](https://github.com/ScottDuncanAI/industrial-ai-troubleshooting-agent)
> Apache License 2.0, Copyright 2025 Scott Duncan.

**No code from that repository is copied here.** The debt is architectural: the idea of
one tool per data source over a stdio MCP server, and of an auditable investigation
trace. That project's own contribution notes invite building the same pattern on a
different dataset, which is what this is.

The two projects differ in the thing that matters to this one. The boiler dataset
covers five days with no recorded failure, so it supports anomaly detection and not
reliability. This dataset has seven months, four dated failures and natural right
censoring, which is what layer 5 is built on.

## What is original here

The life table and its analysis, the operating-time clock, the exposure test, the load
cycle analysis, the schematic generator, and the audit of the sources, including the
defects found in them. Those are in `docs/` and `scripts/`, under the MIT licence.
