# MetroPT Reliability Agent

A diagnostic and reliability agent for the **Air Production Unit (APU)** of Metro do
Porto trains, built on the public **MetroPT-3** dataset.

**Status: layers 1, 2, 3 and 5 built and served over MCP.** Still missing: the
document base for retrieval, layer 4. See [docs/design-sketch-2026-09-05.md](docs/design-sketch-2026-09-05.md) for the design
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
because of its size. See [data/README.md](data/README.md) for how to obtain it.

## What is here

| | |
|---|---|
| [docs/design-sketch-2026-09-05.md](docs/design-sketch-2026-09-05.md) | the design, and the five checks that had to pass before any code |
| [docs/findings-2026-09-05.md](docs/findings-2026-09-05.md) | what the sources returned, including three errors this repository made and corrected |
| [docs/findings-exposure-and-cycles.md](docs/findings-exposure-and-cycles.md) | are the logging gaps downtime? does the load cycle shorten before a failure? |
| [docs/layer5-life-table.md](docs/layer5-life-table.md) | **the point of the project**: what four recurrent events can and cannot support |
| [docs/apu-topology.md](docs/apu-topology.md) + [apu_schematic.svg](docs/apu_schematic.svg) | the unit, its 15 tags and its documented thresholds |
| [kg/apu_topology.json](kg/apu_topology.json) | the topology, machine readable, every node carrying its provenance |
| [data/events.csv](data/events.csv) | the life table: four failures and one suspension |
| [scripts/](scripts/) | the pipeline, and how to run it |

## The agent

`scripts/mcp_server.py` serves seven tools over stdio:

| tool | |
|---|---|
| `historian_tags` | the 15 signals, units, what they measure, documented thresholds |
| `historian_window` | the extent of the data, and how much of the calendar is missing |
| `historian_get_tag_data` | time series, with optional bucketing |
| `historian_gaps` | when the machine was off, useful for reconstructing downtime |
| `events_life_table` | the four reported failures, with the source's own defects marked |
| `reliability_summary` | rate, interval and trend, on either clock |
| `kg_component` | what a component is, what it connects to, what watches it |

Two conventions run through all of them. Rates are denominated in **operating time**,
because a calendar denominator is 22 % optimistic here. And **an event is not an
anomaly**: the life table holds only what the operator reported, never something
inferred from the signal.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/reliability.py   # writes data/events.csv
.venv/bin/python scripts/ingest.py        # builds data/metropt.duckdb
.venv/bin/python scripts/mcp_server.py --selftest
```

`.mcp.json` registers the server for MCP clients that read it.

## Headline result

Roughly **one air leak every 44 days of operation**, somewhere between 19 and 128 days
at 90 % confidence, with **no detectable trend** over seven months. The interval is the
result; a point estimate here would be a fiction with three significant figures.

Two things fell out along the way that are worth more than the number. The logging gaps
are the machine being off rather than lost telemetry, which is demonstrable from the
pressure decay and which moves the rate by 22 %. And the largest excursion in the whole
series, 22 times the baseline load-cycle rate for two consecutive days, carries no
maintenance report, so the dataset's four labels are not an exhaustive list of its
anomalies.

## Credit

This is analysis built on other people's data and papers. The dataset is by Davari,
Veloso, Ribeiro and Gama at INESC TEC and the University of Porto, under CC BY 4.0;
the agent architecture follows Scott Duncan's
[industrial-ai-troubleshooting-agent](https://github.com/ScottDuncanAI/industrial-ai-troubleshooting-agent),
Apache 2.0, with no code copied. Full citations and the exact debts are in
[ATTRIBUTION.md](ATTRIBUTION.md).

Code and documentation here are MIT. The dataset is not redistributed and keeps its own
licence.
