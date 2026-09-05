# MetroPT Reliability Agent

A diagnostic and reliability agent for the **Air Production Unit (APU)** of Metro do
Porto trains, built on the public **MetroPT-3** dataset.

**Status: design sketch.** Structure and design only. No data downloaded, no code
written. See [docs/design-sketch-2026-09-05.md](docs/design-sketch-2026-09-05.md) for the design
and [docs/findings-2026-09-06.md](docs/findings-2026-09-06.md) for what the source
checks returned.

## Origin

Modelled on [ScottDuncanAI/industrial-ai-troubleshooting-agent](https://github.com/ScottDuncanAI/industrial-ai-troubleshooting-agent),
which applies the same pattern to a CFB boiler. The difference is in the data: that
one is process anomaly detection with no recorded failure at all, while this one has
real equipment in service, failures dated by the operator, and right censoring.

That allows a layer the original cannot have: **reliability proper**, built on time
to event rather than signal deviation alone.

## Data

| item | value |
|---|---|
| source | [UCI MetroPT-3](https://archive.ics.uci.edu/dataset/791/metropt+3+dataset) |
| DOI | 10.24432/C5VW3R |
| licence | CC BY 4.0 |
| size | 208 MB, CSV |
| records | 1,516,948 |
| signals | 15 (7 analogue, 8 digital), no GPS |
| rate | 0.1 Hz (not 1 Hz; see docs/findings-2026-09-06.md) |
| period | Feb to Aug 2020 |
| citation | Davari N, Veloso B, Ribeiro R, Gama J. MetroPT-3 Dataset. UCI Machine Learning Repository; 2021. |

CC BY 4.0 permits redistribution with attribution, but the file stays out of git
because of its size. See `data/README.md` for how to obtain it.
