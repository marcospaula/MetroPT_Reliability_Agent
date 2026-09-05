#!/usr/bin/env python3
"""Decide whether the logging gaps are non-operating time or lost logging.

It matters: the answer moves the MTBF by 22 percent (43.8 d against 53.3 d).

The test does not need a label. If the APU is idle at the hours when the gaps
fall, the gaps are parked time and logged time is the right exposure. If the APU
is working at those hours, the gaps are lost telemetry and calendar time is closer
to the truth.

Idle is read from Motor_current, whose levels the primary source documents:
0 A off, 4 A offloaded, 7 A under load, 9 A starting.

    python3 scripts/exposure.py
"""
import numpy as np
import pandas as pd

CSV = "data/raw/MetroPT3(AirCompressor).csv"
GAP_S = 60          # a gap is any step longer than this
RUN_A = 2.0         # motor current above this means the motor is turning


def main():
    df = pd.read_csv(CSV, usecols=["timestamp", "Motor_current", "COMP"],
                     parse_dates=["timestamp"])
    t = df.timestamp
    step = t.diff().dt.total_seconds()

    gaps = pd.DataFrame({"end": t[step > GAP_S], "sec": step[step > GAP_S]})
    gaps["start"] = gaps.end - pd.to_timedelta(gaps.sec, unit="s")
    print(f"{len(gaps)} gaps over {GAP_S} s, {gaps.sec.sum()/86400:.2f} d total")

    # --- where do the gaps fall, by hour of day? weight by duration
    gap_hours = np.zeros(24)
    for s, e in zip(gaps.start, gaps.end):
        h = pd.date_range(s.floor("h"), e.ceil("h"), freq="h")
        for a, b in zip(h[:-1], h[1:]):
            gap_hours[a.hour] += (min(e, b) - max(s, a)).total_seconds()

    # --- is the machine running, by hour of day? from the logged samples only
    df["running"] = df.Motor_current > RUN_A
    by_hour = df.groupby(t.dt.hour).running.mean()
    logged_hours = df.groupby(t.dt.hour).size() * 10.0   # 10 s per sample

    print(f"\n{'h':>3} {'gap (d)':>9} {'logged (d)':>11} {'gap share':>10} {'running':>9}")
    for h in range(24):
        print(f"{h:>3} {gap_hours[h]/86400:9.2f} {logged_hours[h]/86400:11.2f}"
              f" {gap_hours[h]/(gap_hours[h]+logged_hours[h]):9.1%} {by_hour[h]:9.1%}")

    night = [0, 1, 2, 3, 4]
    day = [h for h in range(24) if h not in night]
    print(f"\nnight {night}: {gap_hours[night].sum()/86400:.2f} d of gap"
          f" ({gap_hours[night].sum()/gap_hours.sum():.0%} of all gap time)")
    print(f"  running while logged, night {df[t.dt.hour.isin(night)].running.mean():.1%}"
          f"  vs day {df[t.dt.hour.isin(day)].running.mean():.1%}")

    # --- the decisive test: what is the machine doing in the hour on each side
    #     of a gap? Parked means it winds down before and up after.
    before, after = [], []
    for s, e in zip(gaps.start, gaps.end):
        b = df[(t >= s - pd.Timedelta("1h")) & (t < s)].running
        a = df[(t > e) & (t <= e + pd.Timedelta("1h"))].running
        if len(b) > 60:
            before.append(b.mean())
        if len(a) > 60:
            after.append(a.mean())
    print(f"\nrunning fraction in the hour before a gap: {np.mean(before):.1%}"
          f"  (n={len(before)})")
    print(f"running fraction in the hour after  a gap: {np.mean(after):.1%}"
          f"  (n={len(after)})")
    print(f"running fraction overall while logged:     {df.running.mean():.1%}")


if __name__ == "__main__":
    main()
