# MetroPT Reliability Agent

A diagnostic and reliability agent for the **Air Production Unit (APU)** of Metro do
Porto trains, built on the public **MetroPT-3** dataset.

**Status: all five layers built and served over MCP.**

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
| [docs/data-quality.md](docs/data-quality.md) | **read first**: the acquisition freezes, the non-operating time, the decimation, and the defects in the source |
| [docs/layer5-life-table.md](docs/layer5-life-table.md) | **the point of the project**: what four recurrent events can and cannot support |
| [docs/signal-and-events.md](docs/signal-and-events.md) | does the load cycle shorten before a failure? |
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
| `kb_search` | the derived notes: what a leak looks like, where the data misleads |

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

## Asking it questions

Yes, that is the point of it. Open the repository in an MCP client such as Claude Code;
`.mcp.json` is picked up automatically, and questions in plain language get answered by
the tools above. Nothing is precomputed for a fixed set of questions.

```
> what happened to the compressor before the 15 July failure?

  events_life_table        -> the reported window, 15 Jul 14:30 to 19:00
  historian_gaps           -> a 14.2 h gap on 14 Jul: the unit was off, not quiet
  historian_get_tag_data   -> TP3 down to 5.93 bar, load cycles at 5.32/h against a
                              2.86 baseline, the 8th highest day of 205
  kb_search "air leak"     -> the signature, and the caveat that two of four reports
                              show nothing like it
  kg_component "reservoirs"-> LPS sits here; the leak path to the clients
```

Questions it answers well: what is this tag, what was happening on a date, when was the
machine off, how often does it fail, is there a trend, what does the topology say feeds
what, why does a number in a paper disagree with this repository.

Questions it will push back on: give me a Weibull beta for the APU, what is the
availability, is the failure rate increasing. In each case the honest answer is an
interval or a refusal, and the tools return the reason with the number.

Three commands are included for common jobs, in `.claude/commands/`:

| | |
|---|---|
| `/apu-status` | orientation: the data, the tags, the reliability position, what is unresolved |
| `/reliability-report` | the full layer 5 position, both clocks, with the model choice explained |
| `/investigate` | what the unit was doing over a window you name |

## Headline result

Roughly **one air leak every 44 days of operation**, somewhere between 19 and 128 days
at 90 % confidence, with **no detectable trend** over seven months. The interval is the
result; a point estimate here would be a fiction with three significant figures.

Two things fell out along the way that are worth more than the number. The logging gaps
are the machine being off rather than lost telemetry, which is demonstrable from the
pressure decay and which moves the rate by 22 %. And **ten acquisition freezes**, 6.96
days in which the analogue channels hold a single value while a digital channel toggles
on a fixed 40 s square wave, fabricate up to 63 load cycles per hour and outrank every
real event in the data.

Unmasked, those freezes are the top three days of the series, ahead of every reported
failure, and any detector trained on them learns a logger fault as a fault signature.
Masked, the top day is 15 July 2020, which is a reported failure.
[docs/data-quality.md](docs/data-quality.md) has the detection criterion and the block
list.

## Credit

This is analysis built on other people's data and papers. The dataset is by Davari,
Veloso, Ribeiro and Gama at INESC TEC and the University of Porto, under CC BY 4.0;
the agent architecture follows Scott Duncan's
[industrial-ai-troubleshooting-agent](https://github.com/ScottDuncanAI/industrial-ai-troubleshooting-agent),
Apache 2.0, with no code copied. Full citations and the exact debts are in
[ATTRIBUTION.md](ATTRIBUTION.md).

Code and documentation here are MIT. The dataset is not redistributed and keeps its own
licence.
