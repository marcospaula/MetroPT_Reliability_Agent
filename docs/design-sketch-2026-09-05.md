# Design sketch: a reliability agent for the Metro do Porto APU

5 September 2026. A design document, not an implementation. Nothing has been
downloaded and nothing has been measured. Everything below is an assumption until
the final section has been carried out.

## 1. The thesis

The CFB boiler repository shows that an agent can be attached to four plant data
sources (historian, alarms, topology graph, documents) and produce traceable root
cause diagnosis. What it does not do, and cannot do with that data, is reliability:
five consecutive days, no failure, no repair. What it calls an anomaly is a KPI band
excursion.

MetroPT-3 changes that in three ways:

1. **Real equipment in service**, not a test rig and not a simulation.
2. **Seven months** of continuous operation at 1 Hz, not five days.
3. **Dated failures** from the operator, with the window ending while the equipment
   is still running, which gives natural right censoring.

So the thesis is: reproduce the diagnostic architecture and **add the missing layer**,
tying signal to event. The boiler agent answers "what is happening now". This one
answers "what is happening now, and what it is doing to the life of the asset".

## 2. Architecture, 4+1 layers

The first four mirror the original repository. The fifth is the contribution.

| # | layer | in the boiler repo | here |
|---|---|---|---|
| 1 | historian | DuckDB, 86,400 readings, 30 tags, 5 s | DuckDB, ~1.5 M readings, 15 signals, 1 Hz, 7 months |
| 2 | event log | 6,005 alarms **generated** by an ISA-18.2 state machine | **real** operator failures, plus derived alarms if documented setpoints exist |
| 3 | graph | boiler topology, hand written | APU topology, to be written |
| 4 | documents | written by the author, reading like plant documents | synthetic and **labelled as such** |
| 5 | **reliability** | does not exist | life table, censoring, fitted with ranges |

### Layer 5 in detail

It is the only part with no precedent in the original repository, so it carries both
the risk and the value.

- **Life table.** Each operator failure closes an interval; the end of the window opens
  a suspension. The unit of analysis is still to be decided: the compressor as a whole,
  or the failure mode (the literature describes air leaks).
- **Scarce events are the normal case, not the exception.** Seven months of one APU do
  not produce dozens of failures.
  > **Corrected 06/09 (see findings-2026-09-06.md).** This originally said the scarcity
  > pushes towards Weibayes. It does not. There is one APU repaired four times, so these
  > are recurrent events on a single repairable unit, not independent lifetimes, and a
  > Weibull fit would assume a renewal that a repaired air leak does not license. The
  > route is: trend test first, then the model. The Laplace statistic is +0.50, so a
  > homogeneous Poisson process stands and the answer is an MTBF interval, not a beta.
- **The bridge back to the signal.** The interesting question is not fitting a Weibull.
  It is whether the signal anticipates the event: is there an indicator that separates
  the week before a failure from the rest of the series? If there is, effective age
  stops being calendar time.

## 3. What carries over from the boiler repository, and what does not

**Carries over:** the MCP pattern with one tool per source; the stdio server; the
auditable investigation trace format; the idea of high-level commands; the separation
between a tool that reads data and an agent that reasons.

**Does not carry over:** none of the physics. A boiler is a thermal process with a
temperature control loop. An APU is a reciprocating machine with a load and unload
cycle. The graph, the documents and the limits are all new.

**Carries over with a caveat:** `generate_alarms.py`. Generating alarms from a state
machine only makes sense if documented APU setpoints exist. If they do not, invented
alarms become noise competing with the real failures. In that case layer 2 keeps only
the real events, and it is better that way.

## 4. Two traps already identified

**Confusing event with anomaly.** This is the mistake the repository exists to avoid.
An anomaly detector will flag hundreds of stretches. None of them is a failure. A
failure is what the operator's report says it is. If those two columns ever mix, the
life table inflates and the reliability estimate becomes optimistic or pessimistic
with no way to tell which. They stay in separate tables, under different names, from
day one.

**Synthetic documents that look real.** The boiler repository writes datasheets and
procedures that read like plant documents. For a demonstration that is fine; for a
public method artefact it is a problem, because someone will eventually cite a
"datasheet" figure that no one ever issued. Here every generated document carries a
synthetic header.

## 5. Before writing code

Not a single line before these five items are closed, in order. Item 2 decides whether
the project exists at all. Progress is tracked in `findings-2026-09-06.md`.

1. **Download and inspect the CSV.** Real column names, units, effective rate, gaps.
   The "7 analogue, 8 digital" split came from a description, not from reading the file.
2. **Find the primary source of the failure dates.** How many events, of which mode, at
   what time resolution. **If fewer than three usable events exist, layer 5 does not
   hold** and the project has to be rescoped to detection, which would make it a copy
   of the boiler repository without the new part. This is the stopping point.
   **Closed 06/09: four events, all air leak. The gate passes.**
3. **Count the censoring.** How much failure-free operating time the window contains.
4. **Establish the APU topology.** Compressor, motor, oil separator, dryer, towers,
   intake valves, reservoir. From a public source, not invented.
5. **Decide the unit of analysis** for the life table: asset or failure mode.

## 6. Open questions

- Public or private? The licence allows public release, and the value of the artefact
  lies in being public, but that can wait until layer 5 proves it holds together.
- Is it worth contributing back to Scott's repository? His contribution section asks
  for exactly this: "build on top of a different dataset".

Language is settled: English throughout, as in `ten-degree-rule`.
