# Data quality in MetroPT-3

What has to be known before an analysis of this dataset is trustworthy. Everything here
is measured from the published CSV
(sha256 `db30ccb4ea402e3c8bf2c99db06e288d4f2a772f6928f9dbe26a920d69793e24`), and each
item names the script that reproduces it.

## Acquisition freezes

`scripts/freeze.py`

Ten blocks, **6.96 days, 3.28 % of all samples**, in which `TP2`, `TP3`, `Reservoirs`,
`Motor_current` and `Oil_temperature` each hold a **single value** for the whole block.
One channel stuck is a sensor fault; all five stuck at once is the acquisition.

They come in two kinds, and only one of them is dangerous:

| kind | blocks | signature | effect on an indicator |
|---|---|---|---|
| **cycling** | 11 Mar, 20 Apr, 22-25 Jun, 22 Jul | `DV_eletric` on a fixed 40 s on / 10 s off square wave, motor current frozen mid-run at 3.7 to 5.6 A | **fabricates 48 to 63 load cycles per hour** |
| static | 13 Apr, 17-18 Apr, 26-28 May, 12 Jun, 21 Jul | `DV_eletric` stuck off, motor current frozen at ~0.04 A | fabricates nothing, but the window is blind |

The longest is 22 Jun 15:06:11 to 25 Jun 05:08:35: **18,515 consecutive samples**, one
value per analogue channel. Three of the cycling blocks produce 62.0, 62.7 and 62.7
cycles/h at 79.0, 79.9 and 80.0 % duty. A machine does not repeat itself to three
decimal places on three dates.

**Any cycle-counting indicator must mask these blocks first.** Unmasked, the three
cycling freezes are the top three days of the entire series, ahead of every reported
failure. A detector trained without masking will learn the freeze as a fault signature
and score brilliantly on nothing.

Masked, the top day of the 205-day series is **15 July 2020**, which is a reported
failure.

The masking barely moves the central tendency: 2.87 cycles/h and 11.9 % duty masked,
against 2.86 and 11.9 % unmasked. Ten blocks over seven days cannot shift a 205-day
median. The damage is entirely at the extremes, which is exactly where an anomaly
detector looks.

**A static freeze sits immediately before failure R1**: 17 Apr 09:30 to 18 Apr 00:00,
14.5 hours, ending at the first minute of the reported failure. R1's approach is
therefore unobservable, and that is absence of evidence, not evidence of absence.

### Why sample-count coverage does not catch this

Coverage during the four failure windows is 100, 101, 92 and 100 % of expected samples,
which reads as clean data. It is not a sufficient check: **a frozen channel delivers a
full sample count while carrying no information**. Check that the channels move, with
`nunique()`, not just that they arrive.

## Non-operating time

`scripts/exposure.py`

**331 gaps longer than 60 s remove 37.90 days** from a 213.17 day window, leaving
**175.27 operating days**. These are the machine off, not lost telemetry:

| gap length | n | total | median change in TP3 | median TP3 on return | returns below 7 bar |
|---|---|---|---|---|---|
| under 1 h | 171 | 1.71 d | −0.32 bar | 8.74 | 7 % |
| 1 to 4 h | 95 | 9.81 d | −1.60 bar | 7.38 | 45 % |
| 4 to 12 h | 50 | 12.22 d | −3.19 bar | 5.21 | 64 % |
| over 12 h | 15 | 14.15 d | −5.49 bar | 3.61 | 87 % |

Monotonic in duration, which is a leak-down curve. A unit whose logger died but which
kept running would return at its operating pressure, not at 3.6 bar.

**Any rate denominated in calendar days is 22 % optimistic.**

Evidence that runs the other way, and it should be stated: there is no wind-down before
a gap. The fraction of logged time with the motor turning in the hour before a gap is
48.8 %, slightly **above** the 45.3 % overall. The cut is abrupt. That is consistent
with the logger losing power together with the unit, but it is not positive evidence,
and taken alone it would point at lost telemetry instead.

## Decimation

The APU was acquired at **1 Hz** (15,169,480 points). The published file carries every
tenth sample: **1,516,948 rows at 0.1 Hz**. The index column steps by exactly 10
throughout. Both the "1 Hz" and "0.1 Hz" figures in circulation are correct, at
different levels.

Timestamp steps are 10 s for 88.2 % of rows, 9 s for 8.5 % and 12 s for 2.5 %, so the
clock is not exact. **Compute rates per elapsed second, not per sample.**

Two consequences:

- A load cycle shorter than about 20 s cannot be resolved. Cycle counts are a **lower
  bound**, and severe short-cycling, the clearest leak signature, is the case most
  likely to be undercounted.
- The documented 9 A start-up current appears in **7 samples out of 1,516,948**. A start
  transient of a few seconds does not survive 10:1 decimation. Do not attempt to detect
  starts in this file, and do not read the absence of 9 A as an absence of starts.

## Defects in the source

The failure table in `Data Description_Metro.pdf` numbers **two reports as #1** and has
no #2, and its second row records maintenance on **30 April for a failure on 29 May**, a
month earlier. Report #1 carries no maintenance record at all.

Consequence: two usable repair times out of four, differing by a factor of eight, so
**MTTR and availability are not estimable** from this dataset.

## Extent, and the column names

The window is **1 Feb 2020 00:00:00 to 1 Sep 2020 03:59:50**, not "February to August"
as usually described.

```
TP2  TP3  H1  DV_pressure  Reservoirs  Oil_temperature  Motor_current
COMP  DV_eletric  Towers  MPG  LPS  Pressure_switch  Oil_level  Caudal_impulses
```

`DV_eletric` is misspelled at origin. Do not silently correct it in code that reads the
file.

## Three datasets share the name

| dataset | period | size | failures | GPS |
|---|---|---|---|---|
| **MetroPT-3**, this one | 1 Feb to 1 Sep 2020 | 1,516,948 rows at 0.1 Hz | 4, all air leak | no |
| MetroPT | Jan to Jun 2022 | ~10,979,547 points | 3: 2 air leak, 1 oil leak | yes |
| MetroPT-2 | not established | not established | not established | not established |

Papers cite "the MetroPT dataset" without saying which, and the sensor definitions do
not carry over cleanly: `H1` means the cyclonic separator filter discharge in the
MetroPT-3 primary source and a 10.2 bar valve in the 2022 paper. **Never merge their
failure tables.**
