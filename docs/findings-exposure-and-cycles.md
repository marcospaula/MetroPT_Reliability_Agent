# Exposure and the cycle hypothesis

5 September 2026. Two questions, both answered from the file with no label used until
the last step. Scripts: `scripts/exposure.py`, `scripts/cycles.py`.

## 1. The gaps are non-operating time. Logged time is the right exposure

This was worth 22 % on the MTBF, so it needed a real test rather than a plausible story.

**The first test was inconclusive and I nearly read it the wrong way.** Gap time
concentrates at night (33 to 37 % of the hours 00:00 to 04:00 are missing, against
about 10 % during the day), which suggests a parked train. But the fraction of logged
time with the motor turning is flat across all 24 hours, 42.8 % to 47.8 %, and in the
hour before a gap it is 48.9 %, slightly **above** the 45.3 % overall. No wind-down.
Taken alone that argues for lost telemetry, which would have made calendar time the
right exposure and pushed the MTBF back up to 53 d.

**The physical test settles it.** If the unit is parked and off, it bleeds down during
the gap; if it is running and only the telemetry is lost, pressure returns where it
left off. TP3 across the gap, by gap duration:

| gap length | n | median change in TP3 |
|---|---|---|
| under 1 h | 171 | −0.32 bar |
| 1 to 4 h | 95 | −1.60 bar |
| 4 to 12 h | 50 | −3.19 bar |
| over 12 h | 15 | −5.49 bar |

Monotonic in duration, which is a leak-down curve. Thirty per cent of gaps end with TP3
below the 7 bar LPS floor, so the unit comes back depressurised. The gaps are the
machine being off.

**Conclusion: exposure is the 175.27 d of logged time, not the 213.17 d of calendar.
MTBF 43.8 d, 90 % interval 19.1 to 128.3 d.**

**A test I ran that was worthless.** I looked for the documented 9 A start-up current
after each gap and found it in none of them, and briefly took that as evidence. It is
not: 9 A appears in **7 samples out of 1,516,948** in the entire series. A start
transient of a few seconds cannot survive the 10:1 decimation, so the base rate of
catching one is zero and the test could only ever return zero. Absence of the start
signature says nothing here.

## 2. The cycle indicator responds, but it does not match the four reports

The hypothesis: an air leak makes the APU reach the 8.2 bar load trigger sooner, so
load cycles per operating hour and duty should rise before a failure. Cycles are rising
edges of `DV_eletric`, denominated in logged hours, over the 205 days with more than
6 h of logging.

Baseline is a very quiet machine: **2.86 load cycles per hour, duty 11.9 %**,
p10 to p90 of 1.80 to 3.86.

The indicator is not noise. It moves by more than an order of magnitude:

| day | cycles/h | duty | TP3 min | near a report? |
|---|---|---|---|---|
| 23 Jun | 63.26 | 79.8 % | 8.51 | **no** |
| 24 Jun | 62.53 | 80.0 % | 8.51 | **no** |
| 20 Apr | 48.48 | 63.4 % | 8.09 | 2 d after #1 |
| 22 Jun | 24.70 | 37.4 % | 4.47 | **no** |
| 22 Jul | 16.56 | 27.0 % | 7.84 | 7 d after #4 |
| 25 Jun | 14.06 | 25.0 % | 7.90 | **no** |
| 21 Apr | 5.50 | 11.4 % | 8.04 | 3 d after #1 |
| 15 Jul | 5.32 | 48.1 % | 5.93 | **is #4** |

Bringing the held-out dates back in, the week before each report:

| report | cycles/h in the week before | best daily rank of 205 |
|---|---|---|
| #1, 18 Apr | 0.04 to 2.59 | 120 |
| #1b, 29 May | 0.00 to 4.23 | 12 |
| #3, 5 Jun | 1.28 to 2.94 | 96 |
| #4, 15 Jul | 3.03 to 5.32 | **8** |

**WITHDRAWN.** Recomputed with the acquisition freezes masked, it is **one of four**:
only R4 shows a real approach. R1b's high day is seven days out and the rate *falls*
toward the event; R1 is unobservable behind a 14.5 h freeze. See
`correction-freeze-2026-09-05.md`.

The low pressure signal tells the same story with a different split. LPS minutes in the
+/- 3 day window: #4 has 206.8, #3 has 118.8, while #1 has 14.8 and #1b has 10.0. But
89 of 205 days carry some LPS activation, so on its own it is not discriminating.

## WITHDRAWN: "the finding that was not on the agenda"

> This section claimed that the largest excursion in the series, 23-24 June 2020 at 22
> times baseline, carried no maintenance report, and concluded that the four labels are
> not exhaustive.

**The excursion is an acquisition freeze, not an event.** Five analogue channels hold one
value each across 18,515 consecutive samples while `DV_eletric` toggles on a fixed 40 s /
10 s square wave, which manufactures the cycles. It repeats on ten blocks over 6.96 days.

The conclusion happens to survive on other evidence (12 March 2020 is a genuine
unreported episode on live channels), but the evidence offered for it here was wrong, and
the error made the method look better than it was. Full account, including what else it
invalidates and the two errors in the audit that caught it, in
`correction-freeze-2026-09-05.md`. Detector in `scripts/freeze.py`.

The table above, "two of four anticipated", is also withdrawn: it is **one of four**.

## Caveats that limit both results

- **The 10:1 decimation caps cycle resolution.** At 0.1 Hz a cycle shorter than about
  20 s cannot be resolved, and 63 cycles/h already means one every 57 s, about six
  samples per cycle. Cycle counts are a lower bound, and short-cycling is the failure
  signature most likely to be undercounted. The 1 Hz original would not have this
  problem.
- The documented current levels do not match the data cleanly. The source names 0, 4,
  7 and 9 A; the running distribution sits mostly at 3 to 6 A with a median of about
  5.7 A when turning. The 4 A and 7 A labels are nominal, not thresholds to code
  against.
- Days with under 6 h logged are dropped, which is a choice that could be revisited.

## What this changes for layer 5

The bridge from signal to event is real but weak at this sample size. Honest framing
for anything published: the indicator responds strongly and physically, it precedes
one of the four reports clearly and one marginally, and it fires hardest on an episode
nobody reported. Four events cannot separate those readings.
