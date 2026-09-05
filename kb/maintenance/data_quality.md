---
synthetic: true
title: Data quality notes for this dataset
component: apu
sources: this repository's measurements; Data Description_Metro.pdf
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

Things that will mislead an analysis of MetroPT-3 if they are not known first.

## The file is decimated 10:1

The APU was acquired at 1 Hz (15,169,480 points). The published file carries every tenth
sample, 1,516,948 rows at 0.1 Hz. Both the "1 Hz" and "0.1 Hz" figures in circulation are
correct, at different levels. Timestamp steps are 10 s for 88.2 % of rows, 9 s for 8.5 %
and 12 s for 2.5 %, so the clock is not exact: compute rates per elapsed second, not per
sample.

## 17.8 % of the calendar is not operating time

331 gaps longer than 60 s remove 37.90 days from a 213.17 day window, leaving **175.27
operating days**. These are the machine off, not lost telemetry: TP3 falls monotonically
with gap length (-0.32 bar under 1 h, -5.49 bar over 12 h) and 30 % of gaps end below the
7 bar floor.

Any rate denominated in calendar days is **22 % optimistic**.

## The window runs to September

1 Feb 2020 00:00:00 to **1 Sep 2020 03:59:50**, not "February to August" as usually
described.

## Column names

`TP2 TP3 H1 DV_pressure Reservoirs Oil_temperature Motor_current COMP DV_eletric Towers
MPG LPS Pressure_switch Oil_level Caudal_impulses`

`DV_eletric` is misspelled at origin. Do not silently correct it in code that reads the
file.

## Three datasets share the name

MetroPT-3 is ours: 2020, 15 signals, no GPS, four air-leak reports. MetroPT is 2022,
about 11 M points, with GPS, and three failures including an oil leak. MetroPT-2 is a
third. Papers cite "the MetroPT dataset" without saying which. **Never merge their
failure tables.**
