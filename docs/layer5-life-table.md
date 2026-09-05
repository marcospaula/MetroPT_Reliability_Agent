# Layer 5: the life table

5 September 2026. Built by `scripts/reliability.py`, which writes `data/events.csv`.
This is the layer the boiler repository cannot have, and the point of the project.

## The object

One APU, repaired and returned to service four times, observed until the window ends
with the unit still running. That is a **point process on a single repairable system**,
not a sample of independent lifetimes. The distinction decides the whole analysis:

- A Weibull fit to the four interarrival times would assume every repair returned the
  unit to as-good-as-new. Patching an air leak does not do that.
- So the sequence is: choose the clock, test for trend, then pick a model. Not: fit a
  distribution and interpret its shape.

## The clock is operating time

`docs/data-quality.md` shows the logging gaps are the machine off, not lost telemetry,
so 37.9 of the 213.2 calendar days are not exposure. The failure instants are mapped
onto a cumulative operating-time axis before any test runs.

| event | calendar since previous | **operating since previous** | operating from start | |
|---|---|---|---|---|
| R1, 18 Apr | 77.00 d | **64.65 d** | 64.65 d | |
| R1b, 29 May | 41.98 d | **32.37 d** | 97.02 d | |
| R3, 5 Jun | 6.44 d | **5.74 d** | 102.77 d | |
| R4, 15 Jul | 40.19 d | **32.72 d** | 135.49 d | |
| suspension, 1 Sep | 47.56 d | **39.78 d** | 175.27 d | right censored |

Every interval shrinks by roughly 18 %, and the suspension is carried explicitly. The
window ending with the unit in service is data, not a missing observation.

## Trend: none detectable

| test | result | reading |
|---|---|---|
| Laplace, calendar clock | U = +0.493, p = 0.62 | no trend at 5 % |
| Laplace, operating clock | U = +0.488, p = 0.63 | no trend at 5 % |
| Crow-AMSAA shape | beta = 1.68 MLE, **1.26 bias corrected**, 90 % CI 0.57 to 3.26 | interval contains 1 |

Two things are worth stating rather than assuming.

**The clock barely moves the trend test.** U shifts from +0.493 to +0.488. That is not
luck: the gaps are spread fairly evenly through the window, so removing them rescales
the axis without displacing the events relative to each other. The conclusion is robust
to the exposure question even though the *rate* is not.

**The raw Crow-AMSAA shape is a trap at this sample size.** The MLE of 1.68 reads as
deterioration and would be reported as such by anyone who stopped there. It is biased
upward; the time-terminated unbiased estimator is 1.26, and the 90 % interval runs from
0.57 to 3.26. That interval covers strong improvement through strong wear-out. It says
nothing, and saying nothing is the correct output of four events.

## Rate

| clock | MTBF | 90 % interval | rate |
|---|---|---|---|
| calendar, 213.2 d | 53.3 d | 23.3 to 156.0 d | 6.8 /yr |
| **operating, 175.3 d** | **43.8 d** | **19.1 to 128.3 d** | **8.3 /yr, CI 2.8 to 19.1** |

The operating-time row is the answer. The interval spans a factor of 6.7, and that
factor **is** the deliverable. A single number here would be a fiction with three
significant figures.

## Repair and availability: not estimable

| event | failure start to recorded maintenance |
|---|---|
| R1 | no maintenance record at all |
| R1b | the source dates it 30 April, a month **before** the 29 May failure |
| R3 | 3.25 d |
| R4 | 0.40 d |

Two usable repair times out of four, differing by a factor of eight. MTTR is not
estimable, so neither is availability. This is reported as a gap in the source, not
patched with an assumption.

It is worth noting what the sensor data says about R3 independently: a 21.5 h logging
gap runs from 07/06 14:19, eleven minutes before the reported failure end, to 08/06
11:48, just before the recorded 16:00 maintenance. The machine confirms the report.
That the on-board data can reconstruct a downtime the maintenance record states only
partially is the whole argument for pairing the two sources.

## What layer 5 supports, and what it does not

**Supports:** a failure rate for air leaks on this APU, on an operating-time basis,
with a published interval. A statement that no trend is detectable. An explicit
censoring term. A demonstration that the exposure choice moves the rate by 22 % while
leaving the trend conclusion intact.

**Does not support:** any wear-out claim, any beta, any remaining useful life, any
availability figure, and any comparison against a fleet.

The honest headline is a range and a negative: **roughly one air leak every 44 days of
operation, somewhere between 19 and 128 days at 90 % confidence, with no detectable
trend over seven months.**

## Open

- The unreported episode of 12 March 2020, 11.7 h continuously under load on live
  channels, is not in this life table, because a life table is built from reported
  failures and repairs. If it were a fifth failure the rate is understated by 25 %.
  See `signal-and-events.md`. Do not mistake the apparent June excursion for a
  candidate: it is an acquisition freeze, per `data-quality.md`.
- R1b's repair date. One character in the source, and it decides whether availability
  can ever be computed from this table.
