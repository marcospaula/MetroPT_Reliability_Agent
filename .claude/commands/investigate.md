# Investigate a period

Investigate what the APU was doing over a window the user names, for example a reported
failure, a suspicious day, or "the last week of June".

## Conventions

Same as `apu-status`. Additionally: **do not conclude "failure" from the signal.** The
four reported failures are in `events_life_table`; anything else you find is an
anomalous episode, and should be called that.

## Steps

### 1. Fix the window

Resolve the user's phrasing to explicit timestamps. If they named a reported failure,
get its exact start and end from `events_life_table`.

### 2. Is the machine even running?

Call `historian_gaps` over the period. A drop in activity that is really the unit
parked is the most common false lead on this dataset, and 30 % of gaps end with the
unit depressurised, so a low pressure reading right after a gap is a normal restart.

### 3. Pull the signals

Call `historian_get_tag_data` for `TP3`, `Reservoirs`, `Motor_current`, `DV_eletric`
and `LPS` over the window, bucketed so the request is not capped. Widen
`downsample_minutes` rather than narrowing the window.

Read the load cycle: baseline is 2.86 cycles per operating hour at 11.9 % duty. Note
that at 0.1 Hz a cycle under about 20 s is unresolvable, so short-cycling is
undercounted.

### 4. Locate it on the unit

Call `kg_component` for whatever the signals implicate, to say what it connects to and
what else watches it.

### 5. Check the notes

Call `kb_search` with the symptom. The notes cover the air-leak signature, the LPS
floor, and the data-quality traps.

### 6. Report

Give the user: what the signals did, whether it coincides with a reported failure,
which component the topology implicates, and what would distinguish the remaining
explanations. Be explicit about what the data cannot settle.
