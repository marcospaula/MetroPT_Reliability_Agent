# Reliability report

Produce the full layer 5 position on the APU, with the reasoning visible.

## Conventions

Same as `apu-status`: venv python as `<venv-python>`, operating-time clock, and an
event is never an anomaly.

## Steps

### 1. Both clocks, deliberately

Call `reliability_summary` twice, `clock="operating"` and `clock="calendar"`. Show both
and explain the gap: the difference is the 37.9 days the machine was off, and it moves
the MTBF by 22 %. State that the operating figure is the defensible one, and why the
evidence supports that (pressure decays monotonically with gap length; call
`historian_gaps` if the user wants to see it).

### 2. The life table

Call `events_life_table`. Show the four intervals on both clocks and the censored
suspension. Explain that the suspension is data, not a missing observation.

### 3. The model choice

Explain, do not just assert: one repairable unit repaired four times is a point
process, not a sample of lifetimes, so a Weibull fit would assume a renewal that
patching a leak does not license. Give the Laplace result and the bias-corrected
Crow-AMSAA shape with its interval.

**Refuse to report a wear-out shape.** If the user asks for a beta, give the interval
and say what it covers.

### 4. What cannot be estimated

MTTR and availability. Say why: one report has no maintenance record and another's
precedes its own failure.

### 5. Optional context

If the user wants the signal side, call `kb_search` for "air leak signature" and report
that the cycle indicator anticipates two of the four events, and fires hardest on an
episode with no report at all.
