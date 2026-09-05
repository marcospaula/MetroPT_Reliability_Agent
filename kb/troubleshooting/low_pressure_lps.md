---
synthetic: true
title: Low pressure and the LPS signal
component: reservoirs
sources: Data Description_Metro.pdf; this repository's measurements
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## What LPS means

`LPS` activates when pressure drops below 7 bar, which is below the 8.2 bar load
trigger and therefore below normal operation.

## How common it is (measured)

**89 of 205 usable days carry some LPS activation.** LPS on its own is not
discriminating: it fires on ordinary days as well as on failure days. What separates
the failures is the *duration*.

Days with the most LPS time: 15 Jul (89.0 min, a reported failure day), 17 Jul (69.0),
8 Jun (52.0, the day after a reported failure ended), 19 May (45.3, unreported),
31 Jul (41.2, unreported).

## Reading it

Use accumulated LPS minutes over a window, not a single activation. And note that low
pressure also follows a period with the machine off: 30 % of logging gaps end with TP3
below 7 bar, because the unit bleeds down while parked. Distinguish a leak under load
from a normal restart after a gap before calling anything a fault.
