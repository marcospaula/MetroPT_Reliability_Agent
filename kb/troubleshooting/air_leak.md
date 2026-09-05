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

## Mask the acquisition freezes first

Ten blocks over 6.96 days are the logging chain standing still, not the machine. In four
of them `DV_eletric` toggles on a fixed 40 s / 10 s square wave, which manufactures up to
63 load cycles per hour out of nothing. `scripts/freeze.py` finds them; `docs/data-quality.md` lists them. An indicator
computed without masking them ranks the freezes above every real event.

## What the four reported events show, with the freezes masked (measured)

| report | the week before | LPS minutes, +/- 3 days |
|---|---|---|
| 18 Apr 2020 | **unobservable**: a 14.5 h static freeze ends at the failure's first minute | 14.8 |
| 29 May 2020 | 4.23/h seven days out, then **declining** to 2.94/h on the day | 10.0 |
| 5 Jun 2020 | flat, 2.05 to 2.94/h | 118.8 |
| 15 Jul 2020 | **5.32/h on the day, 7.10/h in the final six hours at 49.7 % duty** | 206.8 |

**One of four** shows a real approach, and it is R4. R1b was previously counted because a
best-day-in-window ranking rewards any high day regardless of direction; its peak decays
toward the event, which is the opposite of a precursor. R1 is blind, and absence of
evidence must not be recorded as evidence of absence.

With the freezes masked, **15 July ranks first in the whole 205-day series** on both
indicators, and it is a reported failure.

## The unreported episode

**12 March 2020**: the compressor runs **11.7 hours continuously under load** at 58.1 %
duty, the highest in the series, with 1,239 distinct `TP3` values, so the channels were
live. `TP3` falls to 0.89 bar and `LPS` is active 28.3 minutes. No report covers it.

Treat the four reports as a partial list, not as exhaustive ground truth. But **check for
a freeze before calling anything an episode**: the three largest apparent excursions in
this dataset are the acquisition standing still, not the machine.
