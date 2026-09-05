# MetroPT Reliability Agent

A diagnostic and reliability agent for the **Air Production Unit (APU)** of Metro do
Porto trains, built on the public **MetroPT-3** dataset.

**Status: design checks closed, no code yet.** The data is downloaded and measured,
the viability gate passed at four failure events, and the topology is built. See [docs/design-sketch-2026-09-05.md](docs/design-sketch-2026-09-05.md) for the design
and [docs/findings-2026-09-05.md](docs/findings-2026-09-05.md) for what the source
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
| sha256 of the CSV | `db30ccb4ea402e3c8bf2c99db06e288d4f2a772f6928f9dbe26a920d69793e24` |
| size | 208 MB zip; CSV is 218,300,507 bytes |
| records | 1,516,948 rows on disk, decimated 10:1 from 15,169,480 acquired |
| signals | 15 (7 analogue, 8 digital), no GPS |
| rate | acquired at 1 Hz, published at 0.1 Hz |
| period | 2020-02-01 00:00:00 to 2020-09-01 03:59:50, measured |
| citation | Davari N, Veloso B, Ribeiro R, Gama J. MetroPT-3 Dataset. UCI Machine Learning Repository; 2021. |

CC BY 4.0 permits redistribution with attribution, but the file stays out of git
because of its size. See `data/README.md` for how to obtain it.
