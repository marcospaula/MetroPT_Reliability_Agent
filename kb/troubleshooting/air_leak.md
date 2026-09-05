---
synthetic: true
title: Air leak: what it looks like in the data
component: apu
sources: this repository's measurements; Data Description_Metro.pdf
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## Signature

An air leak should show as a **shortened load cycle**: pressure falls to the 8.2 bar
trigger sooner, so cycles per operating hour and duty both rise. Severe cases pull the
reservoir below the 7 bar floor and activate `LPS`.

## What the four reported events actually show (measured)

Mixed, and this is stated honestly rather than smoothed:

| report | load cycles in the week before | LPS minutes, +/- 3 days |
|---|---|---|
| 18 Apr 2020 | 0.04 to 2.59 /h, below the 2.86 baseline | 14.8 |
| 29 May 2020 | 0.00 to 4.23 /h, best day ranked 12 of 205 | 10.0 |
| 5 Jun 2020 | 1.28 to 2.94 /h, unremarkable | 118.8 |
| 15 Jul 2020 | 3.03 to 5.32 /h, best day ranked 8 of 205 | 206.8 |

Two of four are anticipated by the cycle indicator; the two long-duration events are
flagged by LPS instead. With four events none of this is a demonstration.

## The unreported episode

The largest excursion in the entire series, **23 and 24 June 2020**, runs at 63 load
cycles per hour, twenty-two times baseline, at 80 % duty for two consecutive days, with
a run-up on 22 June and a tail on 25 June. **No maintenance report covers it.**

Treat the four reports as a partial list, not as exhaustive ground truth. An algorithm
that fires on 23 June is not necessarily producing a false positive.
