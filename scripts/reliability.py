#!/usr/bin/env python3
"""Layer 5: the life table and what can honestly be estimated from it.

One APU, repaired and returned to service four times. These are recurrent events on
a single repairable system, so the object is a point process, not a life distribution.
Fitting a Weibull to the interarrival times would assume renewal to as-good-as-new,
which a repaired air leak does not license.

The clock is OPERATING time, not calendar. scripts/exposure.py establishes that the
logging gaps are the machine being off, so 37.9 of the 213.2 calendar days are not
exposure. Every interval below is therefore shorter than its calendar counterpart,
and the failure times are mapped onto the operating-time axis before any test is run.

Writes data/events.csv.

    python3 scripts/reliability.py
"""
import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

CSV = "data/raw/MetroPT3(AirCompressor).csv"
OUT = "data/events.csv"
STEP_S = 10.0
GAP_S = 60.0

# Data Description_Metro.pdf, reproduced with its own defects: two reports are
# numbered #1, there is no #2, and #1b records maintenance a month before the failure.
REPORTS = [
    ("R1",  "2020-04-18 00:00", "2020-04-18 23:59", None,
     "air leak", "high stress", "no maintenance recorded"),
    ("R1b", "2020-05-29 23:30", "2020-05-30 06:00", "2020-04-30 12:00",
     "air leak", "high stress", "source numbers this #1 as well; repair date precedes the failure"),
    ("R3",  "2020-06-05 10:00", "2020-06-07 14:30", "2020-06-08 16:00",
     "air leak", "high stress", ""),
    ("R4",  "2020-07-15 14:30", "2020-07-15 19:00", "2020-07-16 00:00",
     "air leak", "high stress", ""),
]


def operating_clock():
    """Cumulative operating seconds against wall-clock time.

    Every logged sample contributes STEP_S. Gaps contribute nothing.
    """
    t = pd.read_csv(CSV, usecols=["timestamp"], parse_dates=["timestamp"]).timestamp
    step = t.diff().dt.total_seconds().fillna(STEP_S)
    step = step.where(step <= GAP_S, 0.0)      # a gap is not operating time
    return t.values, np.cumsum(step.values)


def to_op_days(when, wall, cum):
    """Operating days elapsed at a wall-clock instant."""
    i = np.searchsorted(wall, np.datetime64(pd.Timestamp(when)))
    i = min(max(i, 0), len(cum) - 1)
    return cum[i] / 86400.0


def laplace(ts, T):
    """Centroid test for trend in a time-truncated point process."""
    n = len(ts)
    return (np.mean(ts) - T / 2) / (T * np.sqrt(1 / (12 * n)))


def crow_amsaa(ts, T):
    """Power-law NHPP shape, MLE for a time-truncated process, with a 90 % CI.

    beta < 1 improving, beta = 1 homogeneous, beta > 1 deteriorating.

    The MLE is biased upward, badly so at small n. The time-terminated unbiased
    estimator multiplies it by (n-1)/n, which at n = 4 removes a quarter of it.
    Reporting the raw MLE here would manufacture a wear-out claim out of four points.
    """
    n = len(ts)
    beta = n / np.sum(np.log(T / np.asarray(ts)))
    unbiased = beta * (n - 1) / n
    lo = beta * chi2.ppf(0.05, 2 * n) / (2 * n)
    hi = beta * chi2.ppf(0.95, 2 * n) / (2 * n)
    return beta, unbiased, lo, hi


