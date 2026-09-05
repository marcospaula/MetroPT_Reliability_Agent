---
synthetic: true
title: Load and unload control
component: apu
sources: Data Description_Metro.pdf (UCI zip)
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## The control is a cycle, not a loop

Unlike a boiler with a modulating temperature setpoint, the APU cycles between states.
`MPG` starts the compressor under load when APU pressure falls below **8.2 bar**;
`COMP`, the intake valve signal, follows it. `H1` relates to the cyclonic separator
filter discharge. `LPS` marks pressure below **7 bar**.

| signal | threshold | meaning |
|---|---|---|
| MPG | below 8.2 bar | intake valve opens, compressor goes under load |
| LPS | below 7.0 bar | low pressure signal |
| Motor_current | ~0 / ~4 / ~7 / ~9 A | off / offloaded / under load / starting |
| DV_pressure | equal to zero | compressor working under load |

## Why the cycle is the diagnostic

An air leak makes the unit lose pressure faster, so it reaches the 8.2 bar trigger
sooner: **more load cycles per operating hour, at a higher duty**. That is testable
without any label, and it is the indicator this repository uses.

## Measured baseline (this repository)

Over the 205 days with more than six hours of logging: **2.86 load cycles per operating
hour, duty 11.9 %**, with p10 to p90 of 1.80 to 3.86 cycles per hour. A load cycle is
counted as a rising edge of `DV_eletric`.

**Resolution limit.** At the published 0.1 Hz a cycle shorter than about 20 s cannot be
resolved. Cycle counts are therefore a lower bound, and severe short-cycling is exactly
the case most likely to be undercounted.
