# Correction: the 23-24 June "anomaly" is an acquisition freeze

5 September 2026. This repository's most-promoted finding was wrong, and it was found
by an agent reading the repository's own tools, not by its author. What follows is the
correction, what else it invalidates, and the two errors the agent made in the same
report.

## What was claimed

> The largest excursion in the whole series has no maintenance report. On 23 and 24
> June the unit cycles at 63 per hour, twenty-two times baseline, at 80 % duty, for two
> consecutive days. So the four reports are not a complete list of the anomalies in
> this dataset.

It was in the README headline, in `findings-exposure-and-cycles.md`, in the `kb/` notes,
in the `events_life_table` tool's own warning text, and in the citation abstract.

## What it actually is

Between **22 Jun 15:06:11 and 25 Jun 05:08:35**, `TP2`, `TP3`, `Reservoirs`,
`Motor_current` and `Oil_temperature` each hold **one single value** across **18,515
consecutive samples**, while `DV_eletric` toggles on a fixed **40 s on / 10 s off**
period. A digital channel stuck on a 50 s square wave manufactures 72 apparent load
cycles per hour out of nothing, and the frozen analogue channels never move to
contradict it.

The acquisition stopped. The compressor did not do anything.

`scripts/freeze.py` finds every such block. There are **ten, over 6.96 days, 3.28 % of
all samples**, and they come in two kinds:

| kind | blocks | signature | effect |
|---|---|---|---|
| cycling freeze | 11 Mar, 20 Apr, 22-25 Jun, 22 Jul | `DV_eletric` square wave at 40/10 s, motor current frozen mid-run (3.7 to 5.6 A) | fabricates 48 to 63 cycles/h |
| static freeze | 13 Apr, 17-18 Apr, 26-28 May, 12 Jun, 21 Jul | `DV_eletric` stuck off, motor current frozen at ~0.04 A | fabricates nothing, but the window is blind |

Three separate dates producing 62.0, 62.7 and 62.7 cycles/h at 79.0, 79.9 and 80.0 %
duty is not a machine. It is the same fault three times.

## Why it survived

The cycle indicator was validated against its own extremes, which is the wrong test.
The days it ranked highest were assumed interesting because they were extreme. Nothing
checked whether the underlying channels were still moving, which is a one-line query:
`nunique()` on the analogue columns.

It is the error this repository's own rules name. It made the method look better: an
indicator that "fires hardest on an episode nobody reported" is a far better story than
one that fires on a logger fault.

## What else it invalidates

**"Two of the four reports are anticipated by the cycle indicator" becomes one.**

Recomputed with the freezes masked:

| report | the week before | verdict |
|---|---|---|
| R1, 18 Apr | **unobservable**: 17 Apr 09:30 to 18 Apr 00:00 is a static freeze, 14.5 h ending at the failure's first minute | absence of evidence, not evidence of absence |
| R1b, 29 May | 4.23/h at D-7, then **declining**: 4.09, 3.76, 3.65, 3.44, 2.94 on the day, 2.48 in the final 6 h | a decaying peak is not anticipation |
| R3, 5 Jun | flat, 2.05 to 2.94 | nothing |
| R4, 15 Jul | 3.03/h at D-1, **5.32/h on the day, 7.10/h in the final six hours at 49.7 % duty** | a real ramp to 2.5x baseline |

The earlier count credited R1b because a best-day-in-window ranking rewards any high day
regardless of direction. R1b's high day is seven days out and the rate falls toward the
event. That is the opposite of a precursor.

**The sampling-coverage claim is qualified.** "100 %, 101 %, 92 % and 100 % of expected
samples, so nothing is hidden by a gap" is true of the failure windows themselves, but
the metric counts samples, and **a frozen channel delivers a full sample count while
carrying no information**. It cannot see the fault that matters most here.

## The result that replaces it, which is better

With the freezes masked, **15 July 2020 ranks first in the entire 205-day series** on
both indicators: 5.32 cycles/h and 89.0 minutes of `LPS`. It is a reported failure. The
top of the indicator is now a real event rather than a logger fault.

One genuine unreported episode does remain, and it is cleaner than 23 June ever was.
On **12 March 2020** the compressor ran **11.7 hours continuously under load** at 58.1 %
duty, the highest in the series, with 1,239 distinct `TP3` values, so the channels were
live. No operator report covers it.

It still does not enter the life table. An event is what the operator's report says it
is, and the life table would hold four events if the signal showed forty.

## Two errors in the agent's report, for the record

The audit was largely right, and every number above was reproduced independently before
being accepted. Two claims in it were not.

**"The calendar clock flips the sign to beta = 0.49, and that two clocks over the same
four events point in opposite directions is the clearest evidence that neither direction
is real."** That sign flip was **a bug in this repository's `reliability_summary`
tool**, which ordered the calendar intervals by their length instead of chronologically,
so the cumulative sum described a process that never happened. Corrected, both clocks
give beta = 1.68. The argument was elegant and rested on nothing.

The lesson cuts both ways. A tool that hands an agent a wrong number will get that
number reported with confidence, and two nearly proportional clocks producing opposite
signs should have triggered suspicion rather than a conclusion.

**"12 March never breached the 7 bar floor."** It did. `TP3` reaches **0.89 bar** that
day and `LPS` is active for **28.3 minutes**. The episode stands; that detail of it does
not.

Two further figures did not reproduce and are not used here: a masked baseline of
"2.73 cycles/h at 15.2 % duty" (measured: 2.87/h and 11.9 %, barely moved from the
unmasked 2.86/h, because ten blocks over 6.96 days cannot shift a 205-day median), and
"14.7 h" of freeze before R1 against a measured 14.5 h block.
