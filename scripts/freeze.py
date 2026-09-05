#!/usr/bin/env python3
"""Find the acquisition freezes, which look exactly like a failing compressor.

The 23-24 June 2020 excursion, 22 times the baseline load-cycle rate for two days,
reads as the largest anomaly in the series. It is not an anomaly. It is the
acquisition standing still.

The signature, on 22 Jun 15:06:11 to 25 Jun 05:08:35: TP2, TP3, Reservoirs,
Motor_current and Oil_temperature each hold ONE value across 18,515 consecutive
samples, while DV_eletric toggles on a fixed 40 s on / 10 s off period. A frozen
digital channel with a 50 s period produces 72 apparent load cycles per hour out of
nothing, and the analogue channels never move to contradict it.

It repeats. Fifteen days carry frozen blocks, so this is a recurring fault of the
logging chain and not a one-off.

Any indicator built on cycle counting must mask these blocks first. A detector
trained without masking will learn the freeze as a fault signature and score
brilliantly on nothing.

    .venv/bin/python scripts/freeze.py
"""
import pandas as pd

CSV = "data/raw/MetroPT3(AirCompressor).csv"
ANALOGUE = ["TP2", "TP3", "Reservoirs", "Motor_current", "Oil_temperature"]
BUCKET = "30min"
MIN_SAMPLES = 100          # a bucket needs this many samples to be judged


def frozen_buckets(df):
    """Buckets where every analogue channel holds a single value.

    One channel stuck is a sensor fault. All five stuck at once, while the digital
    channels keep toggling, is the acquisition.
    """
    g = df[ANALOGUE].groupby(pd.Grouper(freq=BUCKET))
    return (g.nunique().max(axis=1) <= 1) & (g.size() > MIN_SAMPLES)


def mask_for(df, frozen):
    """Row-level boolean: True where the sample falls in a frozen bucket."""
    bad = set(frozen[frozen].index)
    return pd.Series(df.index.floor(BUCKET), index=df.index).isin(bad)


def main():
    df = pd.read_csv(CSV, parse_dates=["timestamp"]).set_index("timestamp")
    frozen = frozen_buckets(df)
    m = mask_for(df, frozen)
    print(f"frozen buckets: {frozen.sum()} of {len(frozen)} "
          f"({frozen.sum() * 0.5 / 24:.2f} days, {m.mean():.2%} of samples)\n")

    runs = (frozen != frozen.shift()).cumsum()[frozen]
    print(f"{'block':<34}{'hours':>7}{'DV period':>11}   frozen values")
    for _, idx in frozen[frozen].groupby(runs).groups.items():
        a, b = min(idx), max(idx) + pd.Timedelta(BUCKET)
        seg = df.loc[a:b]
        d = seg.DV_eletric
        ch = (d != d.shift()).cumsum()
        r = d.groupby(ch).agg(v="first", n="size")
        on = r[r.v > 0.5].n.median() * 10 if (r.v > 0.5).any() else float("nan")
        off = r[r.v < 0.5].n.median() * 10 if (r.v < 0.5).any() else float("nan")
        vals = "/".join(f"{seg[c].iloc[0]:g}" for c in ("TP3", "Motor_current"))
        print(f"{a:%d %b %H:%M} to {b:%d %b %H:%M}   {(b-a).total_seconds()/3600:6.1f}"
              f"  {on:4.0f}s/{off:<4.0f}s   {vals}")

    print("\nWhat the freeze does to the cycle indicator, per day:")
    for col, lab in ((~m, "masked"), (slice(None), "raw")):
        d = df[col] if lab == "masked" else df
        load = d.DV_eletric > 0.5
        cyc = load & ~load.shift(1, fill_value=False)
        by = pd.DataFrame({"h": d.groupby(d.index.date).size() * 10 / 3600,
                           "c": cyc.groupby(d.index.date).sum(),
                           "duty": load.groupby(d.index.date).mean()})
        by = by[by.h > 6]
        by["cph"] = by.c / by.h
        top = by.nlargest(3, "cph")
        print(f"  {lab:<7} median {by.cph.median():.2f} cycles/h, duty "
              f"{by.duty.median():.1%};  top 3: "
              + ", ".join(f"{d:%d %b} {r.cph:.1f}/h" for d, r in top.iterrows()))
    print("\nMasked, the top day of the series is 15 July, which IS a reported "
          "failure.\nRaw, the top days are the three freezes.")


if __name__ == "__main__":
    main()
