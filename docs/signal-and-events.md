# Does the signal anticipate the failure?

The question layer 5 exists to ask. Reproduced by `scripts/cycles.py`, with the
acquisition freezes masked per `docs/data-quality.md`.

## The hypothesis, and why it is testable without labels

An air leak makes the APU lose pressure faster, so it reaches the documented 8.2 bar
load trigger sooner: **more load cycles per operating hour, at a higher duty**. A load
cycle is a rising edge of `DV_eletric`. Nothing about that needs a label.

Baseline over the 205 days with more than six hours of logging: **2.87 cycles per
operating hour, 11.9 % duty**, p10 to p90 of 1.80 to 3.86.

## What the four reported events show

| report | the week before | LPS minutes, +/- 3 d |
|---|---|---|
| R1, 18 Apr | **unobservable**: a 14.5 h static freeze ends at the failure's first minute | 14.8 |
| R1b, 29 May | 4.23/h seven days out, then declining: 4.09, 3.76, 3.65, 3.44, 2.94 on the day, 2.48 in the final 6 h | 10.0 |
| R3, 5 Jun | flat, 2.05 to 2.94/h | 118.8 |
| R4, 15 Jul | 3.03/h at D-1, **5.32/h on the day, 7.10/h in the final six hours at 49.7 % duty** | 206.8 |

**One of four shows a real approach**, and it is R4: a ramp to 2.5 times baseline inside
the last six hours before the reported window opens.

R1b must not be counted. Its high day is seven days out and the rate *falls* toward the
event, which is the opposite of a precursor. A best-day-in-window ranking will credit it
anyway, because such a ranking rewards any high day regardless of direction; use the
direction, not the maximum.

R1 is blind behind a freeze. That is absence of evidence, and must not be recorded as
evidence of absence.

With the freezes masked, **15 July ranks first in the whole series on both indicators**,
5.32 cycles/h and 89.0 minutes of `LPS`, and it is a reported failure.

## LPS on its own does not discriminate

`LPS` activates below 7 bar. **89 of 205 usable days carry some activation**, so it fires
on ordinary days too. What separates the failure days is accumulated duration, not
occurrence.

And 30 % of logging gaps end with `TP3` below 7 bar, because the unit bleeds down while
parked. Distinguish a leak under load from a normal restart after a gap before calling
anything a fault.

## An unreported episode

**12 March 2020.** The compressor runs **11.7 hours continuously under load**, 58.1 %
duty for the day, the highest in the series. The channels are live: 1,239 distinct `TP3`
values, no frozen block. `TP3` falls to 0.89 bar and `LPS` is active 28.3 minutes. No
operator report covers it.

It is an **anomalous episode**, detected from the signal. It does not enter the life
table, which holds four events because there are four operator reports and would hold
four if the signal showed forty.

## What this supports

The bridge from signal to event is real but weak at n = 4. The honest statement is that
the indicator is physical, responds by more than an order of magnitude, precedes one of
four reports clearly, and that four events cannot separate that from coincidence.

The resolution limit matters here: at 0.1 Hz a cycle under about 20 s is unresolvable,
so short-cycling, the sharpest leak signature, is undercounted. The 1 Hz original would
not have this problem.
