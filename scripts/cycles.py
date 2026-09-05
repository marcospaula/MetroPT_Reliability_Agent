#!/usr/bin/env python3
"""Does the load cycle shorten before a failure?

The thesis of layer 5. An air leak makes the APU lose pressure faster, so it should
hit the 8.2 bar load trigger sooner: more load cycles per operating hour, and a
higher duty. If that shows up before the four documented events, the signal
anticipates the failure and effective age stops being calendar time.

No label is used. The failure dates are held out and only compared at the end.

Denominators are logged time, never calendar: scripts/exposure.py establishes that
the gaps are non-operating time.

WARNING, and the reason scripts/freeze.py exists: this script does NOT mask the ten
acquisition freezes, so its ranking is wrong at the top. Four of those blocks hold a
40 s / 10 s square wave on DV_eletric that fabricates up to 63 cycles per hour, which
this script once reported as the largest anomaly in the dataset. Run freeze.py and use
its mask before trusting any extreme here. Kept unchanged so the error is reproducible;
see docs/correction-freeze-2026-09-05.md.

    python3 scripts/cycles.py
"""
import numpy as np
import pandas as pd

CSV = "data/raw/MetroPT3(AirCompressor).csv"
STEP_S = 10.0

# The four reports from Data Description_Metro.pdf. Held out until the last block.
FAILURES = [("#1",  "2020-04-18 00:00"), ("#1b", "2020-05-29 23:30"),
            ("#3",  "2020-06-05 10:00"), ("#4",  "2020-07-15 14:30")]


def load():
    df = pd.read_csv(CSV, usecols=["timestamp", "DV_eletric", "TP3", "Motor_current"],
                     parse_dates=["timestamp"]).set_index("timestamp")
    df["under_load"] = df.DV_eletric > 0.5
    df["logged_s"] = STEP_S
    # a cycle is a rising edge into load
    df["cycle_start"] = df.under_load & ~df.under_load.shift(1, fill_value=False)
    return df


def daily(df):
    g = df.resample("D")
    out = pd.DataFrame({
        "logged_h": g.logged_s.sum() / 3600.0,
        "cycles": g.cycle_start.sum(),
        "load_h": (g.under_load.sum() * STEP_S) / 3600.0,
        "tp3_min": g.TP3.min(),
        "tp3_med": g.TP3.median(),
    })
    out = out[out.logged_h > 6]                     # drop days barely logged
    out["cycles_per_h"] = out.cycles / out.logged_h
    out["duty"] = out.load_h / out.logged_h
    return out


def main():
    df = load()
    d = daily(df)
    print(f"{len(d)} days with more than 6 h logged, "
          f"{d.logged_h.sum()/24:.1f} d of logged time\n")

    base_c, base_d = d.cycles_per_h.median(), d.duty.median()
    print(f"baseline (median day): {base_c:.2f} load cycles/h, duty {base_d:.1%}")
    print(f"spread: cycles/h p10 {d.cycles_per_h.quantile(.1):.2f} "
          f"p90 {d.cycles_per_h.quantile(.9):.2f}\n")

    print("the ten days with the most load cycles per logged hour:")
    top = d.nlargest(10, "cycles_per_h")
    for ts, r in top.iterrows():
        print(f"  {ts:%d %b}  {r.cycles_per_h:5.2f} /h   duty {r.duty:5.1%}"
              f"   logged {r.logged_h:4.1f} h   TP3 min {r.tp3_min:5.2f}")

    print("\nnow bringing in the held-out failure dates:")
    for name, when in FAILURES:
        f = pd.Timestamp(when)
        pre = d[(d.index >= f.normalize() - pd.Timedelta("7D")) & (d.index <= f.normalize())]
        if pre.empty:
            print(f"  {name}: no logged days in the week before")
            continue
        rank = [int((d.cycles_per_h > v).sum()) + 1 for v in pre.cycles_per_h]
        print(f"  {name} {f:%d %b}: week before, cycles/h "
              f"{pre.cycles_per_h.min():.2f} to {pre.cycles_per_h.max():.2f} "
              f"(baseline {base_c:.2f}), best rank {min(rank)} of {len(d)}")
    hits = sum(ts.normalize() in [pd.Timestamp(w).normalize() for _, w in FAILURES]
               or any(abs((ts - pd.Timestamp(w)).days) <= 7 for _, w in FAILURES)
               for ts in top.index)
    print(f"\nof the 10 highest-cycle days, {hits} fall within 7 days of a failure")


if __name__ == "__main__":
    main()
