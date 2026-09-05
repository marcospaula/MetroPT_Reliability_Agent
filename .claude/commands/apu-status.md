# APU status

Give the user an orientation on the MetroPT-3 APU dataset and this repository's
findings, in a form they can act on.

## Conventions

- **Python:** always the project venv, written as `<venv-python>` below. Substitute
  `.venv/bin/python`.
- **Rates are denominated in operating time**, never calendar. A calendar denominator
  is 22 % optimistic on this dataset. Say which clock any number uses.
- **An event is not an anomaly.** The life table holds only the operator's four
  reports. Never add something detected from the signal to it.

## Steps

### 1. Establish the extent of the data

Call `historian_window`. Report the span, the operating days, and the share of the
calendar that is the machine off.

If it errors because `data/metropt.duckdb` is missing, tell the user to run:

```
<venv-python> scripts/reliability.py
<venv-python> scripts/ingest.py
```

and that `scripts/ingest.py` needs `data/raw/`, per `data/README.md`.

### 2. The signals

Call `historian_tags`. Summarise the seven analogue and eight digital tags and the
documented thresholds. Mention that `DV_eletric` is misspelled at origin.

### 3. The reliability position

Call `reliability_summary` with `clock="operating"`. Report the MTBF **with its
interval**, and the trend result. Do not present the Crow-AMSAA point estimate as
evidence of wear-out: the tool returns the interval and a `do_not` field, and both
belong in the answer.

### 4. What is unresolved

Call `events_life_table` and surface the two defects in the source, the `do_not_use`
field about the 23-24 June acquisition freeze, and the genuine unreported episode of
12 March 2020.

Also state the decimation caveat when reporting `Motor_current`: the documented 9 A
start level appears in 7 samples out of 1,516,948, because a start transient cannot
survive the 10:1 decimation. Do not let a reader plan to detect starts.

Close with the one-line position: about one air leak every 44 operating days, between
19 and 128 at 90 % confidence, no detectable trend, and MTTR not estimable.