def main():
    wall, cum = operating_clock()
    T_op = cum[-1] / 86400.0
    T_cal = (pd.Timestamp(wall[-1]) - pd.Timestamp(wall[0])).total_seconds() / 86400.0
    print(f"window      {pd.Timestamp(wall[0])} to {pd.Timestamp(wall[-1])}")
    print(f"calendar    {T_cal:.2f} d")
    print(f"operating   {T_op:.2f} d   ({T_op/T_cal:.1%} of calendar)\n")

    rows, prev_op, prev_cal = [], 0.0, pd.Timestamp(wall[0])
    for rid, start, end, maint, mode, sev, note in REPORTS:
        s = pd.Timestamp(start)
        op = to_op_days(s, wall, cum)
        rows.append({
            "event": rid, "failure_start": start, "failure_end": end,
            "maintenance": maint or "", "mode": mode, "severity": sev,
            "calendar_days_since_prev": round((s - prev_cal).total_seconds() / 86400, 2),
            "operating_days_since_prev": round(op - prev_op, 2),
            "operating_days_from_start": round(op, 2),
            "censored": 0, "note": note,
        })
        prev_op, prev_cal = op, s
    rows.append({
        "event": "SUSP", "failure_start": str(pd.Timestamp(wall[-1])), "failure_end": "",
        "maintenance": "", "mode": "", "severity": "",
        "calendar_days_since_prev": round((pd.Timestamp(wall[-1]) - prev_cal).total_seconds() / 86400, 2),
        "operating_days_since_prev": round(T_op - prev_op, 2),
        "operating_days_from_start": round(T_op, 2),
        "censored": 1, "note": "window ends with the unit in service; right censored",
    })
    ev = pd.DataFrame(rows)
    ev.to_csv(OUT, index=False)
    print(ev[["event", "calendar_days_since_prev", "operating_days_since_prev",
              "operating_days_from_start", "censored"]].to_string(index=False))
    print(f"\nwrote {OUT}")

    ts = ev.loc[ev.censored == 0, "operating_days_from_start"].values
    n = len(ts)

    print("\n--- trend ---")
    cal_times = np.cumsum(ev.loc[ev.censored == 0, "calendar_days_since_prev"].values)
    for label, times, T in [("calendar", cal_times, T_cal), ("operating", ts, T_op)]:
        U = laplace(times, T)
        p = 2 * (1 - norm.cdf(abs(U)))
        print(f"  Laplace on {label:9s} clock: U = {U:+.3f}, p = {p:.2f}"
              f"  -> {'trend' if abs(U) > 1.96 else 'no trend at 5 %'}")
    b, bu, blo, bhi = crow_amsaa(ts, T_op)
    print(f"  Crow-AMSAA shape: beta = {b:.2f} (MLE), {bu:.2f} bias corrected,"
          f" 90 % CI {blo:.2f} to {bhi:.2f}")
    print("    the CI contains 1, so a homogeneous process is not rejected"
          if blo < 1 < bhi else "    the CI excludes 1")

    print("\n--- repair, not estimable ---")
    down = []
    for rid, start, _end, maint, *_ in REPORTS:
        if maint and pd.Timestamp(maint) > pd.Timestamp(start):
            down.append((rid, (pd.Timestamp(maint) - pd.Timestamp(start)).total_seconds() / 86400))
    for rid, d in down:
        print(f"  {rid}: {d:.2f} d from failure start to recorded maintenance")
    print(f"  usable repair times: {len(down)} of {len(REPORTS)}. R1 has no maintenance"
          " record and R1b's precedes its failure, so MTTR and availability are not"
          " estimable from this table.")

    print("\n--- rate, homogeneous Poisson, time truncated ---")
    for label, T in [("calendar", T_cal), ("operating", T_op)]:
        mtbf = T / n
        lo = 2 * T / chi2.ppf(0.95, 2 * n + 2)
        hi = 2 * T / chi2.ppf(0.05, 2 * n)
        print(f"  {label:9s}: MTBF {mtbf:5.1f} d, 90 % CI {lo:5.1f} to {hi:6.1f} d"
              f"   |  rate {365/mtbf:4.1f}/yr, CI {365/hi:4.1f} to {365/lo:4.1f}")

    print("\n--- what this supports ---")
    print(f"  n = {n} events, one failure mode, one repairable unit.")
    print(f"  The 90 % interval spans a factor of "
          f"{(2*T_op/chi2.ppf(0.05,2*n))/(2*T_op/chi2.ppf(0.95,2*n+2)):.1f}.")
    print("  Reportable: a rate with an interval. Not reportable: a wear-out shape.")


if __name__ == "__main__":
    main()
