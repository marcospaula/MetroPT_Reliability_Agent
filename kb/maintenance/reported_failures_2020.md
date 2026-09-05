---
synthetic: true
title: The 2020 maintenance reports
component: apu
sources: Data Description_Metro.pdf (UCI zip)
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## The table, reproduced with its defects

| Nr. | start | end | failure | severity | report |
|---|---|---|---|---|---|
| #1 | 18/04/2020 00:00 | 18/04/2020 23:59 | Air leak | High stress | |
| **#1** | 29/05/2020 23:30 | 30/05/2020 06:00 | Air Leak | High stress | Maintenance on **30Apr** at 12:00 |
| #3 | 05/06/2020 10:00 | 07/06/2020 14:30 | Air Leak | High stress | Maintenance on 8Jun at 16:00 |
| #4 | 15/07/2020 14:30 | 15/07/2020 19:00 | Air Leak | High stress | Maintenance on 16Jul at 00:00 |

**Two defects, both in the source, not in transcription.** Two rows are numbered #1 and
there is no #2. The second row records maintenance on 30 April for a failure on 29 May,
a month earlier.

Consequence: two usable repair times out of four (3.25 d and 0.40 d), so **MTTR and
availability cannot be estimated** from this table.

## What the sensor data adds (measured)

For report #3 the machine confirms the record independently: a 21.5 hour logging gap
runs from 07/06 14:19, eleven minutes before the reported failure end, to 08/06 11:48,
just before the recorded 16:00 maintenance. That is the train out of service, visible
in the telemetry without any label.

This is the argument for pairing a maintenance record with on-board data: neither is
complete on its own.

## Sampling coverage during the failures

100 %, 101 %, 92 % and 100 % of expected samples. The events themselves are observable;
nothing is hidden by a gap.
